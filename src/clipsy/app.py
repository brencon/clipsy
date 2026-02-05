import logging
import webbrowser

import rumps

from clipsy import __version__
from clipsy.config import DB_PATH, IMAGE_DIR, MENU_DISPLAY_COUNT, POLL_INTERVAL, REDACT_SENSITIVE, THUMBNAIL_SIZE
from clipsy.models import ClipboardEntry, ContentType
from clipsy.monitor import ClipboardMonitor
from clipsy.storage import StorageManager
from clipsy.utils import create_thumbnail, ensure_dirs

logger = logging.getLogger(__name__)

ENTRY_KEY_PREFIX = "clipsy_entry_"


class ClipsyApp(rumps.App):
    def __init__(self):
        super().__init__("Clipsy", title="✂️", quit_button=None)
        ensure_dirs()
        self._storage = StorageManager(DB_PATH)
        self._monitor = ClipboardMonitor(self._storage, on_change=self._refresh_menu)
        self._entry_ids: dict[str, int] = {}
        self._build_menu()

    def _build_menu(self) -> None:
        self.menu.clear()
        self.menu = [
            rumps.MenuItem(f"Clipsy v{__version__} - Clipboard History", callback=None),
            None,  # separator
            rumps.MenuItem("Search...", callback=self._on_search),
            None,  # separator
        ]

        entries = self._storage.get_recent(limit=MENU_DISPLAY_COUNT)
        self._entry_ids.clear()

        if not entries:
            self.menu.add(rumps.MenuItem("(No clipboard history)", callback=None))
        else:
            for entry in entries:
                key = f"{ENTRY_KEY_PREFIX}{entry.id}"
                self._entry_ids[key] = entry.id
                display_text = self._get_display_preview(entry)
                if entry.content_type == ContentType.IMAGE:
                    thumb_path = self._ensure_thumbnail(entry)
                    if thumb_path:
                        item = rumps.MenuItem(
                            display_text,
                            callback=self._on_entry_click,
                            icon=thumb_path,
                            dimensions=(32, 32),
                            template=False,
                        )
                    else:
                        item = rumps.MenuItem(display_text, callback=self._on_entry_click)
                else:
                    item = rumps.MenuItem(display_text, callback=self._on_entry_click)
                item._id = key
                self.menu.add(item)

        self.menu.add(None)  # separator
        self.menu.add(rumps.MenuItem("Clear History", callback=self._on_clear))
        self.menu.add(None)  # separator
        self.menu.add(rumps.MenuItem("Support Clipsy", callback=self._on_support))
        self.menu.add(None)  # separator
        self.menu.add(rumps.MenuItem("Quit Clipsy", callback=self._on_quit))

    def _get_display_preview(self, entry: ClipboardEntry) -> str:
        """Get the display preview for an entry, masking sensitive data if enabled."""
        if REDACT_SENSITIVE and entry.is_sensitive and entry.masked_preview:
            return f"🔒 {entry.masked_preview}"
        return entry.preview

    def _ensure_thumbnail(self, entry: ClipboardEntry) -> str | None:
        """Ensure a thumbnail exists for an image entry, generating if needed."""
        if entry.thumbnail_path:
            return entry.thumbnail_path

        if not entry.image_path:
            return None

        # Generate thumbnail for legacy entries
        from pathlib import Path

        image_path = Path(entry.image_path)
        if not image_path.exists():
            return None

        thumb_filename = image_path.stem + "_thumb.png"
        thumb_path = IMAGE_DIR / thumb_filename

        if thumb_path.exists() or create_thumbnail(str(image_path), str(thumb_path), THUMBNAIL_SIZE):
            self._storage.update_thumbnail_path(entry.id, str(thumb_path))
            return str(thumb_path)

        return None

    def _refresh_menu(self) -> None:
        self._build_menu()

    @rumps.timer(POLL_INTERVAL)
    def _poll_clipboard(self, _sender) -> None:
        self._monitor.check_clipboard()

    def _on_entry_click(self, sender) -> None:
        entry_id = self._entry_ids.get(getattr(sender, "_id", ""))
        if entry_id is None:
            return

        entry = self._storage.get_entry(entry_id)
        if entry is None:
            return

        try:
            from AppKit import NSPasteboard, NSPasteboardTypePNG, NSPasteboardTypeString

            pb = NSPasteboard.generalPasteboard()

            copied = False

            if entry.content_type == ContentType.TEXT and entry.text_content:
                pb.clearContents()
                pb.setString_forType_(entry.text_content, NSPasteboardTypeString)
                self._monitor.sync_change_count()
                copied = True

            elif entry.content_type == ContentType.IMAGE and entry.image_path:
                from Foundation import NSData
                img_data = NSData.dataWithContentsOfFile_(entry.image_path)
                if img_data:
                    pb.clearContents()
                    pb.setData_forType_(img_data, NSPasteboardTypePNG)
                    self._monitor.sync_change_count()
                    copied = True

            elif entry.content_type == ContentType.FILE and entry.text_content:
                pb.clearContents()
                pb.setString_forType_(entry.text_content, NSPasteboardTypeString)
                self._monitor.sync_change_count()
                copied = True

            if copied:
                self._storage.update_timestamp(entry_id)
                self._refresh_menu()
                rumps.notification("Clipsy", "", "Copied to clipboard", sound=False)
        except Exception:
            logger.exception("Error copying entry to clipboard")

    def _on_search(self, _sender) -> None:
        response = rumps.Window(
            message="Search clipboard history:",
            title="Clipsy Search",
            default_text="",
            ok="Search",
            cancel="Cancel",
            dimensions=(300, 24),
        ).run()

        if response.clicked and response.text.strip():
            query = response.text.strip()
            results = self._storage.search(query, limit=MENU_DISPLAY_COUNT)

            if not results:
                rumps.alert("Clipsy Search", f'No results for "{query}"')
                return

            self.menu.clear()
            self._entry_ids.clear()
            self.menu = [
                rumps.MenuItem(f'Search: "{query}" ({len(results)} results)', callback=None),
                None,
                rumps.MenuItem("Show All", callback=lambda _: self._refresh_menu()),
                None,
            ]

            for entry in results:
                key = f"{ENTRY_KEY_PREFIX}{entry.id}"
                self._entry_ids[key] = entry.id
                display_text = self._get_display_preview(entry)
                if entry.content_type == ContentType.IMAGE:
                    thumb_path = self._ensure_thumbnail(entry)
                    if thumb_path:
                        item = rumps.MenuItem(
                            display_text,
                            callback=self._on_entry_click,
                            icon=thumb_path,
                            dimensions=(32, 32),
                            template=False,
                        )
                    else:
                        item = rumps.MenuItem(display_text, callback=self._on_entry_click)
                else:
                    item = rumps.MenuItem(display_text, callback=self._on_entry_click)
                item._id = key
                self.menu.add(item)

            self.menu.add(None)
            self.menu.add(rumps.MenuItem("Quit Clipsy", callback=self._on_quit))

    def _on_clear(self, _sender) -> None:
        if rumps.alert("Clipsy", "Clear all clipboard history?", ok="Clear", cancel="Cancel"):
            self._storage.clear_all()
            self._refresh_menu()

    def _on_support(self, _sender) -> None:
        webbrowser.open("https://github.com/sponsors/brencon")

    def _on_quit(self, _sender) -> None:
        self._storage.close()
        rumps.quit_application()
