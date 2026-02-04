import struct
from unittest.mock import MagicMock, patch

from clipsy.utils import compute_hash, create_thumbnail, ensure_dirs, get_image_dimensions, truncate_text


class TestComputeHash:
    def test_string_input(self):
        h = compute_hash("hello")
        assert isinstance(h, str)
        assert len(h) == 64  # SHA-256 hex digest

    def test_bytes_input(self):
        h = compute_hash(b"hello")
        assert isinstance(h, str)
        assert len(h) == 64

    def test_same_content_same_hash(self):
        assert compute_hash("test") == compute_hash("test")

    def test_different_content_different_hash(self):
        assert compute_hash("abc") != compute_hash("xyz")

    def test_string_and_bytes_same_hash(self):
        assert compute_hash("hello") == compute_hash(b"hello")


class TestTruncateText:
    def test_short_text_unchanged(self):
        assert truncate_text("hello", 60) == "hello"

    def test_long_text_truncated(self):
        result = truncate_text("a" * 100, 60)
        assert len(result) == 60
        assert result.endswith("...")

    def test_multiline_collapsed(self):
        result = truncate_text("hello\nworld\nfoo", 60)
        assert "\n" not in result
        assert result == "hello world foo"

    def test_exact_length_not_truncated(self):
        text = "a" * 60
        assert truncate_text(text, 60) == text

    def test_whitespace_normalized(self):
        result = truncate_text("  hello   world  ", 60)
        assert result == "hello world"


class TestGetImageDimensions:
    def test_valid_png(self):
        header = b"\x89PNG\r\n\x1a\n"
        ihdr_type = b"\x00\x00\x00\rIHDR"
        width = struct.pack(">I", 1920)
        height = struct.pack(">I", 1080)
        png_bytes = header + ihdr_type + width + height + b"\x00" * 100
        w, h = get_image_dimensions(png_bytes)
        assert w == 1920
        assert h == 1080

    def test_invalid_data(self):
        assert get_image_dimensions(b"not a png") == (0, 0)

    def test_too_short(self):
        assert get_image_dimensions(b"\x89PNG") == (0, 0)

    def test_empty(self):
        assert get_image_dimensions(b"") == (0, 0)


class TestEnsureDirs:
    def test_creates_directories(self, tmp_path):
        data_dir = tmp_path / "data"
        image_dir = data_dir / "images"

        with patch("clipsy.utils.DATA_DIR", data_dir), patch("clipsy.utils.IMAGE_DIR", image_dir):
            ensure_dirs()

        assert data_dir.exists()
        assert image_dir.exists()

    def test_idempotent(self, tmp_path):
        data_dir = tmp_path / "data"
        image_dir = data_dir / "images"

        with patch("clipsy.utils.DATA_DIR", data_dir), patch("clipsy.utils.IMAGE_DIR", image_dir):
            ensure_dirs()
            ensure_dirs()  # Should not raise

        assert data_dir.exists()
        assert image_dir.exists()


class TestCreateThumbnail:
    def test_nonexistent_file_returns_false(self, tmp_path):
        result = create_thumbnail(
            str(tmp_path / "nonexistent.png"),
            str(tmp_path / "thumb.png"),
        )
        assert result is False

    def test_invalid_image_returns_false(self, tmp_path):
        # Create a file with invalid image data
        invalid_file = tmp_path / "invalid.png"
        invalid_file.write_bytes(b"not a valid image")

        result = create_thumbnail(
            str(invalid_file),
            str(tmp_path / "thumb.png"),
        )
        assert result is False
