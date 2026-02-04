from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class ContentType(str, Enum):
    TEXT = "text"
    IMAGE = "image"
    FILE = "file"


@dataclass
class ClipboardEntry:
    id: int | None
    content_type: ContentType
    text_content: str | None
    image_path: str | None
    preview: str
    content_hash: str
    byte_size: int
    created_at: datetime
    pinned: bool = False
    source_app: str | None = None
    thumbnail_path: str | None = None
