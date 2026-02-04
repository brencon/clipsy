from datetime import datetime

import pytest

from clipsy.models import ClipboardEntry, ContentType
from clipsy.storage import StorageManager

# Sentinel to distinguish "not provided" from "explicitly None"
_UNSET = object()


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
        thumbnail_path: str | None = _UNSET,
    ) -> ClipboardEntry:
        if content_type == ContentType.IMAGE:
            # Use default only if not provided; explicit None stays None
            actual_thumbnail = "/tmp/test_thumb.png" if thumbnail_path is _UNSET else thumbnail_path
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
                thumbnail_path=actual_thumbnail,
            )
        # For TEXT entries, thumbnail_path should be None unless explicitly provided
        text_thumbnail = None if thumbnail_path is _UNSET else thumbnail_path
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
            thumbnail_path=text_thumbnail,
        )

    return _make_entry
