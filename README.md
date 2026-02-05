# Clipsy

[![CI](https://github.com/brencon/clipsy/actions/workflows/ci.yml/badge.svg)](https://github.com/brencon/clipsy/actions/workflows/ci.yml)
[![Release](https://img.shields.io/github/v/release/brencon/clipsy)](https://github.com/brencon/clipsy/releases)
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
- **Click to re-copy** — Click any entry in the menu to put it back on your clipboard
- **Deduplication** — Copying the same content twice bumps it to the top instead of creating a duplicate
- **Auto-purge** — Keeps the most recent 500 entries, automatically cleans up old ones
- **Persistent storage** — History survives app restarts (SQLite database)
- **Corporate IT friendly** — Runs as a plain Python process, no `.app` bundle or Gatekeeper issues

## Requirements

- macOS
- Python 3.10+ (Homebrew recommended: `brew install python3`)

## Installation

```bash
# Clone the repo
git clone https://github.com/brencon/clipsy.git
cd clipsy

# Create virtual environment and install
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Usage

```bash
# Run clipsy (a scissors icon appears in your menu bar)
.venv/bin/python -m clipsy
```

Then just use your Mac normally. Every time you copy something, it shows up in the Clipsy menu:

```
[✂️ Icon]
├── Clipsy - Clipboard History
├── ──────────────────
├── Search...
├── ──────────────────
├── "Meeting notes for Q3 plan..."
├── "https://github.com/example..."
├── 🔒 "password=••••••••"
├── [thumbnail] "[Image: 1920x1080]"
├── ... (up to 10 items)
├── ──────────────────
├── Clear History
├── Support Clipsy
├── ──────────────────
└── Quit Clipsy
```

## Auto-Start on Login

Run clipsy automatically when you log in — no terminal needed:

```bash
# Install as a LaunchAgent
scripts/install_launchagent.sh install

# Check status
scripts/install_launchagent.sh status

# Remove auto-start
scripts/install_launchagent.sh uninstall
```

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

Only one external dependency:

- **`rumps`** — macOS menu bar app framework (brings `pyobjc-framework-Cocoa` transitively)
- **`sqlite3`** — Built into Python

## License

MIT License — see [LICENSE](LICENSE) for details.
