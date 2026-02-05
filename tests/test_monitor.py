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


class TestSensitiveDataHandling:
    def test_sensitive_text_detected_and_masked(self, monitor, mock_pasteboard, storage):
        """Test that sensitive data is detected and masked (lines 73-74)."""
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.utf8-plain-text"]
        mock_pasteboard.stringForType_.return_value = "password=mysecret123"

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.REDACT_SENSITIVE", True),
        ):
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].is_sensitive is True
        assert entries[0].masked_preview is not None
        assert "mysecret123" not in entries[0].masked_preview


class TestLargeImageHandling:
    def test_large_image_skipped(self, monitor, mock_pasteboard, storage, tmp_path):
        """Test that images exceeding MAX_IMAGE_SIZE are skipped (lines 96-97)."""
        # Create large image data
        large_png_header = b"\x89PNG\r\n\x1a\n"
        ihdr_chunk = b"\x00\x00\x00\rIHDR"
        width = (100).to_bytes(4, "big")
        height = (50).to_bytes(4, "big")
        # Make it larger than MAX_IMAGE_SIZE (10MB)
        large_data = large_png_header + ihdr_chunk + width + height + b"\x00" * (11 * 1024 * 1024)

        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.png"]
        mock_pasteboard.dataForType_.return_value = large_data

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypePNG", "public.png"),
            patch("clipsy.monitor.NSPasteboardTypeTIFF", "public.tiff"),
            patch("clipsy.monitor.NSFilenamesPboardType", "NSFilenamesPboardType"),
            patch("clipsy.monitor.MAX_IMAGE_SIZE", 10 * 1024 * 1024),  # 10MB
        ):
            # Should return False because the image is too large
            result = monitor.check_clipboard()
            assert result is False

        # No entry should be stored
        assert storage.count() == 0


class TestThumbnailGeneration:
    def test_thumbnail_generated_with_image(self, monitor, mock_pasteboard, storage, tmp_path):
        """Test that thumbnail is generated when saving an image (line 150)."""
        import zlib

        def create_minimal_png():
            signature = b"\x89PNG\r\n\x1a\n"
            ihdr_data = b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
            ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF
            ihdr_chunk = b"\x00\x00\x00\x0d" + b"IHDR" + ihdr_data + ihdr_crc.to_bytes(4, "big")
            raw_data = b"\x00\xff\x00\x00"
            compressed = zlib.compress(raw_data)
            idat_crc = zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF
            idat_chunk = len(compressed).to_bytes(4, "big") + b"IDAT" + compressed + idat_crc.to_bytes(4, "big")
            iend_crc = zlib.crc32(b"IEND") & 0xFFFFFFFF
            iend_chunk = b"\x00\x00\x00\x00" + b"IEND" + iend_crc.to_bytes(4, "big")
            return signature + ihdr_chunk + idat_chunk + iend_chunk

        png_data = create_minimal_png()

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
            patch("clipsy.monitor.create_thumbnail") as mock_create_thumb,
        ):
            mock_create_thumb.return_value = True
            monitor.check_clipboard()

        # Verify create_thumbnail was called
        mock_create_thumb.assert_called_once()

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].thumbnail_path is not None

    def test_existing_thumbnail_reused(self, monitor, mock_pasteboard, storage, tmp_path):
        """Test that existing thumbnail is reused (line 153)."""
        import zlib

        def create_minimal_png():
            signature = b"\x89PNG\r\n\x1a\n"
            ihdr_data = b"\x00\x00\x00\x01\x00\x00\x00\x01\x08\x02\x00\x00\x00"
            ihdr_crc = zlib.crc32(b"IHDR" + ihdr_data) & 0xFFFFFFFF
            ihdr_chunk = b"\x00\x00\x00\x0d" + b"IHDR" + ihdr_data + ihdr_crc.to_bytes(4, "big")
            raw_data = b"\x00\xff\x00\x00"
            compressed = zlib.compress(raw_data)
            idat_crc = zlib.crc32(b"IDAT" + compressed) & 0xFFFFFFFF
            idat_chunk = len(compressed).to_bytes(4, "big") + b"IDAT" + compressed + idat_crc.to_bytes(4, "big")
            iend_crc = zlib.crc32(b"IEND") & 0xFFFFFFFF
            iend_chunk = b"\x00\x00\x00\x00" + b"IEND" + iend_crc.to_bytes(4, "big")
            return signature + ihdr_chunk + idat_chunk + iend_chunk

        from clipsy.utils import compute_hash

        png_data = create_minimal_png()
        content_hash = compute_hash(png_data)

        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.png"]
        mock_pasteboard.dataForType_.return_value = png_data

        image_dir = tmp_path / "images"
        image_dir.mkdir(exist_ok=True)

        # Pre-create the thumbnail file
        thumb_filename = content_hash[:12] + "_thumb.png"
        thumb_path = image_dir / thumb_filename
        thumb_path.write_bytes(b"fake thumbnail")

        # Also create the main image file
        main_filename = content_hash[:12] + ".png"
        main_path = image_dir / main_filename
        main_path.write_bytes(png_data)

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypePNG", "public.png"),
            patch("clipsy.monitor.NSPasteboardTypeTIFF", "public.tiff"),
            patch("clipsy.monitor.NSFilenamesPboardType", "NSFilenamesPboardType"),
            patch("clipsy.monitor.IMAGE_DIR", image_dir),
            patch("clipsy.monitor.create_thumbnail") as mock_create_thumb,
        ):
            monitor.check_clipboard()

        # create_thumbnail should NOT be called since file already exists
        mock_create_thumb.assert_not_called()

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].thumbnail_path == str(thumb_path)


class TestRichTextClipboard:
    def test_rtf_data_captured(self, monitor, mock_pasteboard, storage):
        rtf_bytes = b"{\\rtf1\\ansi Hello \\b World\\b0}"
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.utf8-plain-text", "public.rtf"]
        mock_pasteboard.stringForType_.return_value = "Hello World"
        mock_pasteboard.dataForType_.return_value = rtf_bytes

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypeRTF", "public.rtf"),
            patch("clipsy.monitor.NSPasteboardTypeHTML", "public.html"),
        ):
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].text_content == "Hello World"
        assert entries[0].rtf_data == rtf_bytes

    def test_html_data_captured(self, monitor, mock_pasteboard, storage):
        html_bytes = b"<p>Hello <b>World</b></p>"
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.utf8-plain-text", "public.html"]
        mock_pasteboard.stringForType_.return_value = "Hello World"
        mock_pasteboard.dataForType_.return_value = html_bytes

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypeRTF", "public.rtf"),
            patch("clipsy.monitor.NSPasteboardTypeHTML", "public.html"),
        ):
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].html_data == html_bytes

    def test_both_rtf_and_html_captured(self, monitor, mock_pasteboard, storage):
        rtf_bytes = b"{\\rtf1\\ansi Hello}"
        html_bytes = b"<p>Hello</p>"
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.utf8-plain-text", "public.rtf", "public.html"]
        mock_pasteboard.stringForType_.return_value = "Hello"

        def data_for_type(type_str):
            if type_str == "public.rtf":
                return rtf_bytes
            if type_str == "public.html":
                return html_bytes
            return None

        mock_pasteboard.dataForType_ = data_for_type

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypeRTF", "public.rtf"),
            patch("clipsy.monitor.NSPasteboardTypeHTML", "public.html"),
        ):
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].rtf_data == rtf_bytes
        assert entries[0].html_data == html_bytes

    def test_plain_text_without_rtf(self, monitor, mock_pasteboard, storage):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.utf8-plain-text"]
        mock_pasteboard.stringForType_.return_value = "plain text"

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypeRTF", "public.rtf"),
            patch("clipsy.monitor.NSPasteboardTypeHTML", "public.html"),
        ):
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].rtf_data is None
        assert entries[0].html_data is None

    def test_rtf_data_for_type_returns_none(self, monitor, mock_pasteboard, storage):
        mock_pasteboard.changeCount.return_value = 1
        mock_pasteboard.types.return_value = ["public.utf8-plain-text", "public.rtf"]
        mock_pasteboard.stringForType_.return_value = "Hello"
        mock_pasteboard.dataForType_.return_value = None

        with (
            patch("clipsy.monitor.NSPasteboardTypeString", "public.utf8-plain-text"),
            patch("clipsy.monitor.NSPasteboardTypeRTF", "public.rtf"),
            patch("clipsy.monitor.NSPasteboardTypeHTML", "public.html"),
        ):
            assert monitor.check_clipboard() is True

        entries = storage.get_recent()
        assert len(entries) == 1
        assert entries[0].rtf_data is None
