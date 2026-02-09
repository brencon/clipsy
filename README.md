# Clipsy

[![PyPI](https://img.shields.io/pypi/v/clipsy)](https://pypi.org/project/clipsy/)
[![CI](https://github.com/brencon/clipsy/actions/workflows/ci.yml/badge.svg)](https://github.com/brencon/clipsy/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/brencon/clipsy/branch/main/graph/badge.svg)](https://codecov.io/gh/brencon/clipsy)
![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Platform: macOS](https://img.shields.io/badge/platform-macOS-lightgrey.svg)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A lightweight clipboard history manager for macOS. Runs as a menu bar icon — no admin privileges, no code signing, no App Store required.

## Features

- **Clipboard history** — Automatically captures text, images, and file copies
- **Image thumbnails** — Visual previews for copied images in the menu
- **Sensitive data masking** — Auto-detects API keys, passwords, SSNs, credit cards, private keys, and tokens; displays masked previews with 🔒 icon
- **Search** — Full-text search across all clipboard entries (SQLite FTS5)
- **Rich text preservation** — Preserves RTF and HTML formatting when re-copying from history (e.g., bold, italic, links from web pages)
- **Pin favorites** — Option-click to pin up to 5 frequently-used snippets (sensitive data cannot be pinned)
- **Auto-paste** — Click any entry and it pastes directly where your cursor was (toggle on/off from the menu; requires macOS Accessibility permission)
- **Deduplication** — Copying the same content twice bumps it to the top instead of creating a duplicate
- **Auto-purge** — Keeps the most recent 500 entries, automatically cleans up old ones
- **Persistent storage** — History survives app restarts (SQLite database)
- **Corporate IT friendly** — Runs as a plain Python process, no `.app` bundle or Gatekeeper issues

## Requirements

- macOS
- Python 3.10+ (Homebrew recommended: `brew install python3`)

## Installation

### Via Homebrew (recommended)

```bash
brew install brencon/clipsy/clipsy
clipsy
```

### Via pipx

```bash
brew install pipx
pipx install clipsy
clipsy
```

### Via pip

```bash
pip install clipsy
clipsy
```

### From source

```bash
git clone https://github.com/brencon/clipsy.git
cd clipsy
python3 -m venv .venv
.venv/bin/pip install -e .
.venv/bin/clipsy
```

## Usage

After running `clipsy`, the app installs as a background service and starts automatically on login. A scissors icon (✂️) appears in your menu bar.

Then just use your Mac normally. Every time you copy something, it shows up in the Clipsy menu:

```
[✂️ Icon]
├── Clipsy - Clipboard History
├── ──────────────────
├── Search...
├── ──────────────────
├── 📌 Pinned ►
│   ├── "my-api-endpoint.com/v1..."
│   ├── "SELECT * FROM users..."
│   ├── ──────────────────
│   └── Clear Pinned
├── ──────────────────
├── "Meeting notes for Q3 plan..."
├── "https://github.com/example..."
├── 🔒 "password=••••••••"
├── [thumbnail] "[Image: 1920x1080]"
├── ... (up to 10 items, configurable)
├── ──────────────────
├── Auto-Paste: On
├── ──────────────────
├── Clear History
├── ──────────────────
├── Support Clipsy
├── ──────────────────
└── Quit Clipsy
```

**Tip:** Hold **Option (⌥)** while clicking an entry to pin/unpin it.

## Commands

```bash
clipsy            # Install and start as background service (default)
clipsy status     # Check if running
clipsy uninstall  # Remove from login items
clipsy run        # Run in foreground (for debugging)
```

## Configuration

| Variable | Default | Range | Description |
|----------|---------|-------|-------------|
| `CLIPSY_MENU_DISPLAY_COUNT` | `10` | 5–50 | Number of entries shown in the menu |
| `CLIPSY_AUTO_PASTE` | `true` | `true`/`false` | Auto-paste on click (requires Accessibility permission) |

```bash
# Example: show 20 entries in the menu
export CLIPSY_MENU_DISPLAY_COUNT=20

# Disable auto-paste (click copies to clipboard only)
export CLIPSY_AUTO_PASTE=false
```

### Auto-Paste

When Auto-Paste is enabled (the default), clicking a Clipsy entry copies it to the clipboard **and** pastes it directly where your cursor was — no need to Cmd+V manually. You can toggle this on/off from the menu.

Auto-Paste requires **macOS Accessibility permission**. The first time it fires, macOS will prompt you to grant access to the app running Clipsy (e.g., Terminal, VS Code, or iTerm). Grant it in **System Settings > Privacy & Security > Accessibility**. If permission is not granted, Clipsy falls back to copy-only behavior silently.

## Data Storage

All data is stored in `~/.local/share/clipsy/`:

| File | Purpose |
|------|---------|
| `clipsy.db` | SQLite database with clipboard entries |
| `images/` | Saved clipboard images (PNG files) |
| `clipsy.log` | Application log |

## Development

```bash
# Install with dev dependencies
.venv/bin/pip install -e ".[dev]"

# Run tests
.venv/bin/python -m pytest tests/ -v

# Run with coverage
.venv/bin/python -m pytest tests/ --cov=clipsy --cov-report=term-missing
```

## Architecture

```
NSPasteboard → monitor.py → redact.py → storage.py (SQLite) → app.py (menu bar UI)
```

- **`app.py`** — `rumps.App` subclass; renders the menu bar dropdown, handles clicks and search
- **`monitor.py`** — Polls `NSPasteboard.changeCount()` every 0.5s; detects text, images, and file copies
- **`storage.py`** — SQLite with FTS5 full-text search, SHA-256 deduplication, auto-purge
- **`redact.py`** — Sensitive data detection and masking (API keys, passwords, SSN, credit cards, tokens)
- **`config.py`** — Constants, paths, limits
- **`models.py`** — `ClipboardEntry` dataclass, `ContentType` enum
- **`utils.py`** — Hashing, text truncation, PNG dimension parsing, thumbnail generation

### Dependencies

- **`rumps`** — macOS menu bar app framework (brings `pyobjc-framework-Cocoa` transitively)
- **`pyobjc-framework-Quartz`** — Keyboard event simulation for auto-paste
- **`sqlite3`** — Built into Python

## License

MIT License — see [LICENSE](LICENSE) for details.
