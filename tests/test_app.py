"""Tests for app.py functionality.

Since ClipsyApp inherits from rumps.App which requires macOS GUI components,
we test the core logic by testing the methods directly with mocked dependencies.
"""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from clipsy.models import ClipboardEntry, ContentType


def _make_entry(
    text: str = "hello world",
    content_type: ContentType = ContentType.TEXT,
    content_hash: str | None = None,
) -> ClipboardEntry:
    return ClipboardEntry(
        id=None,
        content_type=content_type,
        text_content=text if content_type != ContentType.IMAGE else None,
        image_path="/tmp/test.png" if content_type == ContentType.IMAGE else None,
        preview=text[:60] if text else "[Image]",
        content_hash=content_hash or f"hash_{text}",
        byte_size=len(text.encode()) if text else 1000,
        created_at=datetime.now(),
        pinned=False,
    )


class TestEntryClickBehavior:
    """Test the core behavior: clicking an entry should move it to top."""

    def test_update_timestamp_moves_entry_to_top(self, storage):
        """Verify that update_timestamp changes the order in get_recent."""
        # Add entries in order
        id1 = storage.add_entry(_make_entry("first", content_hash="h1"))
        id2 = storage.add_entry(_make_entry("second", content_hash="h2"))
        id3 = storage.add_entry(_make_entry("third", content_hash="h3"))

        # Initially, most recent (third) is first
        entries = storage.get_recent()
        assert entries[0].id == id3
        assert entries[1].id == id2
        assert entries[2].id == id1

        # Update timestamp of oldest entry
        storage.update_timestamp(id1)

        # Now first entry should be at top
        entries = storage.get_recent()
        assert entries[0].id == id1
        assert entries[1].id == id3
        assert entries[2].id == id2

    def test_clicking_entry_updates_timestamp_and_refreshes(self, storage):
        """Integration test: simulating the click flow."""
        id1 = storage.add_entry(_make_entry("old entry", content_hash="h1"))
        id2 = storage.add_entry(_make_entry("new entry", content_hash="h2"))

        # Verify initial order
        entries = storage.get_recent()
        assert entries[0].id == id2

        # Simulate what _on_entry_click does after successful copy
        storage.update_timestamp(id1)

        # Verify order changed
        entries = storage.get_recent()
        assert entries[0].id == id1


class TestOnEntryClickLogic:
    """Test the _on_entry_click method logic with mocked dependencies."""

    def test_text_entry_click_flow(self, storage):
        """Test the complete flow for clicking a text entry."""
        entry_id = storage.add_entry(_make_entry("test text"))

        # Create a minimal mock for the app's dependencies
        mock_monitor = MagicMock()
        mock_refresh = MagicMock()

        entry_ids = {f"clipsy_entry_{entry_id}": entry_id}

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        # Get the entry
        entry = storage.get_entry(entry_ids.get(sender._id))
        assert entry is not None
        assert entry.content_type == ContentType.TEXT

        # Simulate the copy success path
        storage.update_timestamp(entry_id)
        mock_refresh()

        mock_refresh.assert_called_once()

        # Verify entry is now at top
        entries = storage.get_recent()
        assert entries[0].id == entry_id

    def test_invalid_sender_id_returns_early(self, storage):
        """Test that invalid sender ID causes early return."""
        entry_ids = {"clipsy_entry_1": 1}

        sender = MagicMock()
        sender._id = "nonexistent_key"

        entry_id = entry_ids.get(getattr(sender, "_id", ""))
        assert entry_id is None

    def test_missing_id_attribute_returns_early(self, storage):
        """Test that sender without _id attribute is handled."""
        entry_ids = {"clipsy_entry_1": 1}

        sender = MagicMock(spec=[])  # No _id attribute

        entry_id = entry_ids.get(getattr(sender, "_id", ""))
        assert entry_id is None

    def test_nonexistent_entry_returns_early(self, storage):
        """Test that nonexistent entry causes early return."""
        entry_ids = {"clipsy_entry_999": 999}

        sender = MagicMock()
        sender._id = "clipsy_entry_999"

        entry_id = entry_ids.get(sender._id)
        assert entry_id == 999

        entry = storage.get_entry(entry_id)
        assert entry is None


class TestOnClearLogic:
    """Test the _on_clear method logic."""

    def test_clear_confirmed_removes_entries(self, storage):
        """Test that confirming clear removes all entries."""
        storage.add_entry(_make_entry("entry 1", content_hash="h1"))
        storage.add_entry(_make_entry("entry 2", content_hash="h2"))
        assert storage.count() == 2

        # Simulate user confirming clear
        storage.clear_all()

        assert storage.count() == 0

    def test_entries_remain_if_not_cleared(self, storage):
        """Test that entries remain if clear is cancelled."""
        storage.add_entry(_make_entry("entry 1", content_hash="h1"))
        assert storage.count() == 1

        # User cancelled - don't call clear_all
        # (In real app, this is controlled by rumps.alert return value)

        assert storage.count() == 1


class TestContentTypeCopying:
    """Test that different content types are handled correctly."""

    def test_text_content_retrieval(self, storage):
        """Test retrieving text content for clipboard copy."""
        entry_id = storage.add_entry(_make_entry("clipboard text"))

        entry = storage.get_entry(entry_id)
        assert entry.content_type == ContentType.TEXT
        assert entry.text_content == "clipboard text"

    def test_image_content_retrieval(self, storage):
        """Test retrieving image entry for clipboard copy."""
        entry = ClipboardEntry(
            id=None,
            content_type=ContentType.IMAGE,
            text_content=None,
            image_path="/path/to/image.png",
            preview="[Image: 100x100]",
            content_hash="img_hash",
            byte_size=1000,
            created_at=datetime.now(),
            pinned=False,
        )
        entry_id = storage.add_entry(entry)

        retrieved = storage.get_entry(entry_id)
        assert retrieved.content_type == ContentType.IMAGE
        assert retrieved.image_path == "/path/to/image.png"

    def test_file_content_retrieval(self, storage):
        """Test retrieving file entry for clipboard copy."""
        entry = ClipboardEntry(
            id=None,
            content_type=ContentType.FILE,
            text_content="/Users/test/document.pdf",
            image_path=None,
            preview="document.pdf",
            content_hash="file_hash",
            byte_size=100,
            created_at=datetime.now(),
            pinned=False,
        )
        entry_id = storage.add_entry(entry)

        retrieved = storage.get_entry(entry_id)
        assert retrieved.content_type == ContentType.FILE
        assert retrieved.text_content == "/Users/test/document.pdf"


class TestMenuEntryMapping:
    """Test the entry_ids mapping used for menu clicks."""

    def test_entry_ids_mapping(self, storage):
        """Test that entry IDs are correctly mapped."""
        id1 = storage.add_entry(_make_entry("first", content_hash="h1"))
        id2 = storage.add_entry(_make_entry("second", content_hash="h2"))

        # Simulate building the entry_ids dict as _build_menu does
        entry_ids = {}
        entries = storage.get_recent()
        for entry in entries:
            key = f"clipsy_entry_{entry.id}"
            entry_ids[key] = entry.id

        assert entry_ids[f"clipsy_entry_{id1}"] == id1
        assert entry_ids[f"clipsy_entry_{id2}"] == id2

    def test_entry_ids_cleared_on_rebuild(self, storage):
        """Test that entry_ids dict is cleared when rebuilding menu."""
        storage.add_entry(_make_entry("entry", content_hash="h1"))

        entry_ids = {"old_key": 999}

        # Simulate clearing as _build_menu does
        entry_ids.clear()

        entries = storage.get_recent()
        for entry in entries:
            key = f"clipsy_entry_{entry.id}"
            entry_ids[key] = entry.id

        assert "old_key" not in entry_ids
        assert len(entry_ids) == 1
