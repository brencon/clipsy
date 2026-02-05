import os
from unittest.mock import patch

from clipsy.config import _parse_menu_display_count


class TestParseMenuDisplayCount:
    def test_default_when_not_set(self):
        env = os.environ.copy()
        env.pop("CLIPSY_MENU_DISPLAY_COUNT", None)
        with patch.dict("os.environ", env, clear=True):
            assert _parse_menu_display_count() == 10

    def test_valid_value(self):
        with patch.dict("os.environ", {"CLIPSY_MENU_DISPLAY_COUNT": "20"}):
            assert _parse_menu_display_count() == 20

    def test_clamped_below_minimum(self):
        with patch.dict("os.environ", {"CLIPSY_MENU_DISPLAY_COUNT": "2"}):
            assert _parse_menu_display_count() == 5

    def test_clamped_above_maximum(self):
        with patch.dict("os.environ", {"CLIPSY_MENU_DISPLAY_COUNT": "100"}):
            assert _parse_menu_display_count() == 50

    def test_invalid_non_integer(self):
        with patch.dict("os.environ", {"CLIPSY_MENU_DISPLAY_COUNT": "abc"}):
            assert _parse_menu_display_count() == 10

    def test_boundary_minimum(self):
        with patch.dict("os.environ", {"CLIPSY_MENU_DISPLAY_COUNT": "5"}):
            assert _parse_menu_display_count() == 5

    def test_boundary_maximum(self):
        with patch.dict("os.environ", {"CLIPSY_MENU_DISPLAY_COUNT": "50"}):
            assert _parse_menu_display_count() == 50
