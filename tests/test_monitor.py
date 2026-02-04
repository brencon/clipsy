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

    def test_multiple_files(self, monitor, mock_pasteboard, storage):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["NSFilenamesPboardType"]
        mock_pasteboard.propertyListForType_.return_value = [
            "/Users/test/file1.txt",
            "/Users/test/file2.txt",
            "/Users/test/file3.txt",
        ]

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
        assert "3 files" in entries[0].preview


class TestImageClipboard:
    def test_png_image(self, monitor, mock_pasteboard, storage, tmp_path):
        # Create a minimal valid PNG header
        png_header = b"\x89PNG\r\n\x1a\n"
        ihdr_chunk = b"\x00\x00\x00\rIHDR"
        # Width: 100, Height: 50
        width = (100).to_bytes(4, "big")
        height = (50).to_bytes(4, "big")
        png_data = png_header + ihdr_chunk + width + height + b"\x00" * 100

        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.png"]
        mock_pasteboard.dataForType_.return_value = png_data

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypePNG", "public.png"),
            patch("clipsy.monitor.NSPasteboardTypeTIFF", "public.tiff"),
            patch("clipsy.monitor.NSFilenamesPboardType", "NSFilenamesPboardType"),
            patch("clipsy.monitor.IMAGE_DIR", tmp_path / "images"),
        ):
            (tmp_path / "images").mkdir(exist_ok=True)
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].content_type == ContentType.IMAGE
        assert "100x50" in entries[0].preview

    def test_image_saved_to_disk(self, monitor, mock_pasteboard, storage, tmp_path):
        png_header = b"\x89PNG\r\n\x1a\n"
        ihdr_chunk = b"\x00\x00\x00\rIHDR"
        width = (100).to_bytes(4, "big")
        height = (50).to_bytes(4, "big")
        png_data = png_header + ihdr_chunk + width + height + b"\x00" * 100

        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.png"]
        mock_pasteboard.dataForType_.return_value = png_data

        image_dir = tmp_path / "images"
        image_dir.mkdir(exist_ok=True)

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypePNG", "public.png"),
            patch("clipsy.monitor.NSPasteboardTypeTIFF", "public.tiff"),
            patch("clipsy.monitor.NSFilenamesPboardType", "NSFilenamesPboardType"),
            patch("clipsy.monitor.IMAGE_DIR", image_dir),
        ):
            monitor.check_clipboard()

        # Check that a PNG file was saved
        png_files = list(image_dir.glob("*.png"))
        assert len(png_files) == 1

    def test_image_none_data_skipped(self, monitor, mock_pasteboard, storage):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.png"]
        mock_pasteboard.dataForType_.return_value = None

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypePNG", "public.png"),
            patch("clipsy.monitor.NSPasteboardTypeTIFF", "public.tiff"),
            patch("clipsy.monitor.NSFilenamesPboardType", "NSFilenamesPboardType"),
        ):
            assert monitor.check_clipboard() is False

        assert storage.count() == 0


class TestSyncChangeCount:
    def test_sync_change_count(self, monitor, mock_pasteboard):
        mock_pasteboard.changeCount.return_value = 42
        monitor.sync_change_count()
        assert monitor._last_change_count == 42


class TestErrorHandling:
    def test_exception_in_read_clipboard_returns_false(self, monitor, mock_pasteboard):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.side_effect = Exception("Test error")

        result = monitor.check_clipboard()
        assert result is False
