import argparse
import logging
import os
import subprocess
import sys
from pathlib import Path

from clipsy.config import LOG_PATH
from clipsy.utils import ensure_dirs

PLIST_NAME = "com.clipsy.app.plist"
LAUNCHAGENT_DIR = Path.home() / "Library" / "LaunchAgents"
PLIST_PATH = LAUNCHAGENT_DIR / PLIST_NAME


def get_clipsy_path() -> str:
    """Get the path to the clipsy executable."""
    import shutil

    # Check if we're running from an installed location
    clipsy_path = shutil.which("clipsy")
    if clipsy_path:
        return clipsy_path
    # Fallback to current Python module
    return f"{sys.executable} -m clipsy"


def create_plist(clipsy_path: str) -> str:
    """Generate the LaunchAgent plist content."""
    data_dir = Path.home() / ".local" / "share" / "clipsy"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.clipsy.app</string>
    <key>ProgramArguments</key>
    <array>
        <string>{clipsy_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>{data_dir}/clipsy.log</string>
    <key>StandardErrorPath</key>
    <string>{data_dir}/clipsy.log</string>
</dict>
</plist>
"""


def install_launchagent() -> int:
    """Install and start the LaunchAgent."""
    ensure_dirs()

    clipsy_path = get_clipsy_path()
    print(f"Installing LaunchAgent for: {clipsy_path}")

    # Create LaunchAgents directory if needed
    LAUNCHAGENT_DIR.mkdir(parents=True, exist_ok=True)

    # Unload existing if present
    if PLIST_PATH.exists():
        subprocess.run(
            ["launchctl", "unload", str(PLIST_PATH)],
            capture_output=True,
        )

    # Write plist
    PLIST_PATH.write_text(create_plist(clipsy_path))
    print(f"Created: {PLIST_PATH}")

    # Load the agent
    result = subprocess.run(
        ["launchctl", "load", str(PLIST_PATH)],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("Clipsy is now running in the background.")
        print("It will start automatically on login.")
        return 0
    else:
        print(f"Failed to load LaunchAgent: {result.stderr}")
        return 1


def uninstall_launchagent() -> int:
    """Stop and remove the LaunchAgent."""
    if not PLIST_PATH.exists():
        print("LaunchAgent not installed.")
        return 0

    # Unload
    subprocess.run(
        ["launchctl", "unload", str(PLIST_PATH)],
        capture_output=True,
    )

    # Remove plist
    PLIST_PATH.unlink()
    print("LaunchAgent uninstalled.")
    print("Clipsy will no longer start on login.")
    return 0


def check_status() -> int:
    """Check if Clipsy is running."""
    result = subprocess.run(
        ["launchctl", "list", "com.clipsy.app"],
        capture_output=True,
        text=True,
    )

    if result.returncode == 0:
        print("Clipsy is running.")
        if PLIST_PATH.exists():
            print(f"LaunchAgent: {PLIST_PATH}")
        return 0
    else:
        print("Clipsy is not running.")
        if PLIST_PATH.exists():
            print(f"LaunchAgent installed but not loaded: {PLIST_PATH}")
        else:
            print("LaunchAgent not installed. Run: clipsy install")
        return 1


def run_app():
    """Run the Clipsy application."""
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


def main():
    parser = argparse.ArgumentParser(
        description="Clipsy - Clipboard history manager for macOS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  (none)      Run Clipsy in foreground
  install     Install as LaunchAgent (runs on login)
  uninstall   Remove LaunchAgent
  status      Check if Clipsy is running

Examples:
  clipsy install    # Install and start as background service
  clipsy status     # Check if running
  clipsy uninstall  # Stop and remove from login items
""",
    )
    parser.add_argument(
        "command",
        nargs="?",
        choices=["install", "uninstall", "status"],
        help="Command to run",
    )

    args = parser.parse_args()

    if args.command == "install":
        sys.exit(install_launchagent())
    elif args.command == "uninstall":
        sys.exit(uninstall_launchagent())
    elif args.command == "status":
        sys.exit(check_status())
    else:
        run_app()


if __name__ == "__main__":
    main()
