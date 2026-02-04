#!/usr/bin/env bash
set -euo pipefail

LABEL="com.clipsy.agent"
PLIST_PATH="$HOME/Library/LaunchAgents/${LABEL}.plist"
PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
VENV_PYTHON="${PROJECT_DIR}/.venv/bin/python"
DATA_DIR="$HOME/.local/share/clipsy"

if [ ! -f "$VENV_PYTHON" ]; then
    echo "Error: Virtual environment not found at ${VENV_PYTHON}"
    echo "Run: python3 -m venv .venv && .venv/bin/pip install -e ."
    exit 1
fi

case "${1:-install}" in
    install)
        mkdir -p "$HOME/Library/LaunchAgents"
        mkdir -p "$DATA_DIR"

        cat > "$PLIST_PATH" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>${LABEL}</string>
    <key>ProgramArguments</key>
    <array>
        <string>${VENV_PYTHON}</string>
        <string>-m</string>
        <string>clipsy</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
    <key>StandardOutPath</key>
    <string>${DATA_DIR}/clipsy.log</string>
    <key>StandardErrorPath</key>
    <string>${DATA_DIR}/clipsy.log</string>
</dict>
</plist>
PLIST

        launchctl load "$PLIST_PATH"
        echo "Clipsy LaunchAgent installed and loaded."
        echo "It will start automatically on login."
        echo "Plist: $PLIST_PATH"
        ;;

    uninstall)
        if [ -f "$PLIST_PATH" ]; then
            launchctl unload "$PLIST_PATH" 2>/dev/null || true
            rm "$PLIST_PATH"
            echo "Clipsy LaunchAgent uninstalled."
        else
            echo "LaunchAgent not found at $PLIST_PATH"
        fi
        ;;

    status)
        if launchctl list | grep -q "$LABEL"; then
            echo "Clipsy is loaded."
            launchctl list "$LABEL"
        else
            echo "Clipsy is not loaded."
        fi
        ;;

    *)
        echo "Usage: $0 {install|uninstall|status}"
        exit 1
        ;;
esac
