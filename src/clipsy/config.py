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
MENU_DISPLAY_COUNT = 10  # items shown in dropdown
THUMBNAIL_SIZE = (32, 32)  # pixels, for menu icon display
