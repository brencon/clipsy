import logging
import sys

from clipsy.config import LOG_PATH
from clipsy.utils import ensure_dirs


def main():
    ensure_dirs()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(LOG_PATH),
            logging.StreamHandler(sys.stderr),
        ],
    )

    from clipsy.app import ClipsyApp
    app = ClipsyApp()
    app.run()


if __name__ == "__main__":
    main()
