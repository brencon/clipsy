import os
from pathlib import Path

DATA_DIR = Path(os.environ.get("CLIPSY_DATA_DIR", Path.home() / ".local" / "share" / "clipsy"))
DB_PATH = DATA_DIR / "clipsy.db"
IMAGE_DIR = DATA_DIR / "images"
LOG_PATH = DATA_DIR / "clipsy.log"

POLL_INTERVAL = 0.5  # seconds between clipboard checks
MAX_ENTRIES = 500  # auto-purge threshold
MAX_TEXT_SIZE = 1_000_000  # 1MB text limit
MAX_IMAGE_SIZE = 10_000_000  # 10MB image limit
PREVIEW_LENGTH = 60  # characters shown in menu item
def _parse_menu_display_count() -> int:
    raw = os.environ.get("CLIPSY_MENU_DISPLAY_COUNT")
    if raw is None:
        return 10
    try:
        value = int(raw)
    except ValueError:
        return 10
    return max(5, min(50, value))


MENU_DISPLAY_COUNT = _parse_menu_display_count()
THUMBNAIL_SIZE = (32, 32)  # pixels, for menu icon display
REDACT_SENSITIVE = True  # mask sensitive data in preview (API keys, passwords, etc.)
