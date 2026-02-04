from unittest.mock import MagicMock, patch

import pytest

from clipsy.models import ContentType
from clipsy.monitor import ClipboardMonitor


@pytest.fixture
def mock_pasteboard():
    with patch("clipsy.monitor.NSPasteboard") as mock_pb_class:
        mock_pb = MagicMock()
        mock_pb_class.generalPasteboard.return_value = mock_pb
        mock_pb.changeCount.return_value = 0
        mock_pb.types.return_value = []
        yield mock_pb


@pytest.fixture
def monitor(storage, mock_pasteboard, tmp_path):
    with patch("clipsy.monitor.ensure_dirs"):
        with patch("clipsy.monitor.IMAGE_DIR", tmp_path / "images"):
            (tmp_path / "images").mkdir()
            mon = ClipboardMonitor(storage)
            mon._pasteboard = mock_pasteboard
            yield mon


class TestCheckClipboard:
    def test_no_change(self, monitor, mock_pasteboard):
        mock_pasteboard.changeCount.return_value = 0
        assert monitor.check_clipboard() is False

    def test_text_change(self, monitor, mock_pasteboard, storage):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.utf8-plain-text"]
        mock_pasteboard.stringForType_.return_value = "hello world"

        with patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"):
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].content_type == ContentType.TEXT
        assert entries[0].text_content == "hello world"

    def test_duplicate_text_bumps_timestamp(self, monitor, mock_pasteboard, storage):
        mock_pasteboard.types.return_value = ["public.utf8-plain-text"]
        mock_pasteboard.stringForType_.return_value = "duplicate"

        with patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"):
            mock_pasteboard.changeCount.return_value = 1
            monitor.check_clipboard()

            mock_pasteboard.changeCount.return_value = 2
            monitor.check_clipboard()

        entries = storage.get_recent()
        assert len(entries) == 1

    def test_callback_called_on_change(self, storage, mock_pasteboard, tmp_path):
        callback = MagicMock()
        with patch("clipsy.monitor.ensure_dirs"):
            with patch("clipsy.monitor.IMAGE_DIR", tmp_path / "images"):
                (tmp_path / "images").mkdir(exist_ok=True)
                mon = ClipboardMonitor(storage, on_change=callback)
                mon._pasteboard = mock_pasteboard

        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.utf8-plain-text"]
        mock_pasteboard.stringForType_.return_value = "test"

        with patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"):
            mon.check_clipboard()

        callback.assert_called_once()

    def test_empty_clipboard_no_entry(self, monitor, mock_pasteboard, storage):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = []

        assert monitor.check_clipboard() is False
        assert storage.count() == 0

    def test_none_types_no_crash(self, monitor, mock_pasteboard):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = None

        assert monitor.check_clipboard() is False


class TestFileClipboard:
    def test_single_file(self, monitor, mock_pasteboard, storage):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["NSFilenamesPboardType"]
        mock_pasteboard.propertyListForType_.return_value = ["/Users/test/document.pdf"]

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypePNG", "public.png"),
            patch("clipsy.monitor.NSPasteboardTypeTIFF", "public.tiff"),
            patch("clipsy.monitor.NSFilenamesPboardType", "NSFilenamesPboardType"),
        ):
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].content_type == ContentType.FILE
        assert "document.pdf" in entries[0].preview
