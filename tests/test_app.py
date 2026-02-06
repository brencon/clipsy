"""Tests for app.py functionality.

Since ClipsyApp inherits from rumps.App which requires macOS GUI components,
we test the core logic by testing the methods directly with mocked dependencies.
"""
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from clipsy.models import ClipboardEntry, ContentType


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

    def test_clear_pinned_clears_all(self, storage, make_entry):
        id1 = storage.add_entry(make_entry("entry 1", content_hash="h1"))
        id2 = storage.add_entry(make_entry("entry 2", content_hash="h2"))
        storage.toggle_pin(id1)
        storage.toggle_pin(id2)

        assert storage.count_pinned() == 2

        storage.clear_pinned()

        assert storage.count_pinned() == 0
        assert storage.get_pinned() == []


@pytest.fixture
def clipsy_app(storage):
    """Create a ClipsyApp-like object for testing methods."""
    from clipsy.app import ClipsyApp

    # Create a minimal mock object that has the methods we want to test
    app = MagicMock(spec=ClipsyApp)

    # Bind the real methods to our mock
    app._storage = storage
    app._monitor = MagicMock()
    app._entry_ids = {}
    app.menu = MagicMock()

    # Bind real methods
    app._get_display_preview = lambda entry: ClipsyApp._get_display_preview(app, entry)
    app._ensure_thumbnail = lambda entry: ClipsyApp._ensure_thumbnail(app, entry)
    app._refresh_menu = lambda: ClipsyApp._refresh_menu(app)
    app._poll_clipboard = lambda sender: ClipsyApp._poll_clipboard(app, sender)
    app._on_clear_pinned = lambda sender: ClipsyApp._on_clear_pinned(app, sender)
    app._on_support = lambda sender: ClipsyApp._on_support(app, sender)
    app._on_quit = lambda sender: ClipsyApp._on_quit(app, sender)
    app._on_clear = lambda sender: ClipsyApp._on_clear(app, sender)
    app._on_pin_toggle = lambda entry: ClipsyApp._on_pin_toggle(app, entry)
    app._on_entry_click = lambda sender: ClipsyApp._on_entry_click(app, sender)
    app._on_search = lambda sender: ClipsyApp._on_search(app, sender)
    app._compute_entry_spec = lambda entry: ClipsyApp._compute_entry_spec(app, entry)
    app._compute_menu_specs = lambda: ClipsyApp._compute_menu_specs(app)
    app._compute_search_results_specs = lambda q, r: ClipsyApp._compute_search_results_specs(app, q, r)
    app._init_app = lambda: ClipsyApp._init_app(app)
    app._build_menu = MagicMock()

    return app


class TestClipsyAppInit:
    """Test ClipsyApp initialization."""

    def test_app_initializes(self, clipsy_app):
        """Test that app initializes with expected attributes."""
        assert clipsy_app._storage is not None
        assert clipsy_app._entry_ids == {}
        assert clipsy_app._monitor is not None


class TestGetDisplayPreview:
    """Test _get_display_preview method."""

    def test_normal_entry_shows_preview(self, clipsy_app):
        """Test that normal entries show their preview."""
        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.TEXT,
            text_content="test",
            image_path=None,
            preview="test preview",
            content_hash="h1",
            byte_size=10,
            created_at=datetime.now(),
            is_sensitive=False,
        )
        result = clipsy_app._get_display_preview(entry)
        assert result == "test preview"

    @patch("clipsy.app.REDACT_SENSITIVE", True)
    def test_sensitive_entry_shows_masked_preview(self, clipsy_app):
        """Test that sensitive entries show masked preview when redaction enabled."""
        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.TEXT,
            text_content="password=secret",
            image_path=None,
            preview="password=secret",
            content_hash="h1",
            byte_size=15,
            created_at=datetime.now(),
            is_sensitive=True,
            masked_preview="password=••••••",
        )
        result = clipsy_app._get_display_preview(entry)
        assert result == "🔒 password=••••••"

    @patch("clipsy.app.REDACT_SENSITIVE", False)
    def test_sensitive_entry_shows_plain_when_redaction_disabled(self, clipsy_app):
        """Test that sensitive entries show plain preview when redaction disabled."""
        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.TEXT,
            text_content="password=secret",
            image_path=None,
            preview="password=secret",
            content_hash="h1",
            byte_size=15,
            created_at=datetime.now(),
            is_sensitive=True,
            masked_preview="password=••••••",
        )
        result = clipsy_app._get_display_preview(entry)
        assert result == "password=secret"


class TestEnsureThumbnail:
    """Test _ensure_thumbnail method."""

    def test_returns_existing_thumbnail_path(self, clipsy_app):
        """Test that existing thumbnail path is returned."""
        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.IMAGE,
            text_content=None,
            image_path="/path/to/image.png",
            preview="🖼️ Image",
            content_hash="h1",
            byte_size=1000,
            created_at=datetime.now(),
            thumbnail_path="/path/to/thumb.png",
        )
        result = clipsy_app._ensure_thumbnail(entry)
        assert result == "/path/to/thumb.png"

    def test_returns_none_for_no_image_path(self, clipsy_app):
        """Test that None is returned when no image path."""
        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.IMAGE,
            text_content=None,
            image_path=None,
            preview="🖼️ Image",
            content_hash="h1",
            byte_size=1000,
            created_at=datetime.now(),
        )
        result = clipsy_app._ensure_thumbnail(entry)
        assert result is None

    def test_returns_none_for_nonexistent_image(self, clipsy_app):
        """Test that None is returned when image file doesn't exist."""
        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.IMAGE,
            text_content=None,
            image_path="/nonexistent/image.png",
            preview="🖼️ Image",
            content_hash="h1",
            byte_size=1000,
            created_at=datetime.now(),
        )
        result = clipsy_app._ensure_thumbnail(entry)
        assert result is None


class TestRefreshMenu:
    """Test _refresh_menu method."""

    def test_refresh_calls_build_menu(self, clipsy_app):
        """Test that refresh calls build menu."""
        clipsy_app._build_menu = MagicMock()
        clipsy_app._refresh_menu()
        clipsy_app._build_menu.assert_called_once()


class TestPollClipboard:
    """Test _poll_clipboard method."""

    def test_poll_calls_monitor(self, clipsy_app):
        """Test that poll calls clipboard monitor."""
        clipsy_app._poll_clipboard(None)
        clipsy_app._monitor.check_clipboard.assert_called_once()


class TestOnClearPinned:
    """Test _on_clear_pinned method."""

    def test_clears_pinned_and_refreshes(self, clipsy_app, make_entry):
        """Test that clear pinned clears storage and refreshes."""
        clipsy_app._build_menu = MagicMock()

        # Add a pinned entry
        entry_id = clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))
        clipsy_app._storage.toggle_pin(entry_id)
        assert clipsy_app._storage.count_pinned() == 1

        clipsy_app._on_clear_pinned(None)

        assert clipsy_app._storage.count_pinned() == 0
        clipsy_app._build_menu.assert_called_once()


class TestOnSupport:
    """Test _on_support method."""

    @patch("clipsy.app.webbrowser.open")
    def test_opens_sponsor_page(self, mock_open, clipsy_app):
        """Test that support opens sponsor page."""
        clipsy_app._on_support(None)
        mock_open.assert_called_once_with("https://github.com/sponsors/brencon")


class TestOnQuit:
    """Test _on_quit method."""

    @patch("clipsy.app.rumps")
    def test_closes_storage_and_quits(self, mock_rumps, clipsy_app):
        """Test that quit closes storage and quits app."""
        clipsy_app._storage.close = MagicMock()
        clipsy_app._on_quit(None)
        clipsy_app._storage.close.assert_called_once()
        mock_rumps.quit_application.assert_called_once()


class TestOnClear:
    """Test _on_clear method."""

    @patch("clipsy.app.rumps")
    def test_clear_confirmed_clears_storage(self, mock_rumps, clipsy_app, make_entry):
        """Test that confirming clear removes entries."""
        clipsy_app._build_menu = MagicMock()
        mock_rumps.alert.return_value = 1  # OK clicked

        clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))
        assert clipsy_app._storage.count() == 1

        clipsy_app._on_clear(None)

        assert clipsy_app._storage.count() == 0
        clipsy_app._build_menu.assert_called_once()

    @patch("clipsy.app.rumps")
    def test_clear_cancelled_keeps_entries(self, mock_rumps, clipsy_app, make_entry):
        """Test that cancelling clear keeps entries."""
        clipsy_app._build_menu = MagicMock()
        mock_rumps.alert.return_value = 0  # Cancel clicked

        clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))
        assert clipsy_app._storage.count() == 1

        clipsy_app._on_clear(None)

        assert clipsy_app._storage.count() == 1
        clipsy_app._build_menu.assert_not_called()


class TestOnPinToggle:
    """Test _on_pin_toggle method."""

    @patch("clipsy.app.rumps")
    def test_unpin_existing_pinned_entry(self, mock_rumps, clipsy_app, make_entry):
        """Test unpinning an already pinned entry."""
        clipsy_app._build_menu = MagicMock()

        entry_id = clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))
        clipsy_app._storage.toggle_pin(entry_id)
        entry = clipsy_app._storage.get_entry(entry_id)

        clipsy_app._on_pin_toggle(entry)

        updated = clipsy_app._storage.get_entry(entry_id)
        assert updated.pinned is False
        mock_rumps.notification.assert_called()
        clipsy_app._build_menu.assert_called_once()

    @patch("clipsy.app.rumps")
    def test_pin_normal_entry(self, mock_rumps, clipsy_app, make_entry):
        """Test pinning a normal entry."""
        clipsy_app._build_menu = MagicMock()

        entry_id = clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))
        entry = clipsy_app._storage.get_entry(entry_id)

        clipsy_app._on_pin_toggle(entry)

        updated = clipsy_app._storage.get_entry(entry_id)
        assert updated.pinned is True
        clipsy_app._build_menu.assert_called_once()

    @patch("clipsy.app.rumps")
    def test_cannot_pin_sensitive_entry(self, mock_rumps, clipsy_app):
        """Test that sensitive entries cannot be pinned."""
        clipsy_app._build_menu = MagicMock()

        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.TEXT,
            text_content="password=secret",
            image_path=None,
            preview="password=secret",
            content_hash="h1",
            byte_size=15,
            created_at=datetime.now(),
            is_sensitive=True,
            pinned=False,
        )

        clipsy_app._on_pin_toggle(entry)

        # Should show notification about sensitive data
        mock_rumps.notification.assert_called()
        call_args = mock_rumps.notification.call_args
        assert "sensitive" in call_args[0][2].lower()
        clipsy_app._build_menu.assert_not_called()

    @patch("clipsy.app.rumps")
    def test_cannot_exceed_max_pinned(self, mock_rumps, clipsy_app, make_entry):
        """Test that pinning is blocked at max limit."""
        from clipsy.config import MAX_PINNED_ENTRIES

        clipsy_app._build_menu = MagicMock()

        # Fill up pinned slots
        for i in range(MAX_PINNED_ENTRIES):
            eid = clipsy_app._storage.add_entry(make_entry(f"entry{i}", content_hash=f"h{i}"))
            clipsy_app._storage.toggle_pin(eid)

        # Try to pin one more
        new_id = clipsy_app._storage.add_entry(make_entry("new", content_hash="hnew"))
        entry = clipsy_app._storage.get_entry(new_id)

        clipsy_app._on_pin_toggle(entry)

        # Should show notification about limit
        mock_rumps.notification.assert_called()
        call_args = mock_rumps.notification.call_args
        assert str(MAX_PINNED_ENTRIES) in call_args[0][2]
        clipsy_app._build_menu.assert_not_called()


class TestOnEntryClick:
    """Test _on_entry_click method."""

    def test_invalid_sender_returns_early(self, clipsy_app):
        """Test that invalid sender ID returns early."""
        sender = MagicMock()
        sender._id = "nonexistent_key"
        clipsy_app._on_entry_click(sender)
        # No exception should be raised

    def test_missing_id_attribute_returns_early(self, clipsy_app):
        """Test that sender without _id returns early."""
        sender = MagicMock(spec=[])
        clipsy_app._on_entry_click(sender)
        # No exception should be raised

    def test_nonexistent_entry_returns_early(self, clipsy_app):
        """Test that nonexistent entry returns early."""
        clipsy_app._entry_ids["clipsy_entry_999"] = 999
        sender = MagicMock()
        sender._id = "clipsy_entry_999"
        clipsy_app._on_entry_click(sender)
        # No exception should be raised

    @patch("clipsy.app.rumps")
    def test_option_key_triggers_pin_toggle(self, mock_rumps, clipsy_app, make_entry):
        """Test that Option key triggers pin toggle."""
        clipsy_app._build_menu = MagicMock()

        entry_id = clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))
        clipsy_app._entry_ids[f"clipsy_entry_{entry_id}"] = entry_id

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        # Mock the AppKit imports inside the function
        mock_ns_event = MagicMock()
        mock_ns_event.modifierFlags.return_value = 0x80000  # Option key

        with patch.dict(
            "sys.modules",
            {
                "AppKit": MagicMock(NSEvent=mock_ns_event, NSAlternateKeyMask=0x80000),
            },
        ):
            clipsy_app._on_entry_click(sender)

        # Should have toggled pin (entry should now be pinned)
        entry = clipsy_app._storage.get_entry(entry_id)
        assert entry.pinned is True

    @patch("clipsy.app.rumps")
    def test_text_entry_copies_to_clipboard(self, mock_rumps, clipsy_app, make_entry):
        """Test that text entry is copied to clipboard."""
        clipsy_app._build_menu = MagicMock()

        entry_id = clipsy_app._storage.add_entry(make_entry("test text", content_hash="h1"))
        clipsy_app._entry_ids[f"clipsy_entry_{entry_id}"] = entry_id

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        # Mock AppKit
        mock_ns_event = MagicMock()
        mock_ns_event.modifierFlags.return_value = 0  # No modifier keys
        mock_pasteboard = MagicMock()
        mock_ns_pasteboard = MagicMock()
        mock_ns_pasteboard.generalPasteboard.return_value = mock_pasteboard

        with patch.dict(
            "sys.modules",
            {
                "AppKit": MagicMock(
                    NSEvent=mock_ns_event,
                    NSAlternateKeyMask=0x80000,
                    NSPasteboard=mock_ns_pasteboard,
                    NSPasteboardTypeString="public.utf8-plain-text",
                    NSPasteboardTypePNG="public.png",
                ),
                "Foundation": MagicMock(NSData=MagicMock()),
            },
        ):
            clipsy_app._on_entry_click(sender)

        mock_pasteboard.clearContents.assert_called()
        mock_pasteboard.setString_forType_.assert_called()
        mock_rumps.notification.assert_called()

    @patch("clipsy.app.rumps")
    def test_image_entry_copies_to_clipboard(self, mock_rumps, clipsy_app, make_entry):
        """Test that image entry is copied to clipboard."""
        clipsy_app._build_menu = MagicMock()

        entry = make_entry("img", content_type=ContentType.IMAGE, image_path="/path/img.png", content_hash="h1")
        entry_id = clipsy_app._storage.add_entry(entry)
        clipsy_app._entry_ids[f"clipsy_entry_{entry_id}"] = entry_id

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        mock_ns_event = MagicMock()
        mock_ns_event.modifierFlags.return_value = 0
        mock_pasteboard = MagicMock()
        mock_ns_pasteboard = MagicMock()
        mock_ns_pasteboard.generalPasteboard.return_value = mock_pasteboard
        mock_ns_data = MagicMock()
        mock_ns_data.dataWithContentsOfFile_.return_value = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "AppKit": MagicMock(
                    NSEvent=mock_ns_event,
                    NSAlternateKeyMask=0x80000,
                    NSPasteboard=mock_ns_pasteboard,
                    NSPasteboardTypeString="public.utf8-plain-text",
                    NSPasteboardTypePNG="public.png",
                ),
                "Foundation": MagicMock(NSData=mock_ns_data),
            },
        ):
            clipsy_app._on_entry_click(sender)

        mock_ns_data.dataWithContentsOfFile_.assert_called_with("/path/img.png")

    @patch("clipsy.app.rumps")
    def test_file_entry_copies_to_clipboard(self, mock_rumps, clipsy_app, make_entry):
        """Test that file entry is copied to clipboard."""
        clipsy_app._build_menu = MagicMock()

        entry = make_entry("/path/to/file.pdf", content_type=ContentType.FILE, content_hash="h1")
        entry_id = clipsy_app._storage.add_entry(entry)
        clipsy_app._entry_ids[f"clipsy_entry_{entry_id}"] = entry_id

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        mock_ns_event = MagicMock()
        mock_ns_event.modifierFlags.return_value = 0
        mock_pasteboard = MagicMock()
        mock_ns_pasteboard = MagicMock()
        mock_ns_pasteboard.generalPasteboard.return_value = mock_pasteboard

        with patch.dict(
            "sys.modules",
            {
                "AppKit": MagicMock(
                    NSEvent=mock_ns_event,
                    NSAlternateKeyMask=0x80000,
                    NSPasteboard=mock_ns_pasteboard,
                    NSPasteboardTypeString="public.utf8-plain-text",
                    NSPasteboardTypePNG="public.png",
                ),
                "Foundation": MagicMock(NSData=MagicMock()),
            },
        ):
            clipsy_app._on_entry_click(sender)

        mock_pasteboard.setString_forType_.assert_called()


class TestOnSearch:
    """Test _on_search method."""

    @patch("clipsy.app.rumps")
    def test_search_cancelled_does_nothing(self, mock_rumps, clipsy_app):
        """Test that cancelled search does nothing."""
        mock_response = MagicMock()
        mock_response.clicked = False
        mock_rumps.Window.return_value.run.return_value = mock_response

        clipsy_app._on_search(None)

        mock_rumps.alert.assert_not_called()

    @patch("clipsy.app.rumps")
    def test_search_empty_query_does_nothing(self, mock_rumps, clipsy_app):
        """Test that empty query does nothing."""
        mock_response = MagicMock()
        mock_response.clicked = True
        mock_response.text = "   "
        mock_rumps.Window.return_value.run.return_value = mock_response

        clipsy_app._on_search(None)

        mock_rumps.alert.assert_not_called()

    @patch("clipsy.app.rumps")
    def test_search_no_results_shows_alert(self, mock_rumps, clipsy_app):
        """Test that no results shows alert."""
        mock_response = MagicMock()
        mock_response.clicked = True
        mock_response.text = "nonexistent"
        mock_rumps.Window.return_value.run.return_value = mock_response

        clipsy_app._on_search(None)

        mock_rumps.alert.assert_called_once()

    @patch("clipsy.app.rumps")
    def test_search_with_results_clears_and_rebuilds_menu(self, mock_rumps, clipsy_app, make_entry):
        """Test that search with results clears and rebuilds menu."""
        # Add an entry that can be found
        entry_id = clipsy_app._storage.add_entry(make_entry("findable text", content_hash="h1"))

        mock_response = MagicMock()
        mock_response.clicked = True
        mock_response.text = "findable"
        mock_rumps.Window.return_value.run.return_value = mock_response

        # Track that menu.clear was called
        clear_called = []

        def track_clear():
            clear_called.append(True)

        clipsy_app.menu.clear = track_clear

        # Mock _render_menu_specs since it uses rumps
        clipsy_app._render_menu_specs = MagicMock()

        clipsy_app._on_search(None)

        assert len(clear_called) == 1
        # Entry should be in entry_ids after search results are computed
        assert f"clipsy_entry_{entry_id}" in clipsy_app._entry_ids


class TestComputeEntrySpec:
    """Test _compute_entry_spec method."""

    def test_creates_spec_for_text_entry(self, clipsy_app, make_entry):
        """Test creating spec for text entry."""
        from clipsy.app import MenuItemSpec

        entry_id = clipsy_app._storage.add_entry(make_entry("test text", content_hash="h1"))
        entry = clipsy_app._storage.get_entry(entry_id)

        spec = clipsy_app._compute_entry_spec(entry)

        assert isinstance(spec, MenuItemSpec)
        assert spec.title == "test text"
        assert spec.entry_id == entry_id
        assert f"clipsy_entry_{entry_id}" in clipsy_app._entry_ids

    def test_creates_spec_for_image_with_thumbnail(self, clipsy_app, make_entry):
        """Test creating spec for image entry with thumbnail."""
        from clipsy.app import MenuItemSpec

        entry = make_entry(
            "img",
            content_type=ContentType.IMAGE,
            image_path="/path/img.png",
            content_hash="h1",
        )
        entry_id = clipsy_app._storage.add_entry(entry)
        clipsy_app._storage.update_thumbnail_path(entry_id, "/path/thumb.png")
        entry = clipsy_app._storage.get_entry(entry_id)

        spec = clipsy_app._compute_entry_spec(entry)

        assert isinstance(spec, MenuItemSpec)
        assert spec.icon == "/path/thumb.png"
        assert spec.dimensions == (32, 32)
        assert spec.template is False

    def test_creates_spec_for_image_without_thumbnail(self, clipsy_app, make_entry):
        """Test creating spec for image entry without thumbnail."""
        from clipsy.app import MenuItemSpec

        entry = make_entry(
            "img",
            content_type=ContentType.IMAGE,
            image_path="/nonexistent/img.png",
            content_hash="h1",
            thumbnail_path=None,  # Explicitly no thumbnail
        )
        entry_id = clipsy_app._storage.add_entry(entry)
        entry = clipsy_app._storage.get_entry(entry_id)

        spec = clipsy_app._compute_entry_spec(entry)

        assert isinstance(spec, MenuItemSpec)
        assert spec.icon is None
        assert spec.dimensions is None


class TestOnEntryClickRichText:
    """Test _on_entry_click with RTF/HTML data."""

    @patch("clipsy.app.rumps")
    def test_text_entry_with_rtf_data(self, mock_rumps, clipsy_app, make_entry):
        """Test that RTF data is copied along with text."""
        clipsy_app._build_menu = MagicMock()

        rtf_data = b"{\\rtf1 Hello}"
        entry_id = clipsy_app._storage.add_entry(
            make_entry("Hello", content_hash="h1", rtf_data=rtf_data)
        )
        clipsy_app._entry_ids[f"clipsy_entry_{entry_id}"] = entry_id

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        mock_ns_event = MagicMock()
        mock_ns_event.modifierFlags.return_value = 0
        mock_pasteboard = MagicMock()
        mock_ns_pasteboard = MagicMock()
        mock_ns_pasteboard.generalPasteboard.return_value = mock_pasteboard
        mock_ns_data = MagicMock()
        mock_ns_data.dataWithBytes_length_.return_value = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "AppKit": MagicMock(
                    NSEvent=mock_ns_event,
                    NSAlternateKeyMask=0x80000,
                    NSPasteboard=mock_ns_pasteboard,
                    NSPasteboardTypeString="public.utf8-plain-text",
                    NSPasteboardTypePNG="public.png",
                ),
                "Foundation": MagicMock(NSData=mock_ns_data),
            },
        ):
            clipsy_app._on_entry_click(sender)

        # RTF data should have been set
        mock_ns_data.dataWithBytes_length_.assert_called()
        mock_pasteboard.setData_forType_.assert_called()

    @patch("clipsy.app.rumps")
    def test_text_entry_with_html_data(self, mock_rumps, clipsy_app, make_entry):
        """Test that HTML data is copied along with text."""
        clipsy_app._build_menu = MagicMock()

        html_data = b"<p>Hello</p>"
        entry_id = clipsy_app._storage.add_entry(
            make_entry("Hello", content_hash="h1", html_data=html_data)
        )
        clipsy_app._entry_ids[f"clipsy_entry_{entry_id}"] = entry_id

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        mock_ns_event = MagicMock()
        mock_ns_event.modifierFlags.return_value = 0
        mock_pasteboard = MagicMock()
        mock_ns_pasteboard = MagicMock()
        mock_ns_pasteboard.generalPasteboard.return_value = mock_pasteboard
        mock_ns_data = MagicMock()
        mock_ns_data.dataWithBytes_length_.return_value = MagicMock()

        with patch.dict(
            "sys.modules",
            {
                "AppKit": MagicMock(
                    NSEvent=mock_ns_event,
                    NSAlternateKeyMask=0x80000,
                    NSPasteboard=mock_ns_pasteboard,
                    NSPasteboardTypeString="public.utf8-plain-text",
                    NSPasteboardTypePNG="public.png",
                ),
                "Foundation": MagicMock(NSData=mock_ns_data),
            },
        ):
            clipsy_app._on_entry_click(sender)

        mock_ns_data.dataWithBytes_length_.assert_called()


class TestOnEntryClickExceptionHandling:
    """Test _on_entry_click exception handling."""

    @patch("clipsy.app.rumps")
    @patch("clipsy.app.logger")
    def test_exception_during_copy_is_logged(self, mock_logger, mock_rumps, clipsy_app, make_entry):
        """Test that exceptions during copy are logged."""
        clipsy_app._build_menu = MagicMock()

        entry_id = clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))
        clipsy_app._entry_ids[f"clipsy_entry_{entry_id}"] = entry_id

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        mock_ns_event = MagicMock()
        mock_ns_event.modifierFlags.return_value = 0
        mock_ns_pasteboard = MagicMock()
        mock_ns_pasteboard.generalPasteboard.side_effect = Exception("Clipboard error")

        with patch.dict(
            "sys.modules",
            {
                "AppKit": MagicMock(
                    NSEvent=mock_ns_event,
                    NSAlternateKeyMask=0x80000,
                    NSPasteboard=mock_ns_pasteboard,
                    NSPasteboardTypeString="public.utf8-plain-text",
                    NSPasteboardTypePNG="public.png",
                ),
                "Foundation": MagicMock(NSData=MagicMock()),
            },
        ):
            clipsy_app._on_entry_click(sender)

        mock_logger.exception.assert_called()

    def test_modifier_check_exception_continues_to_copy(self, clipsy_app, make_entry):
        """Test that exception during modifier check continues to copy."""
        clipsy_app._build_menu = MagicMock()

        entry_id = clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))
        clipsy_app._entry_ids[f"clipsy_entry_{entry_id}"] = entry_id

        sender = MagicMock()
        sender._id = f"clipsy_entry_{entry_id}"

        # Make AppKit import raise an exception
        with patch.dict("sys.modules", {"AppKit": None}):
            # This should not crash - it should continue to the copy logic
            # which will then fail because we haven't mocked the copy path
            try:
                clipsy_app._on_entry_click(sender)
            except (TypeError, AttributeError):
                pass  # Expected - we didn't mock the full copy path


class TestComputeMenuSpecs:
    """Test _compute_menu_specs method - pure logic, no rumps."""

    def test_empty_history_shows_no_history_message(self, clipsy_app):
        """Test that empty history shows appropriate message."""
        from clipsy.app import MenuItemSpec

        specs = clipsy_app._compute_menu_specs()

        # Find the "no history" item
        titles = [s.title if s else None for s in specs]
        assert "(No clipboard history)" in titles

    def test_with_entries_shows_entries(self, clipsy_app, make_entry):
        """Test that entries are included in specs."""
        from clipsy.app import MenuItemSpec

        clipsy_app._storage.add_entry(make_entry("test entry", content_hash="h1"))

        specs = clipsy_app._compute_menu_specs()

        # Should have the entry
        entry_specs = [s for s in specs if s and s.entry_id is not None]
        assert len(entry_specs) == 1
        assert entry_specs[0].title == "test entry"

    def test_with_pinned_entries_creates_submenu(self, clipsy_app, make_entry):
        """Test that pinned entries create a submenu."""
        entry_id = clipsy_app._storage.add_entry(make_entry("pinned", content_hash="h1"))
        clipsy_app._storage.toggle_pin(entry_id)

        specs = clipsy_app._compute_menu_specs()

        # Find pinned submenu
        pinned_submenu = [s for s in specs if s and s.is_submenu and "Pinned" in s.title]
        assert len(pinned_submenu) == 1
        assert pinned_submenu[0].children is not None
        assert len(pinned_submenu[0].children) >= 2  # Entry + separator + clear

    def test_includes_standard_menu_items(self, clipsy_app):
        """Test that standard menu items are included."""
        specs = clipsy_app._compute_menu_specs()

        titles = [s.title if s else None for s in specs]
        assert any("Clipsy v" in t for t in titles if t)
        assert "Search..." in titles
        assert "Clear History" in titles
        assert "Support Clipsy" in titles
        assert "Quit Clipsy" in titles


class TestComputeSearchResultsSpecs:
    """Test _compute_search_results_specs method."""

    def test_creates_specs_for_search_results(self, clipsy_app, make_entry):
        """Test that search results create proper specs."""
        from clipsy.app import MenuItemSpec

        entry = make_entry("findable", content_hash="h1")
        entry_id = clipsy_app._storage.add_entry(entry)
        results = clipsy_app._storage.search("findable")

        specs = clipsy_app._compute_search_results_specs("findable", results)

        # Check header
        assert any(s and 'Search: "findable"' in s.title for s in specs)

        # Check "Show All" is present
        titles = [s.title if s else None for s in specs]
        assert "Show All" in titles

        # Check entry is included
        entry_specs = [s for s in specs if s and s.entry_id is not None]
        assert len(entry_specs) == 1

        # Check "Quit" is present
        assert "Quit Clipsy" in titles


class TestInitApp:
    """Test _init_app method."""

    @patch("clipsy.app.ClipboardMonitor")
    @patch("clipsy.app.StorageManager")
    @patch("clipsy.app.ensure_dirs")
    def test_initializes_components(self, mock_dirs, mock_storage, mock_monitor, clipsy_app):
        """Test that _init_app initializes all components."""
        mock_storage.return_value = MagicMock()
        mock_monitor.return_value = MagicMock()

        # Reset state
        clipsy_app._storage = None
        clipsy_app._monitor = None
        clipsy_app._entry_ids = None

        # Call _init_app
        clipsy_app._init_app()

        mock_dirs.assert_called_once()
        mock_storage.assert_called_once()
        mock_monitor.assert_called_once()


class TestBuildMenu:
    """Test _build_menu method."""

    def test_clears_and_rebuilds(self, clipsy_app, make_entry):
        """Test that _build_menu clears menu and entry_ids."""
        # Add an entry
        clipsy_app._storage.add_entry(make_entry("test", content_hash="h1"))

        # Pre-populate entry_ids
        clipsy_app._entry_ids["old_key"] = 999

        # Mock _render_menu_specs since it uses rumps
        clipsy_app._render_menu_specs = MagicMock()

        # Call _build_menu (need to bind the real method)
        from clipsy.app import ClipsyApp
        ClipsyApp._build_menu(clipsy_app)

        # Old key should be gone
        assert "old_key" not in clipsy_app._entry_ids
        # New entry should be present (added by _compute_menu_specs -> _compute_entry_spec)
        assert len(clipsy_app._entry_ids) == 1
        clipsy_app._render_menu_specs.assert_called_once()


class TestEnsureThumbnailGeneration:
    """Test _ensure_thumbnail thumbnail generation code path."""

    @patch("clipsy.app.create_thumbnail", return_value=True)
    def test_generates_thumbnail_for_existing_image(self, mock_create, clipsy_app, tmp_path):
        """Test that thumbnail is generated for existing image."""
        # Create a real image file
        img_path = tmp_path / "test.png"
        img_path.write_bytes(b"fake png data")

        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.IMAGE,
            text_content=None,
            image_path=str(img_path),
            preview="Image",
            content_hash="h1",
            byte_size=100,
            created_at=datetime.now(),
            thumbnail_path=None,
        )

        # Mock the storage update
        clipsy_app._storage.update_thumbnail_path = MagicMock()

        with patch("clipsy.app.IMAGE_DIR", tmp_path):
            result = clipsy_app._ensure_thumbnail(entry)

        mock_create.assert_called_once()
        clipsy_app._storage.update_thumbnail_path.assert_called_once()

    @patch("clipsy.app.create_thumbnail", return_value=False)
    def test_returns_none_when_thumbnail_creation_fails(self, mock_create, clipsy_app, tmp_path):
        """Test that None is returned when thumbnail creation fails."""
        img_path = tmp_path / "test.png"
        img_path.write_bytes(b"fake png data")

        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.IMAGE,
            text_content=None,
            image_path=str(img_path),
            preview="Image",
            content_hash="h1",
            byte_size=100,
            created_at=datetime.now(),
            thumbnail_path=None,
        )

        with patch("clipsy.app.IMAGE_DIR", tmp_path):
            result = clipsy_app._ensure_thumbnail(entry)

        assert result is None

    def test_uses_existing_thumbnail_file(self, clipsy_app, tmp_path):
        """Test that existing thumbnail file is used."""
        img_path = tmp_path / "test.png"
        img_path.write_bytes(b"fake png data")
        thumb_path = tmp_path / "test_thumb.png"
        thumb_path.write_bytes(b"fake thumb data")

        entry = ClipboardEntry(
            id=1,
            content_type=ContentType.IMAGE,
            text_content=None,
            image_path=str(img_path),
            preview="Image",
            content_hash="h1",
            byte_size=100,
            created_at=datetime.now(),
            thumbnail_path=None,
        )

        clipsy_app._storage.update_thumbnail_path = MagicMock()

        with patch("clipsy.app.IMAGE_DIR", tmp_path):
            result = clipsy_app._ensure_thumbnail(entry)

        assert result == str(thumb_path)
        clipsy_app._storage.update_thumbnail_path.assert_called_once()


class TestRenderMenuSpecs:
    """Test _render_menu_specs converts specs to rumps items."""

    def test_renders_specs_to_menu_items(self, clipsy_app):
        """Test that specs are converted to menu items list."""
        from clipsy.app import ClipsyApp, MenuItemSpec

        mock_menu_item = MagicMock()
        with patch("clipsy.app.rumps.MenuItem", return_value=mock_menu_item):
            specs = [
                MenuItemSpec("Item 1"),
                None,  # separator
                MenuItemSpec("Item 2", callback=lambda x: None),
            ]
            ClipsyApp._render_menu_specs(clipsy_app, specs)

        # menu should be set to the list of items
        assert isinstance(clipsy_app.menu, list)
        assert len(clipsy_app.menu) == 3


class TestRenderSingleSpec:
    """Test _render_single_spec for various spec types."""

    def test_none_spec_returns_none(self, clipsy_app):
        """Test that None spec returns None (separator)."""
        from clipsy.app import ClipsyApp

        result = ClipsyApp._render_single_spec(clipsy_app, None)
        assert result is None

    def test_simple_spec_creates_menu_item(self, clipsy_app):
        """Test that simple spec creates MenuItem."""
        from clipsy.app import ClipsyApp, MenuItemSpec

        mock_item = MagicMock()
        with patch("clipsy.app.rumps.MenuItem", return_value=mock_item) as mock_cls:
            spec = MenuItemSpec("Test Item")
            result = ClipsyApp._render_single_spec(clipsy_app, spec)

        mock_cls.assert_called_once_with("Test Item", callback=None)
        assert result == mock_item

    def test_spec_with_callback_passes_callback(self, clipsy_app):
        """Test that callback is passed to MenuItem."""
        from clipsy.app import ClipsyApp, MenuItemSpec

        mock_item = MagicMock()
        callback = MagicMock()
        with patch("clipsy.app.rumps.MenuItem", return_value=mock_item) as mock_cls:
            spec = MenuItemSpec("Test Item", callback=callback)
            result = ClipsyApp._render_single_spec(clipsy_app, spec)

        mock_cls.assert_called_once_with("Test Item", callback=callback)

    def test_spec_with_icon_passes_icon(self, clipsy_app):
        """Test that icon is passed to MenuItem."""
        from clipsy.app import ClipsyApp, MenuItemSpec

        mock_item = MagicMock()
        with patch("clipsy.app.rumps.MenuItem", return_value=mock_item) as mock_cls:
            spec = MenuItemSpec("Test Item", icon="/path/to/icon.png")
            result = ClipsyApp._render_single_spec(clipsy_app, spec)

        mock_cls.assert_called_once_with(
            "Test Item", callback=None, icon="/path/to/icon.png"
        )

    def test_spec_with_dimensions_passes_dimensions(self, clipsy_app):
        """Test that dimensions are passed to MenuItem."""
        from clipsy.app import ClipsyApp, MenuItemSpec

        mock_item = MagicMock()
        with patch("clipsy.app.rumps.MenuItem", return_value=mock_item) as mock_cls:
            spec = MenuItemSpec("Test Item", icon="/path.png", dimensions=(32, 32))
            result = ClipsyApp._render_single_spec(clipsy_app, spec)

        mock_cls.assert_called_once_with(
            "Test Item", callback=None, icon="/path.png", dimensions=(32, 32)
        )

    def test_spec_with_template_passes_template(self, clipsy_app):
        """Test that template is passed to MenuItem."""
        from clipsy.app import ClipsyApp, MenuItemSpec

        mock_item = MagicMock()
        with patch("clipsy.app.rumps.MenuItem", return_value=mock_item) as mock_cls:
            spec = MenuItemSpec("Test Item", icon="/path.png", template=False)
            result = ClipsyApp._render_single_spec(clipsy_app, spec)

        mock_cls.assert_called_once_with(
            "Test Item", callback=None, icon="/path.png", template=False
        )

    def test_spec_with_entry_id_sets_id(self, clipsy_app):
        """Test that entry_id is set on the MenuItem."""
        from clipsy.app import ClipsyApp, MenuItemSpec

        mock_item = MagicMock()
        with patch("clipsy.app.rumps.MenuItem", return_value=mock_item):
            spec = MenuItemSpec("Test Item", entry_id=42)
            result = ClipsyApp._render_single_spec(clipsy_app, spec)

        assert mock_item._id == "clipsy_entry_42"

    def test_submenu_spec_creates_submenu(self, clipsy_app):
        """Test that submenu spec creates MenuItem with children."""
        from clipsy.app import ClipsyApp, MenuItemSpec

        # Track MenuItem instances
        menu_items = []

        def create_menu_item(*args, **kwargs):
            item = MagicMock()
            menu_items.append(item)
            return item

        # Bind the real method to clipsy_app for recursive calls
        clipsy_app._render_single_spec = lambda spec: ClipsyApp._render_single_spec(
            clipsy_app, spec
        )

        with patch("clipsy.app.rumps.MenuItem", side_effect=create_menu_item):
            spec = MenuItemSpec(
                "Parent",
                is_submenu=True,
                children=[
                    MenuItemSpec("Child 1"),
                    None,  # separator
                    MenuItemSpec("Child 2"),
                ],
            )
            result = ClipsyApp._render_single_spec(clipsy_app, spec)

        # Parent + 2 children = 3 MenuItem instances
        assert len(menu_items) == 3
        # Parent should have add called for each child
        parent = menu_items[0]
        assert parent.add.call_count == 3  # 2 children + 1 separator (None)


class TestClipsyAppInitialization:
    """Test ClipsyApp.__init__ method."""

    @patch("clipsy.app.ClipsyApp._init_app")
    @patch("rumps.App.__init__")
    def test_init_calls_super_and_init_app(self, mock_super_init, mock_init_app):
        """Test that __init__ calls super().__init__ and _init_app."""
        from clipsy.app import ClipsyApp

        # Create instance
        app = object.__new__(ClipsyApp)
        ClipsyApp.__init__(app)

        mock_super_init.assert_called_once_with("Clipsy", title="✂️", quit_button=None)
        mock_init_app.assert_called_once()
