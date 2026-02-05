class TestAddAndRetrieve:
    def test_add_entry(self, storage, make_entry):
        entry = make_entry("test text")
        entry_id = storage.add_entry(entry)
        assert entry_id is not None
        assert entry_id > 0

    def test_get_recent(self, storage, make_entry):
        storage.add_entry(make_entry("first"))
        storage.add_entry(make_entry("second", content_hash="hash_second"))
        entries = storage.get_recent()
        assert len(entries) == 2
        assert entries[0].text_content == "second"
        assert entries[1].text_content == "first"

    def test_get_recent_limit(self, storage, make_entry):
        for i in range(10):
            storage.add_entry(make_entry(f"item {i}", content_hash=f"hash_{i}"))
        entries = storage.get_recent(limit=3)
        assert len(entries) == 3

    def test_get_entry_by_id(self, storage, make_entry):
        entry_id = storage.add_entry(make_entry("find me"))
        found = storage.get_entry(entry_id)
        assert found is not None
        assert found.text_content == "find me"

    def test_get_entry_not_found(self, storage):
        assert storage.get_entry(99999) is None


class TestDeduplication:
    def test_find_by_hash(self, storage, make_entry):
        storage.add_entry(make_entry("dup test", content_hash="unique_hash"))
        found = storage.find_by_hash("unique_hash")
        assert found is not None
        assert found.text_content == "dup test"

    def test_find_by_hash_not_found(self, storage):
        assert storage.find_by_hash("nonexistent") is None

    def test_update_timestamp(self, storage, make_entry):
        entry_id = storage.add_entry(make_entry("old"))
        old_entry = storage.get_entry(entry_id)
        storage.update_timestamp(entry_id)
        new_entry = storage.get_entry(entry_id)
        assert new_entry.created_at >= old_entry.created_at

    def test_update_thumbnail_path(self, storage, make_entry):
        from clipsy.models import ContentType

        entry = make_entry("img", content_type=ContentType.IMAGE, thumbnail_path=None)
        entry_id = storage.add_entry(entry)
        storage.update_thumbnail_path(entry_id, "/new/thumb.png")
        updated = storage.get_entry(entry_id)
        assert updated.thumbnail_path == "/new/thumb.png"


class TestSearch:
    def test_search_text(self, storage, make_entry):
        storage.add_entry(make_entry("python programming"))
        storage.add_entry(make_entry("javascript coding", content_hash="hash_js"))
        results = storage.search("python")
        assert len(results) == 1
        assert results[0].text_content == "python programming"

    def test_search_no_results(self, storage, make_entry):
        storage.add_entry(make_entry("hello world"))
        results = storage.search("nonexistent")
        assert len(results) == 0

    def test_search_limit(self, storage, make_entry):
        for i in range(10):
            storage.add_entry(make_entry(f"match item {i}", content_hash=f"hash_{i}"))
        results = storage.search("match", limit=3)
        assert len(results) == 3

    def test_search_special_characters_no_crash(self, storage, make_entry):
        storage.add_entry(make_entry("hello world"))
        results = storage.search('test "quotes" AND OR NOT')
        assert isinstance(results, list)

    def test_search_asterisk_no_crash(self, storage, make_entry):
        storage.add_entry(make_entry("some text"))
        results = storage.search("*")
        assert isinstance(results, list)

    def test_search_parentheses_no_crash(self, storage, make_entry):
        storage.add_entry(make_entry("function(arg)"))
        results = storage.search("function(arg)")
        assert isinstance(results, list)

    def test_search_empty_query(self, storage, make_entry):
        storage.add_entry(make_entry("hello"))
        results = storage.search("")
        assert results == []

    def test_search_whitespace_only(self, storage, make_entry):
        storage.add_entry(make_entry("hello"))
        results = storage.search("   ")
        assert results == []


class TestDelete:
    def test_delete_entry(self, storage, make_entry):
        entry_id = storage.add_entry(make_entry("to delete"))
        storage.delete_entry(entry_id)
        assert storage.get_entry(entry_id) is None

    def test_clear_all(self, storage, make_entry):
        for i in range(5):
            storage.add_entry(make_entry(f"item {i}", content_hash=f"hash_{i}"))
        assert storage.count() == 5
        storage.clear_all()
        assert storage.count() == 0


class TestPurge:
    def test_purge_old_entries(self, storage, make_entry):
        for i in range(10):
            storage.add_entry(make_entry(f"item {i}", content_hash=f"hash_{i}"))
        deleted = storage.purge_old(keep_count=5)
        assert deleted == 5
        assert storage.count() == 5

    def test_purge_skips_pinned(self, storage, make_entry):
        for i in range(5):
            storage.add_entry(make_entry(f"item {i}", content_hash=f"hash_{i}"))
        storage.add_entry(make_entry("pinned item", content_hash="hash_pinned", pinned=True))

        deleted = storage.purge_old(keep_count=3)
        remaining = storage.get_recent(limit=100)
        pinned_entries = [e for e in remaining if e.pinned]
        assert len(pinned_entries) == 1
        assert pinned_entries[0].text_content == "pinned item"


class TestPin:
    def test_toggle_pin(self, storage, make_entry):
        entry_id = storage.add_entry(make_entry("pin me"))
        result = storage.toggle_pin(entry_id)
        assert result is True
        entry = storage.get_entry(entry_id)
        assert entry.pinned is True

    def test_toggle_pin_off(self, storage, make_entry):
        entry_id = storage.add_entry(make_entry("pin me", pinned=True))
        result = storage.toggle_pin(entry_id)
        assert result is False

    def test_toggle_pin_nonexistent(self, storage):
        result = storage.toggle_pin(99999)
        assert result is False


class TestCount:
    def test_empty_count(self, storage):
        assert storage.count() == 0

    def test_count_after_inserts(self, storage, make_entry):
        for i in range(3):
            storage.add_entry(make_entry(f"item {i}", content_hash=f"hash_{i}"))
        assert storage.count() == 3


class TestImageEntries:
    def test_add_image_entry_with_thumbnail(self, storage, make_entry):
        from clipsy.models import ContentType

        entry = make_entry(
            "img",
            content_type=ContentType.IMAGE,
            image_path="/tmp/test.png",
            thumbnail_path="/tmp/test_thumb.png",
        )
        entry_id = storage.add_entry(entry)
        retrieved = storage.get_entry(entry_id)
        assert retrieved.content_type == ContentType.IMAGE
        assert retrieved.image_path == "/tmp/test.png"
        assert retrieved.thumbnail_path == "/tmp/test_thumb.png"

    def test_add_image_entry_without_thumbnail(self, storage, make_entry):
        from clipsy.models import ContentType

        entry = make_entry(
            "img",
            content_type=ContentType.IMAGE,
            image_path="/tmp/test.png",
            thumbnail_path=None,
        )
        entry_id = storage.add_entry(entry)
        retrieved = storage.get_entry(entry_id)
        assert retrieved.thumbnail_path is None


class TestContextManager:
    def test_context_manager_usage(self):
        from clipsy.storage import StorageManager

        with StorageManager(db_path=":memory:") as mgr:
            assert mgr.count() == 0

    def test_context_manager_closes_on_exit(self):
        from clipsy.storage import StorageManager

        mgr = StorageManager(db_path=":memory:")
        mgr.__enter__()
        result = mgr.__exit__(None, None, None)
        assert result is False


class TestMigration:
    def test_migrate_adds_thumbnail_path_column(self, tmp_path):
        """Test that migration adds thumbnail_path to old databases."""
        import sqlite3
        from clipsy.storage import StorageManager

        # Create a minimal old-style database without thumbnail_path column
        db_file = tmp_path / "old_db.sqlite"
        conn = sqlite3.connect(str(db_file))
        conn.executescript("""
            CREATE TABLE clipboard_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,
                text_content TEXT,
                image_path TEXT,
                preview TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                byte_size INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                pinned INTEGER NOT NULL DEFAULT 0,
                source_app TEXT
            );
        """)
        conn.commit()
        conn.close()

        # Open with StorageManager which should run migration
        mgr = StorageManager(db_path=str(db_file))

        # Verify thumbnail_path column exists
        cursor = mgr._conn.execute("PRAGMA table_info(clipboard_entries)")
        columns = {row[1] for row in cursor.fetchall()}
        assert "thumbnail_path" in columns

        mgr.close()


class TestFileCleanup:
    def test_delete_entry_removes_image_file(self, storage, make_entry, tmp_path):
        from clipsy.models import ContentType

        # Create a real image file
        image_file = tmp_path / "test_image.png"
        image_file.write_bytes(b"fake png data")

        entry = make_entry(
            "img",
            content_type=ContentType.IMAGE,
            image_path=str(image_file),
            thumbnail_path=None,
        )
        entry_id = storage.add_entry(entry)

        assert image_file.exists()
        storage.delete_entry(entry_id)
        assert not image_file.exists()

    def test_delete_entry_removes_thumbnail_file(self, storage, make_entry, tmp_path):
        from clipsy.models import ContentType

        # Create real image and thumbnail files
        image_file = tmp_path / "test_image.png"
        thumb_file = tmp_path / "test_thumb.png"
        image_file.write_bytes(b"fake png data")
        thumb_file.write_bytes(b"fake thumb data")

        entry = make_entry(
            "img",
            content_type=ContentType.IMAGE,
            image_path=str(image_file),
            thumbnail_path=str(thumb_file),
        )
        entry_id = storage.add_entry(entry)

        assert image_file.exists()
        assert thumb_file.exists()
        storage.delete_entry(entry_id)
        assert not image_file.exists()
        assert not thumb_file.exists()

    def test_clear_all_removes_image_files(self, storage, make_entry, tmp_path):
        from clipsy.models import ContentType

        # Create multiple image files
        image1 = tmp_path / "img1.png"
        image2 = tmp_path / "img2.png"
        thumb1 = tmp_path / "thumb1.png"
        image1.write_bytes(b"data1")
        image2.write_bytes(b"data2")
        thumb1.write_bytes(b"thumb data")

        storage.add_entry(
            make_entry("img1", content_type=ContentType.IMAGE, image_path=str(image1), thumbnail_path=str(thumb1), content_hash="h1")
        )
        storage.add_entry(
            make_entry("img2", content_type=ContentType.IMAGE, image_path=str(image2), thumbnail_path=None, content_hash="h2")
        )

        assert image1.exists()
        assert image2.exists()
        assert thumb1.exists()

        storage.clear_all()

        assert not image1.exists()
        assert not image2.exists()
        assert not thumb1.exists()

    def test_purge_old_removes_image_files(self, storage, make_entry, tmp_path):
        from clipsy.models import ContentType

        # Create old entries with files that will be purged
        for i in range(5):
            img = tmp_path / f"old_img_{i}.png"
            thumb = tmp_path / f"old_thumb_{i}.png"
            img.write_bytes(f"data_{i}".encode())
            thumb.write_bytes(f"thumb_{i}".encode())
            storage.add_entry(
                make_entry(
                    f"img{i}",
                    content_type=ContentType.IMAGE,
                    image_path=str(img),
                    thumbnail_path=str(thumb),
                    content_hash=f"hash_{i}",
                )
            )

        assert storage.count() == 5

        # Purge all but 2
        deleted = storage.purge_old(keep_count=2)
        assert deleted == 3
        assert storage.count() == 2

        # Check that old files were deleted
        remaining_files = list(tmp_path.glob("*.png"))
        assert len(remaining_files) == 4  # 2 images + 2 thumbnails


class TestRichTextEntries:
    def test_store_and_retrieve_rtf_data(self, storage, make_entry):
        rtf_bytes = b"{\\rtf1\\ansi Hello \\b World\\b0}"
        entry = make_entry("Hello World", rtf_data=rtf_bytes)
        entry_id = storage.add_entry(entry)
        retrieved = storage.get_entry(entry_id)
        assert retrieved.rtf_data == rtf_bytes
        assert retrieved.text_content == "Hello World"

    def test_store_and_retrieve_html_data(self, storage, make_entry):
        html_bytes = b"<p>Hello <b>World</b></p>"
        entry = make_entry("Hello World", html_data=html_bytes, content_hash="html_hash")
        entry_id = storage.add_entry(entry)
        retrieved = storage.get_entry(entry_id)
        assert retrieved.html_data == html_bytes

    def test_store_both_rtf_and_html(self, storage, make_entry):
        rtf_bytes = b"{\\rtf1\\ansi Hello \\b World\\b0}"
        html_bytes = b"<p>Hello <b>World</b></p>"
        entry = make_entry("Hello World", rtf_data=rtf_bytes, html_data=html_bytes)
        entry_id = storage.add_entry(entry)
        retrieved = storage.get_entry(entry_id)
        assert retrieved.rtf_data == rtf_bytes
        assert retrieved.html_data == html_bytes

    def test_entry_without_rtf_data(self, storage, make_entry):
        entry = make_entry("plain text only")
        entry_id = storage.add_entry(entry)
        retrieved = storage.get_entry(entry_id)
        assert retrieved.rtf_data is None
        assert retrieved.html_data is None

    def test_search_still_uses_text_content(self, storage, make_entry):
        rtf_bytes = b"{\\rtf1\\ansi Hello}"
        entry = make_entry("Hello World", rtf_data=rtf_bytes)
        storage.add_entry(entry)
        results = storage.search("Hello")
        assert len(results) == 1
        assert results[0].rtf_data == rtf_bytes


class TestPinnedEntries:
    def test_get_pinned_empty(self, storage):
        assert storage.get_pinned() == []

    def test_get_pinned_returns_pinned_entries(self, storage, make_entry):
        id1 = storage.add_entry(make_entry("entry 1"))
        id2 = storage.add_entry(make_entry("entry 2", content_hash="hash2"))
        storage.toggle_pin(id1)

        pinned = storage.get_pinned()
        assert len(pinned) == 1
        assert pinned[0].id == id1
        assert pinned[0].pinned is True

    def test_count_pinned(self, storage, make_entry):
        assert storage.count_pinned() == 0

        id1 = storage.add_entry(make_entry("entry 1"))
        id2 = storage.add_entry(make_entry("entry 2", content_hash="hash2"))
        storage.toggle_pin(id1)
        storage.toggle_pin(id2)

        assert storage.count_pinned() == 2

    def test_toggle_pin_on_and_off(self, storage, make_entry):
        entry_id = storage.add_entry(make_entry("test"))

        # Pin
        result = storage.toggle_pin(entry_id)
        assert result is True
        assert storage.get_entry(entry_id).pinned is True

        # Unpin
        result = storage.toggle_pin(entry_id)
        assert result is False
        assert storage.get_entry(entry_id).pinned is False

    def test_pinned_entries_ordered_by_created_at(self, storage, make_entry):
        import time

        id1 = storage.add_entry(make_entry("older", content_hash="h1"))
        time.sleep(0.01)
        id2 = storage.add_entry(make_entry("newer", content_hash="h2"))
        storage.toggle_pin(id1)
        storage.toggle_pin(id2)

        pinned = storage.get_pinned()
        assert len(pinned) == 2
        assert pinned[0].id == id2  # newer first
        assert pinned[1].id == id1

    def test_clear_pinned(self, storage, make_entry):
        id1 = storage.add_entry(make_entry("entry 1"))
        id2 = storage.add_entry(make_entry("entry 2", content_hash="hash2"))
        id3 = storage.add_entry(make_entry("entry 3", content_hash="hash3"))
        storage.toggle_pin(id1)
        storage.toggle_pin(id2)

        assert storage.count_pinned() == 2

        storage.clear_pinned()

        assert storage.count_pinned() == 0
        assert storage.get_entry(id1).pinned is False
        assert storage.get_entry(id2).pinned is False
        assert storage.get_entry(id3).pinned is False  # was never pinned


class TestRichTextMigration:
    def test_migrate_adds_rtf_and_html_columns(self, tmp_path):
        """Test that migration adds rtf_data and html_data to old databases."""
        import sqlite3
        from clipsy.storage import StorageManager

        db_file = tmp_path / "old_db_no_rtf.sqlite"
        conn = sqlite3.connect(str(db_file))
        conn.executescript("""
            CREATE TABLE clipboard_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_type TEXT NOT NULL,
                text_content TEXT,
                image_path TEXT,
                preview TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                byte_size INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                pinned INTEGER NOT NULL DEFAULT 0,
                source_app TEXT,
                thumbnail_path TEXT,
                is_sensitive INTEGER NOT NULL DEFAULT 0,
                masked_preview TEXT
            );
        """)
        conn.commit()
        conn.close()

        mgr = StorageManager(db_path=str(db_file))

        cursor = mgr._conn.execute("PRAGMA table_info(clipboard_entries)")
        columns = {row[1] for row in cursor.fetchall()}
        assert "rtf_data" in columns
        assert "html_data" in columns

        mgr.close()
