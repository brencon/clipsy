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
