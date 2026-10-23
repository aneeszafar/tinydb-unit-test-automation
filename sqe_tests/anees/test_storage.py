# Module 2 - Storage & Middleware (tinydb/storages.py, tinydb/middlewares.py)
# Owner: Muhammad Anees

# Unit tests for MemoryStorage, JSONStorage and CachingMiddleware, designed with
# Equivalence Class Partitioning (ECP) and Boundary Value Analysis (BVA).
# Test IDs (EC1, BVA ...) match docs/notes/module2_storage_ecp_bva.md

import json

import pytest

from tinydb import TinyDB
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage, MemoryStorage

SAMPLE = {"users": {"1": {"name": "Ali"}}}

# Task 4: group marker + group execution order (storage group runs 1st)
pytestmark = [pytest.mark.storage, pytest.mark.order(1)]


# ============================== PART 1 =====================================
class TestMemoryStorage:
    """MemoryStorage.read() / write()"""

    def test_new_storage_reads_none(self):                          # EC1
        assert MemoryStorage().read() is None

    @pytest.mark.smoke
    def test_write_then_read(self):                                 # EC2
        storage = MemoryStorage()
        storage.write(SAMPLE)
        assert storage.read() == SAMPLE

    def test_second_write_overwrites(self):                         # EC3
        storage = MemoryStorage()
        storage.write({"a": {}})
        storage.write({"b": {}})
        assert storage.read() == {"b": {}}

    def test_write_empty_dict(self):                                # BVA
        storage = MemoryStorage()
        storage.write({})
        assert storage.read() == {}

    def test_used_by_tinydb(self):
        db = TinyDB(storage=MemoryStorage)
        db.insert({"x": 1})
        assert len(db) == 1


class TestJSONStorageCreate:
    """JSONStorage constructor: creating / opening a file"""

    def test_creates_file_in_existing_folder(self, tmp_path):       # EC1
        path = tmp_path / "db.json"
        JSONStorage(str(path)).close()
        assert path.exists()

    @pytest.mark.negative
    def test_missing_folder_without_create_dirs_raises(self, tmp_path):  # EC2
        with pytest.raises(FileNotFoundError):
            JSONStorage(str(tmp_path / "x" / "y" / "db.json"))

    def test_missing_folder_with_create_dirs(self, tmp_path):       # EC3
        path = tmp_path / "x" / "y" / "db.json"
        JSONStorage(str(path), create_dirs=True).close()
        assert path.exists()

    def test_unsafe_access_mode_warns(self, tmp_path):              # EC4
        with pytest.warns(UserWarning):
            JSONStorage(str(tmp_path / "db.json"), access_mode="w").close()

    def test_safe_access_mode_no_warning(self, tmp_path, recwarn):
        JSONStorage(str(tmp_path / "db.json"), access_mode="r+").close()
        assert len(recwarn) == 0


# ============================== PART 2 =====================================
class TestJSONStorageReadWrite:
    """JSONStorage.read() / write()"""

    @pytest.fixture
    def storage(self, tmp_path):
        s = JSONStorage(str(tmp_path / "db.json"))
        yield s
        s.close()

    def test_empty_file_reads_none(self, storage):                  # EC1 (size 0)
        assert storage.read() is None

    def test_write_then_read(self, storage):                        # EC2
        storage.write(SAMPLE)
        assert storage.read() == SAMPLE

    @pytest.mark.negative
    def test_read_only_mode_write_raises(self, tmp_path):           # EC3
        path = tmp_path / "db.json"
        path.write_text("{}")
        storage = JSONStorage(str(path), access_mode="r")
        with pytest.raises(IOError):
            storage.write(SAMPLE)
        storage.close()

    @pytest.mark.negative
    def test_corrupted_json_raises(self, tmp_path):                 # EC4
        path = tmp_path / "db.json"
        path.write_text("{bad")
        storage = JSONStorage(str(path))
        with pytest.raises(json.JSONDecodeError):
            storage.read()
        storage.close()

    def test_smaller_second_write_leaves_no_leftover(self, storage, tmp_path):  # EC5
        storage.write({"t": {str(i): {"v": "x" * 50} for i in range(20)}})
        storage.write({"t": {}})
        assert storage.read() == {"t": {}}
        assert json.loads((tmp_path / "db.json").read_text()) == {"t": {}}


# ============================== PART 3 =====================================
class TestCachingMiddleware:
    """CachingMiddleware: write cache, flush and close"""

    @pytest.fixture
    def cache(self):
        c = CachingMiddleware(MemoryStorage)()
        c.storage.write({"start": {}})       # data already saved in real storage
        return c

    @pytest.mark.parametrize("writes, saved", [
        (2, False),   # BVA: one below the limit
        (3, True),    # BVA: on the limit
    ])
    def test_cache_size_boundary_small(self, cache, writes, saved):
        cache.WRITE_CACHE_SIZE = 3
        for i in range(writes):
            cache.write({"last": {"i": i}})
        assert (cache.storage.read() == {"last": {"i": writes - 1}}) is saved

    def test_default_limit_999_not_saved(self, cache):              # BVA 999
        for i in range(999):
            cache.write({"last": {"i": i}})
        assert cache.storage.read() == {"start": {}}

    def test_default_limit_1000_saved(self, cache):                 # BVA 1000
        for i in range(1000):
            cache.write({"last": {"i": i}})
        assert cache.storage.read() == {"last": {"i": 999}}

    def test_write_after_flush_is_cached_again(self, cache):        # BVA 1001
        for i in range(1001):
            cache.write({"last": {"i": i}})
        assert cache.storage.read() == {"last": {"i": 999}}

    def test_read_returns_cached_data(self, cache):
        cache.write({"new": {}})
        assert cache.read() == {"new": {}}

    @pytest.mark.smoke
    def test_flush_saves_pending_writes(self, cache):               # EC1
        cache.write({"new": {}})
        cache.flush()
        assert cache.storage.read() == {"new": {}}

    def test_flush_without_pending_writes(self, cache):             # EC2
        cache.flush()
        assert cache.storage.read() == {"start": {}}

    @pytest.mark.order("last")   # Task 4: this test always runs last in its group
    def test_close_saves_pending_writes(self, cache):               # EC3
        cache.write({"new": {}})
        cache.close()
        assert cache.storage.read() == {"new": {}}

    @pytest.mark.negative
    @pytest.mark.parametrize("action", ["read", "write"])
    def test_use_after_close_raises(self, cache, action):           # EC4
        cache.close()
        with pytest.raises(ValueError):
            cache.read() if action == "read" else cache.write({})
