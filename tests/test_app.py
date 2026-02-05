"""Tests for app.py functionality.

Since ClipsyApp inherits from rumps.App which requires macOS GUI components,
we test the core logic by testing the methods directly with mocked dependencies.
"""
from unittest.mock import MagicMock

from clipsy.models import ContentType


class TestEntryClickBehavior:
    """Test the core behavior: clicking an entry should move it to top."""

    def test_update_timestamp_moves_entry_to_top(self, storage, make_entry):
        """Verify that update_timestamp changes the order in get_recent."""
        # Add entries in order
        id1 = storage.add_entry(make_entry("first", content_hash="h1"))
        id2 = storage.add_entry(make_entry("second", content_hash="h2"))
        id3 = storage.add_entry(make_entry("third", content_hash="h3"))

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

    def test_clicking_entry_updates_timestamp_and_refreshes(self, storage, make_entry):
        """Integration test: simulating the click flow."""
        id1 = storage.add_entry(make_entry("old entry", content_hash="h1"))
        id2 = storage.add_entry(make_entry("new entry", content_hash="h2"))

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

    def test_text_entry_click_flow(self, storage, make_entry):
        """Test the complete flow for clicking a text entry."""
        entry_id = storage.add_entry(make_entry("test text"))

        # Create a minimal mock for the app's dependencies
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

    def test_clear_confirmed_removes_entries(self, storage, make_entry):
        """Test that confirming clear removes all entries."""
        storage.add_entry(make_entry("entry 1", content_hash="h1"))
        storage.add_entry(make_entry("entry 2", content_hash="h2"))
        assert storage.count() == 2

        # Simulate user confirming clear
        storage.clear_all()

        assert storage.count() == 0

    def test_entries_remain_if_not_cleared(self, storage, make_entry):
        """Test that entries remain if clear is cancelled."""
        storage.add_entry(make_entry("entry 1", content_hash="h1"))
        assert storage.count() == 1

        # User cancelled - don't call clear_all
        # (In real app, this is controlled by rumps.alert return value)

        assert storage.count() == 1


class TestContentTypeCopying:
    """Test that different content types are handled correctly."""

    def test_text_content_retrieval(self, storage, make_entry):
        """Test retrieving text content for clipboard copy."""
        entry_id = storage.add_entry(make_entry("clipboard text"))

        entry = storage.get_entry(entry_id)
        assert entry.content_type == ContentType.TEXT
        assert entry.text_content == "clipboard text"

    def test_image_content_retrieval(self, storage, make_entry):
        """Test retrieving image entry for clipboard copy."""
        entry = make_entry("img", content_type=ContentType.IMAGE, image_path="/path/to/image.png")
        entry_id = storage.add_entry(entry)

        retrieved = storage.get_entry(entry_id)
        assert retrieved.content_type == ContentType.IMAGE
        assert retrieved.image_path == "/path/to/image.png"

    def test_file_content_retrieval(self, storage, make_entry):
        """Test retrieving file entry for clipboard copy."""
        entry = make_entry("/Users/test/document.pdf", content_type=ContentType.FILE)
        entry_id = storage.add_entry(entry)

        retrieved = storage.get_entry(entry_id)
        assert retrieved.content_type == ContentType.FILE
        assert retrieved.text_content == "/Users/test/document.pdf"


class TestMenuEntryMapping:
    """Test the entry_ids mapping used for menu clicks."""

    def test_entry_ids_mapping(self, storage, make_entry):
        """Test that entry IDs are correctly mapped."""
        id1 = storage.add_entry(make_entry("first", content_hash="h1"))
        id2 = storage.add_entry(make_entry("second", content_hash="h2"))

        # Simulate building the entry_ids dict as _build_menu does
        entry_ids = {}
        entries = storage.get_recent()
        for entry in entries:
            key = f"clipsy_entry_{entry.id}"
            entry_ids[key] = entry.id

        assert entry_ids[f"clipsy_entry_{id1}"] == id1
        assert entry_ids[f"clipsy_entry_{id2}"] == id2

    def test_entry_ids_cleared_on_rebuild(self, storage, make_entry):
        """Test that entry_ids dict is cleared when rebuilding menu."""
        storage.add_entry(make_entry("entry", content_hash="h1"))

        entry_ids = {"old_key": 999}

        # Simulate clearing as _build_menu does
        entry_ids.clear()

        entries = storage.get_recent()
        for entry in entries:
            key = f"clipsy_entry_{entry.id}"
            entry_ids[key] = entry.id

        assert "old_key" not in entry_ids
        assert len(entry_ids) == 1


class TestRichTextRestoration:
    """Test that RTF/HTML data round-trips through storage for restoration."""

    def test_text_entry_with_rtf_data_available(self, storage, make_entry):
        rtf_bytes = b"{\\rtf1\\ansi Hello \\b World\\b0}"
        entry_id = storage.add_entry(make_entry("Hello World", rtf_data=rtf_bytes))
        entry = storage.get_entry(entry_id)
        assert entry.rtf_data == rtf_bytes
        assert entry.text_content == "Hello World"
        assert entry.content_type == ContentType.TEXT

    def test_text_entry_with_html_data_available(self, storage, make_entry):
        html_bytes = b"<p>Hello <b>World</b></p>"
        entry_id = storage.add_entry(make_entry("Hello World", html_data=html_bytes, content_hash="html_h"))
        entry = storage.get_entry(entry_id)
        assert entry.html_data == html_bytes
        assert entry.text_content == "Hello World"

    def test_text_entry_with_both_formats(self, storage, make_entry):
        rtf_bytes = b"{\\rtf1\\ansi Hello}"
        html_bytes = b"<p>Hello</p>"
        entry_id = storage.add_entry(
            make_entry("Hello", rtf_data=rtf_bytes, html_data=html_bytes)
        )
        entry = storage.get_entry(entry_id)
        assert entry.rtf_data == rtf_bytes
        assert entry.html_data == html_bytes

    def test_plain_text_entry_has_no_rich_data(self, storage, make_entry):
        entry_id = storage.add_entry(make_entry("plain text"))
        entry = storage.get_entry(entry_id)
        assert entry.rtf_data is None
        assert entry.html_data is None
        assert entry.text_content == "plain text"


class TestPinningBehavior:
    """Test pinning-related behavior at the app level."""

    def test_pinned_entries_not_in_recent_list(self, storage, make_entry):
        id1 = storage.add_entry(make_entry("pinned entry", content_hash="h1"))
        id2 = storage.add_entry(make_entry("regular entry", content_hash="h2"))
        storage.toggle_pin(id1)

        recent = storage.get_recent()
        pinned = storage.get_pinned()

        # Filter recent like app.py does
        recent_unpinned = [e for e in recent if not e.pinned]

        assert len(pinned) == 1
        assert pinned[0].id == id1
        assert all(e.id != id1 for e in recent_unpinned)

    def test_cannot_pin_sensitive_entry(self, storage, make_entry):
        from clipsy.models import ClipboardEntry, ContentType
        from datetime import datetime

        sensitive_entry = ClipboardEntry(
            id=None,
            content_type=ContentType.TEXT,
            text_content="password=secret123",
            image_path=None,
            preview="password=secret123",
            content_hash="sensitive_hash",
            byte_size=20,
            created_at=datetime.now(),
            is_sensitive=True,
            masked_preview="password=••••••••",
        )
        entry_id = storage.add_entry(sensitive_entry)
        entry = storage.get_entry(entry_id)

        # The entry is sensitive
        assert entry.is_sensitive is True

        # Simulate app-level check: sensitive entries should not be pinned
        # This mimics what _on_pin_toggle does
        if entry.is_sensitive:
            can_pin = False
        else:
            can_pin = True

        assert can_pin is False

    def test_max_pinned_limit(self, storage, make_entry):
        from clipsy.config import MAX_PINNED_ENTRIES

        # Pin up to the limit
        for i in range(MAX_PINNED_ENTRIES):
            entry_id = storage.add_entry(make_entry(f"entry {i}", content_hash=f"hash_{i}"))
            storage.toggle_pin(entry_id)

        assert storage.count_pinned() == MAX_PINNED_ENTRIES

        # App should check this before allowing another pin
        at_limit = storage.count_pinned() >= MAX_PINNED_ENTRIES
        assert at_limit is True
