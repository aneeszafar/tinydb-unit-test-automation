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


# ============================== PART 1 =====================================
class TestMemoryStorage:
    """MemoryStorage.read() / write()"""

    def test_new_storage_reads_none(self):                          # EC1
        assert MemoryStorage().read() is None

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

    def test_read_only_mode_write_raises(self, tmp_path):           # EC3
        path = tmp_path / "db.json"
        path.write_text("{}")
        storage = JSONStorage(str(path), access_mode="r")
        with pytest.raises(IOError):
            storage.write(SAMPLE)
        storage.close()

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
