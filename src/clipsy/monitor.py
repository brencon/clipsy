import logging
from collections.abc import Callable
from pathlib import Path

from AppKit import NSPasteboard, NSPasteboardTypePNG, NSPasteboardTypeTIFF, NSPasteboardTypeString, NSFilenamesPboardType

from clipsy.config import IMAGE_DIR, MAX_IMAGE_SIZE, MAX_TEXT_SIZE, PREVIEW_LENGTH
from clipsy.models import ClipboardEntry, ContentType
from clipsy.storage import StorageManager
from clipsy.utils import compute_hash, ensure_dirs, get_image_dimensions, truncate_text

logger = logging.getLogger(__name__)


class ClipboardMonitor:
    def __init__(self, storage: StorageManager, on_change: Callable[[], None] | None = None):
        self._storage = storage
        self._on_change = on_change
        self._pasteboard = NSPasteboard.generalPasteboard()
        self._last_change_count = self._pasteboard.changeCount()
        ensure_dirs()

    def check_clipboard(self) -> bool:
        current_count = self._pasteboard.changeCount()
        if current_count == self._last_change_count:
            return False

        self._last_change_count = current_count

        try:
            entry = self._read_clipboard()
            if entry is None:
                return False

            existing = self._storage.find_by_hash(entry.content_hash)
            if existing:
                self._storage.update_timestamp(existing.id)
            else:
                self._storage.add_entry(entry)
                self._storage.purge_old()

            if self._on_change:
                self._on_change()
            return True
        except Exception:
            logger.exception("Error reading clipboard")
            return False

    def sync_change_count(self) -> None:
        self._last_change_count = self._pasteboard.changeCount()

    def _read_clipboard(self) -> ClipboardEntry | None:
        from datetime import datetime

        types = self._pasteboard.types()
        if types is None:
            return None

        if NSPasteboardTypeString in types:
            text = self._pasteboard.stringForType_(NSPasteboardTypeString)
            if text:
                text_bytes = text.encode("utf-8")
                if len(text_bytes) <= MAX_TEXT_SIZE:
                    content_hash = compute_hash(text_bytes)
                    return ClipboardEntry(
                        id=None,
                        content_type=ContentType.TEXT,
                        text_content=text,
                        image_path=None,
                        preview=truncate_text(text, PREVIEW_LENGTH),
                        content_hash=content_hash,
                        byte_size=len(text_bytes),
                        created_at=datetime.now(),
                    )

        for img_type in (NSPasteboardTypePNG, NSPasteboardTypeTIFF):
            if img_type in types:
                data = self._pasteboard.dataForType_(img_type)
                if data is None:
                    continue
                img_bytes = bytes(data)
                if len(img_bytes) > MAX_IMAGE_SIZE:
                    logger.warning("Image too large (%d bytes), skipping", len(img_bytes))
                    return None
                content_hash = compute_hash(img_bytes)
                is_png = img_type == NSPasteboardTypePNG
                image_path = self._save_image(img_bytes, content_hash, is_png)
                width, height = get_image_dimensions(img_bytes)
                preview = f"[Image: {width}x{height}]" if width > 0 else "[Image]"
                return ClipboardEntry(
                    id=None,
                    content_type=ContentType.IMAGE,
                    text_content=None,
                    image_path=str(image_path),
                    preview=preview,
                    content_hash=content_hash,
                    byte_size=len(img_bytes),
                    created_at=datetime.now(),
                )

        if NSFilenamesPboardType in types:
            filenames = self._pasteboard.propertyListForType_(NSFilenamesPboardType)
            if filenames:
                file_list = list(filenames)
                text = "\n".join(file_list)
                content_hash = compute_hash(text)
                if len(file_list) == 1:
                    preview = truncate_text(Path(file_list[0]).name, PREVIEW_LENGTH)
                else:
                    preview = truncate_text(f"{len(file_list)} files: {Path(file_list[0]).name}, ...", PREVIEW_LENGTH)
                return ClipboardEntry(
                    id=None,
                    content_type=ContentType.FILE,
                    text_content=text,
                    image_path=None,
                    preview=preview,
                    content_hash=content_hash,
                    byte_size=len(text.encode("utf-8")),
                    created_at=datetime.now(),
                )

        return None

    def _save_image(self, img_bytes: bytes, content_hash: str, is_png: bool) -> Path:
        ext = ".png" if is_png else ".tiff"
        filename = content_hash[:12] + ext
        path = IMAGE_DIR / filename
        if not path.exists():
            path.write_bytes(img_bytes)
        return path
