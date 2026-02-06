import logging
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

import rumps

from clipsy import __version__
from clipsy.config import DB_PATH, IMAGE_DIR, MAX_PINNED_ENTRIES, MENU_DISPLAY_COUNT, POLL_INTERVAL, REDACT_SENSITIVE, THUMBNAIL_SIZE
from clipsy.models import ClipboardEntry, ContentType
from clipsy.monitor import ClipboardMonitor
from clipsy.storage import StorageManager
from clipsy.utils import create_thumbnail, ensure_dirs

logger = logging.getLogger(__name__)

ENTRY_KEY_PREFIX = "clipsy_entry_"


@dataclass
class MenuItemSpec:
    """Specification for a menu item, separating logic from rumps rendering."""

    title: str
    callback: Callable | None = None
    icon: str | None = None
    dimensions: tuple[int, int] | None = None
    template: bool | None = None
    entry_id: int | None = None
    is_submenu: bool = False
    children: list["MenuItemSpec"] | None = None


class ClipsyApp(rumps.App):
    def __init__(self):
        super().__init__("Clipsy", title="✂️", quit_button=None)
        self._init_app()

    def _init_app(self) -> None:
        """Initialize app components. Separated for testability."""
        ensure_dirs()
        self._storage = StorageManager(DB_PATH)
        self._monitor = ClipboardMonitor(self._storage, on_change=self._refresh_menu)
        self._entry_ids: dict[str, int] = {}
        self._build_menu()

    def _build_menu(self) -> None:
        """Build the menu from computed specifications."""
        self.menu.clear()
        self._entry_ids.clear()
        specs = self._compute_menu_specs()
        self._render_menu_specs(specs)

    def _compute_menu_specs(self) -> list[MenuItemSpec | None]:
        """Compute menu item specifications. Pure logic, no rumps dependency."""
        specs: list[MenuItemSpec | None] = [
            MenuItemSpec(f"Clipsy v{__version__} - Clipboard History"),
            None,  # separator
            MenuItemSpec("Search...", callback=self._on_search),
            None,  # separator
        ]

        pinned_entries = self._storage.get_pinned()
        if pinned_entries:
            pinned_children = [self._compute_entry_spec(e) for e in pinned_entries]
            pinned_children.append(None)  # separator
            pinned_children.append(MenuItemSpec("Clear Pinned", callback=self._on_clear_pinned))
            specs.append(MenuItemSpec("📌 Pinned", is_submenu=True, children=pinned_children))
            specs.append(None)  # separator

        entries = self._storage.get_recent(limit=MENU_DISPLAY_COUNT)
        entries = [e for e in entries if not e.pinned]

        if not entries and not pinned_entries:
            specs.append(MenuItemSpec("(No clipboard history)"))
        else:
            for entry in entries:
                specs.append(self._compute_entry_spec(entry))

        specs.extend([
            None,  # separator
            MenuItemSpec("Clear History", callback=self._on_clear),
            None,  # separator
            MenuItemSpec("Support Clipsy", callback=self._on_support),
            None,  # separator
            MenuItemSpec("Quit Clipsy", callback=self._on_quit),
        ])

        return specs

    def _compute_entry_spec(self, entry: ClipboardEntry) -> MenuItemSpec:
        """Compute menu item spec for a clipboard entry."""
        key = f"{ENTRY_KEY_PREFIX}{entry.id}"
        self._entry_ids[key] = entry.id
        display_text = self._get_display_preview(entry)

        spec = MenuItemSpec(
            title=display_text,
            callback=self._on_entry_click,
            entry_id=entry.id,
        )

        if entry.content_type == ContentType.IMAGE:
            thumb_path = self._ensure_thumbnail(entry)
            if thumb_path:
                spec.icon = thumb_path
                spec.dimensions = (32, 32)
                spec.template = False

        return spec

    def _render_menu_specs(self, specs: list[MenuItemSpec | None]) -> None:
        """Render menu item specifications to actual rumps MenuItems."""
        items = []
        for spec in specs:
            items.append(self._render_single_spec(spec))
        self.menu = items

    def _render_single_spec(self, spec: MenuItemSpec | None) -> rumps.MenuItem | None:
        """Render a single menu item specification."""
        if spec is None:
            return None

        if spec.is_submenu and spec.children:
            submenu = rumps.MenuItem(spec.title)
            for child in spec.children:
                child_item = self._render_single_spec(child)
                if child_item is None:
                    submenu.add(None)
                else:
                    submenu.add(child_item)
            return submenu

        kwargs = {"callback": spec.callback}
        if spec.icon:
            kwargs["icon"] = spec.icon
        if spec.dimensions:
            kwargs["dimensions"] = spec.dimensions
        if spec.template is not None:
            kwargs["template"] = spec.template

        item = rumps.MenuItem(spec.title, **kwargs)

        if spec.entry_id is not None:
            item._id = f"{ENTRY_KEY_PREFIX}{spec.entry_id}"

        return item

    def _get_display_preview(self, entry: ClipboardEntry) -> str:
        """Get the display preview for an entry, masking sensitive data if enabled."""
        if REDACT_SENSITIVE and entry.is_sensitive and entry.masked_preview:
            return f"🔒 {entry.masked_preview}"
        return entry.preview

    def _ensure_thumbnail(self, entry: ClipboardEntry) -> str | None:
        """Ensure a thumbnail exists for an image entry, generating if needed."""
        if entry.thumbnail_path:
            return entry.thumbnail_path

        if not entry.image_path:
            return None

        image_path = Path(entry.image_path)
        if not image_path.exists():
            return None

        thumb_filename = image_path.stem + "_thumb.png"
        thumb_path = IMAGE_DIR / thumb_filename

        if thumb_path.exists() or create_thumbnail(str(image_path), str(thumb_path), THUMBNAIL_SIZE):
            self._storage.update_thumbnail_path(entry.id, str(thumb_path))
            return str(thumb_path)

        return None

    def _refresh_menu(self) -> None:
        self._build_menu()

    @rumps.timer(POLL_INTERVAL)
    def _poll_clipboard(self, _sender) -> None:
        self._monitor.check_clipboard()

    def _on_entry_click(self, sender) -> None:
        entry_id = self._entry_ids.get(getattr(sender, "_id", ""))
        if entry_id is None:
            return

        entry = self._storage.get_entry(entry_id)
        if entry is None:
            return

        # Check if Option key is held (for pin toggle)
        try:
            from AppKit import NSAlternateKeyMask, NSEvent

            modifier_flags = NSEvent.modifierFlags()
            if modifier_flags & NSAlternateKeyMask:
                self._on_pin_toggle(entry)
                return
        except Exception:
            pass  # If we can't check modifiers, proceed with normal copy

        try:
            from AppKit import NSPasteboard, NSPasteboardTypePNG, NSPasteboardTypeString
            from Foundation import NSData

            pb = NSPasteboard.generalPasteboard()

            copied = False

            if entry.content_type == ContentType.TEXT and entry.text_content:
                pb.clearContents()
                pb.setString_forType_(entry.text_content, NSPasteboardTypeString)
                if entry.rtf_data:
                    rtf_ns_data = NSData.dataWithBytes_length_(entry.rtf_data, len(entry.rtf_data))
                    if rtf_ns_data:
                        pb.setData_forType_(rtf_ns_data, "public.rtf")
                if entry.html_data:
                    html_ns_data = NSData.dataWithBytes_length_(entry.html_data, len(entry.html_data))
                    if html_ns_data:
                        pb.setData_forType_(html_ns_data, "public.html")
                self._monitor.sync_change_count()
                copied = True

            elif entry.content_type == ContentType.IMAGE and entry.image_path:
                img_data = NSData.dataWithContentsOfFile_(entry.image_path)
                if img_data:
                    pb.clearContents()
                    pb.setData_forType_(img_data, NSPasteboardTypePNG)
                    self._monitor.sync_change_count()
                    copied = True

            elif entry.content_type == ContentType.FILE and entry.text_content:
                pb.clearContents()
                pb.setString_forType_(entry.text_content, NSPasteboardTypeString)
                self._monitor.sync_change_count()
                copied = True

            if copied:
                self._storage.update_timestamp(entry_id)
                self._refresh_menu()
                rumps.notification("Clipsy", "", "Copied to clipboard", sound=False)
        except Exception:
            logger.exception("Error copying entry to clipboard")

    def _on_pin_toggle(self, entry: ClipboardEntry) -> None:
        """Toggle pin status for an entry."""
        if entry.pinned:
            self._storage.toggle_pin(entry.id)
            rumps.notification("Clipsy", "", "Unpinned", sound=False)
        else:
            if entry.is_sensitive:
                rumps.notification("Clipsy", "", "Cannot pin sensitive data", sound=False)
                return

            if self._storage.count_pinned() >= MAX_PINNED_ENTRIES:
                rumps.notification("Clipsy", "", f"Maximum {MAX_PINNED_ENTRIES} pinned items", sound=False)
                return

            self._storage.toggle_pin(entry.id)
            rumps.notification("Clipsy", "", "Pinned", sound=False)

        self._refresh_menu()

    def _on_clear_pinned(self, _sender) -> None:
        """Clear all pinned entries."""
        self._storage.clear_pinned()
        self._refresh_menu()

    def _on_search(self, _sender) -> None:
        response = rumps.Window(
            message="Search clipboard history:",
            title="Clipsy Search",
            default_text="",
            ok="Search",
            cancel="Cancel",
            dimensions=(300, 24),
        ).run()

        if response.clicked and response.text.strip():
            query = response.text.strip()
            results = self._storage.search(query, limit=MENU_DISPLAY_COUNT)

            if not results:
                rumps.alert("Clipsy Search", f'No results for "{query}"')
                return

            self._entry_ids.clear()
            specs = self._compute_search_results_specs(query, results)
            self.menu.clear()
            self._render_menu_specs(specs)

    def _compute_search_results_specs(self, query: str, results: list[ClipboardEntry]) -> list[MenuItemSpec | None]:
        """Compute menu specs for search results."""
        specs: list[MenuItemSpec | None] = [
            MenuItemSpec(f'Search: "{query}" ({len(results)} results)'),
            None,
            MenuItemSpec("Show All", callback=lambda _: self._refresh_menu()),
            None,
        ]

        for entry in results:
            specs.append(self._compute_entry_spec(entry))

        specs.extend([
            None,
            MenuItemSpec("Quit Clipsy", callback=self._on_quit),
        ])

        return specs

    def _on_clear(self, _sender) -> None:
        if rumps.alert("Clipsy", "Clear all clipboard history?", ok="Clear", cancel="Cancel"):
            self._storage.clear_all()
            self._refresh_menu()

    def _on_support(self, _sender) -> None:
        webbrowser.open("https://github.com/sponsors/brencon")

    def _on_quit(self, _sender) -> None:
        self._storage.close()
        rumps.quit_application()
