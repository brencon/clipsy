#!/bin/bash
PLIST="$HOME/Library/LaunchAgents/com.clipsy.agent.plist"

if [ ! -f "$PLIST" ]; then
    echo "LaunchAgent not installed. Run scripts/install_launchagent.sh first."
    exit 1
fi

launchctl unload "$PLIST" 2>/dev/null
launchctl load "$PLIST"
echo "Clipsy restarted."
