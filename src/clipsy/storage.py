import sqlite3
from datetime import datetime
from pathlib import Path

from clipsy.config import DB_PATH, MAX_ENTRIES
from clipsy.models import ClipboardEntry, ContentType


SCHEMA = """
CREATE TABLE IF NOT EXISTS clipboard_entries (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    content_type   TEXT NOT NULL CHECK(content_type IN ('text', 'image', 'file')),
    text_content   TEXT,
    image_path     TEXT,
    preview        TEXT NOT NULL,
    content_hash   TEXT NOT NULL,
    byte_size      INTEGER NOT NULL DEFAULT 0,
    created_at     TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%S', 'now', 'localtime')),
    pinned         INTEGER NOT NULL DEFAULT 0,
    source_app     TEXT,
    thumbnail_path TEXT,
    is_sensitive   INTEGER NOT NULL DEFAULT 0,
    masked_preview TEXT,
    rtf_data       BLOB,
    html_data      BLOB
);

CREATE INDEX IF NOT EXISTS idx_created_at ON clipboard_entries(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_content_hash ON clipboard_entries(content_hash);
CREATE INDEX IF NOT EXISTS idx_content_type ON clipboard_entries(content_type);

CREATE VIRTUAL TABLE IF NOT EXISTS clipboard_fts USING fts5(
    preview,
    text_content,
    content='clipboard_entries',
    content_rowid='id'
);

CREATE TRIGGER IF NOT EXISTS clipboard_ai AFTER INSERT ON clipboard_entries BEGIN
    INSERT INTO clipboard_fts(rowid, preview, text_content)
    VALUES (new.id, new.preview, new.text_content);
END;

CREATE TRIGGER IF NOT EXISTS clipboard_ad AFTER DELETE ON clipboard_entries BEGIN
    INSERT INTO clipboard_fts(clipboard_fts, rowid, preview, text_content)
    VALUES ('delete', old.id, old.preview, old.text_content);
END;
"""


class StorageManager:
    def __init__(self, db_path: str | Path | None = None):
        self._db_path = str(db_path) if db_path else str(DB_PATH)
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self.init_db()

    def init_db(self) -> None:
        self._conn.executescript(SCHEMA)
        self._migrate_schema()
        self._conn.commit()

    def _migrate_schema(self) -> None:
        """Add new columns to existing databases."""
        cursor = self._conn.execute("PRAGMA table_info(clipboard_entries)")
        columns = {row[1] for row in cursor.fetchall()}
        if "thumbnail_path" not in columns:
            self._conn.execute("ALTER TABLE clipboard_entries ADD COLUMN thumbnail_path TEXT")
        if "is_sensitive" not in columns:
            self._conn.execute("ALTER TABLE clipboard_entries ADD COLUMN is_sensitive INTEGER NOT NULL DEFAULT 0")
        if "masked_preview" not in columns:
            self._conn.execute("ALTER TABLE clipboard_entries ADD COLUMN masked_preview TEXT")
        if "rtf_data" not in columns:
            self._conn.execute("ALTER TABLE clipboard_entries ADD COLUMN rtf_data BLOB")
        if "html_data" not in columns:
            self._conn.execute("ALTER TABLE clipboard_entries ADD COLUMN html_data BLOB")

    @staticmethod
    def _delete_files(image_path: str | None, thumbnail_path: str | None) -> None:
        for file_path in (image_path, thumbnail_path):
            if file_path:
                p = Path(file_path)
                if p.exists():
                    p.unlink()

    def add_entry(self, entry: ClipboardEntry) -> int:
        cursor = self._conn.execute(
            """INSERT INTO clipboard_entries
               (content_type, text_content, image_path, preview, content_hash, byte_size, created_at, pinned, source_app, thumbnail_path, is_sensitive, masked_preview, rtf_data, html_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                entry.content_type.value,
                entry.text_content,
                entry.image_path,
                entry.preview,
                entry.content_hash,
                entry.byte_size,
                entry.created_at.isoformat(),
                int(entry.pinned),
                entry.source_app,
                entry.thumbnail_path,
                int(entry.is_sensitive),
                entry.masked_preview,
                entry.rtf_data,
                entry.html_data,
            ),
        )
        self._conn.commit()
        return cursor.lastrowid

    def get_recent(self, limit: int = 25) -> list[ClipboardEntry]:
        rows = self._conn.execute(
            "SELECT * FROM clipboard_entries ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def search(self, query: str, limit: int = 25) -> list[ClipboardEntry]:
        sanitized = self._sanitize_fts_query(query)
        if not sanitized:
            return []
        rows = self._conn.execute(
            """SELECT e.* FROM clipboard_entries e
               JOIN clipboard_fts f ON e.id = f.rowid
               WHERE clipboard_fts MATCH ?
               ORDER BY e.created_at DESC
               LIMIT ?""",
            (sanitized, limit),
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def get_entry(self, entry_id: int) -> ClipboardEntry | None:
        row = self._conn.execute(
            "SELECT * FROM clipboard_entries WHERE id = ?", (entry_id,)
        ).fetchone()
        return self._row_to_entry(row) if row else None

    def delete_entry(self, entry_id: int) -> None:
        entry = self.get_entry(entry_id)
        if entry:
            self._delete_files(entry.image_path, entry.thumbnail_path)
        self._conn.execute("DELETE FROM clipboard_entries WHERE id = ?", (entry_id,))
        self._conn.commit()

    def find_by_hash(self, content_hash: str) -> ClipboardEntry | None:
        row = self._conn.execute(
            "SELECT * FROM clipboard_entries WHERE content_hash = ? ORDER BY created_at DESC LIMIT 1",
            (content_hash,),
        ).fetchone()
        return self._row_to_entry(row) if row else None

    def update_timestamp(self, entry_id: int) -> None:
        now = datetime.now().isoformat()
        self._conn.execute(
            "UPDATE clipboard_entries SET created_at = ? WHERE id = ?",
            (now, entry_id),
        )
        self._conn.commit()

    def update_thumbnail_path(self, entry_id: int, thumbnail_path: str) -> None:
        self._conn.execute(
            "UPDATE clipboard_entries SET thumbnail_path = ? WHERE id = ?",
            (thumbnail_path, entry_id),
        )
        self._conn.commit()

    def purge_old(self, keep_count: int | None = None) -> int:
        keep = keep_count if keep_count is not None else MAX_ENTRIES
        rows = self._conn.execute(
            """SELECT id, image_path, thumbnail_path FROM clipboard_entries
               WHERE pinned = 0
               ORDER BY created_at DESC
               LIMIT -1 OFFSET ?""",
            (keep,),
        ).fetchall()

        deleted = 0
        for row in rows:
            self._delete_files(row["image_path"], row["thumbnail_path"])
            self._conn.execute("DELETE FROM clipboard_entries WHERE id = ?", (row["id"],))
            deleted += 1

        if deleted:
            self._conn.commit()
        return deleted

    def toggle_pin(self, entry_id: int) -> bool:
        entry = self.get_entry(entry_id)
        if not entry:
            return False
        new_pinned = not entry.pinned
        self._conn.execute(
            "UPDATE clipboard_entries SET pinned = ? WHERE id = ?",
            (int(new_pinned), entry_id),
        )
        self._conn.commit()
        return new_pinned

    def clear_all(self) -> None:
        rows = self._conn.execute(
            "SELECT image_path, thumbnail_path FROM clipboard_entries WHERE image_path IS NOT NULL OR thumbnail_path IS NOT NULL"
        ).fetchall()
        for row in rows:
            self._delete_files(row["image_path"], row["thumbnail_path"])
        self._conn.execute("DELETE FROM clipboard_entries")
        self._conn.commit()

    def count(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM clipboard_entries").fetchone()
        return row["cnt"]

    def get_pinned(self) -> list[ClipboardEntry]:
        rows = self._conn.execute(
            "SELECT * FROM clipboard_entries WHERE pinned = 1 ORDER BY created_at DESC"
        ).fetchall()
        return [self._row_to_entry(r) for r in rows]

    def count_pinned(self) -> int:
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM clipboard_entries WHERE pinned = 1").fetchone()
        return row["cnt"]

    def close(self) -> None:
        self._conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    @staticmethod
    def _sanitize_fts_query(query: str) -> str:
        # Quote each token to prevent FTS5 syntax errors from special chars
        tokens = query.split()
        if not tokens:
            return ""
        quoted = ['"' + token.replace('"', '""') + '"' for token in tokens]
        return " ".join(quoted)

    def _row_to_entry(self, row: sqlite3.Row) -> ClipboardEntry:
        # Handle columns which may not exist in older databases
        keys = row.keys()
        thumbnail_path = row["thumbnail_path"] if "thumbnail_path" in keys else None
        is_sensitive = bool(row["is_sensitive"]) if "is_sensitive" in keys else False
        masked_preview = row["masked_preview"] if "masked_preview" in keys else None
        rtf_data = bytes(row["rtf_data"]) if "rtf_data" in keys and row["rtf_data"] is not None else None
        html_data = bytes(row["html_data"]) if "html_data" in keys and row["html_data"] is not None else None
        return ClipboardEntry(
            id=row["id"],
            content_type=ContentType(row["content_type"]),
            text_content=row["text_content"],
            image_path=row["image_path"],
            preview=row["preview"],
            content_hash=row["content_hash"],
            byte_size=row["byte_size"],
            created_at=datetime.fromisoformat(row["created_at"]),
            pinned=bool(row["pinned"]),
            source_app=row["source_app"],
            thumbnail_path=thumbnail_path,
            is_sensitive=is_sensitive,
            masked_preview=masked_preview,
            rtf_data=rtf_data,
            html_data=html_data,
        )
