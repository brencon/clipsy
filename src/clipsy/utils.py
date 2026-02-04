import hashlib
import struct
from pathlib import Path

from clipsy.config import DATA_DIR, IMAGE_DIR


def compute_hash(data: str | bytes) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def truncate_text(text: str, max_len: int) -> str:
    single_line = " ".join(text.split())
    if len(single_line) <= max_len:
        return single_line
    return single_line[: max_len - 3] + "..."


def ensure_dirs() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)


def get_image_dimensions(png_bytes: bytes) -> tuple[int, int]:
    if len(png_bytes) < 24 or png_bytes[:8] != b"\x89PNG\r\n\x1a\n":
        return (0, 0)
    width = struct.unpack(">I", png_bytes[16:20])[0]
    height = struct.unpack(">I", png_bytes[20:24])[0]
    return (width, height)


def create_thumbnail(image_path: str, thumb_path: str, size: tuple[int, int] = (32, 32)) -> bool:
    """Create a thumbnail from an image file using native NSImage.

    Args:
        image_path: Path to the source image
        thumb_path: Path to save the thumbnail
        size: Target size in pixels (width, height)

    Returns:
        True if thumbnail was created successfully, False otherwise
    """
    try:
        from AppKit import NSBitmapImageRep, NSGraphicsContext, NSImage

        original = NSImage.alloc().initWithContentsOfFile_(image_path)
        if not original:
            return False

        resized = NSImage.alloc().initWithSize_(size)
        resized.lockFocus()
        NSGraphicsContext.currentContext().setImageInterpolation_(3)  # High quality
        original.drawInRect_(((0, 0), size))
        resized.unlockFocus()

        tiff_data = resized.TIFFRepresentation()
        if not tiff_data:
            return False

        bitmap_rep = NSBitmapImageRep.imageRepWithData_(tiff_data)
        if not bitmap_rep:
            return False

        png_data = bitmap_rep.representationUsingType_properties_(4, None)  # 4 = PNG
        if not png_data:
            return False

        return bool(png_data.writeToFile_atomically_(thumb_path, True))
    except Exception:
        return False
