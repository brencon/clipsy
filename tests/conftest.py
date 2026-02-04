from datetime import datetime

import pytest

from clipsy.models import ClipboardEntry, ContentType
from clipsy.storage import StorageManager


@pytest.fixture
def storage():
    mgr = StorageManager(db_path=":memory:")
    yield mgr
    mgr.close()


@pytest.fixture
def make_entry():
    """Factory fixture to create ClipboardEntry instances for testing."""

    def _make_entry(
        text: str = "hello world",
        content_type: ContentType = ContentType.TEXT,
        content_hash: str | None = None,
        pinned: bool = False,
        image_path: str | None = None,
    ) -> ClipboardEntry:
        if content_type == ContentType.IMAGE:
            return ClipboardEntry(
                id=None,
                content_type=content_type,
                text_content=None,
                image_path=image_path or "/tmp/test.png",
                preview="[Image: 100x100]",
                content_hash=content_hash or f"hash_{text}",
                byte_size=1000,
                created_at=datetime.now(),
                pinned=pinned,
            )
        return ClipboardEntry(
            id=None,
            content_type=content_type,
            text_content=text,
            image_path=None,
            preview=text[:60] if text else "",
            content_hash=content_hash or f"hash_{text}",
            byte_size=len(text.encode()) if text else 0,
            created_at=datetime.now(),
            pinned=pinned,
        )

    return _make_entry
