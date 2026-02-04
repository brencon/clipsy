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
