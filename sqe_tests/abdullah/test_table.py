# Module 3 - Table (tinydb/table.py)
# Owner: Abdullah Jamal

# Unit tests for the Table and Document classes, designed with
# Equivalence Class Partitioning (ECP) and Boundary Value Analysis (BVA).
# Test IDs (EC1, BVA, ERR1 ...) match docs/notes/module3_table_ecp_bva.md 

import pytest

from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage
from tinydb.table import Document


# ---------------------------------------------------------------------------
# Fixtures: fresh test data for every test, kept in memory (no files created)
# ---------------------------------------------------------------------------
@pytest.fixture
def table():
    """An empty table."""
    db = TinyDB(storage=MemoryStorage)
    yield db.table("_default")
    db.close()


@pytest.fixture
def filled_table(table):
    """A table with 3 documents: ages 10, 20, 30 (doc_ids 1, 2, 3)."""
    table.insert_multiple([
        {"name": "Ali", "age": 10},
        {"name": "Sara", "age": 20},
        {"name": "Usman", "age": 30},
    ])
    return table


q = Query()


# ============================== PART 1 =====================================
class TestInsert:
    """Table.insert(document)"""

    def test_insert_valid_dict_returns_id(self, table):            # EC1
        doc_id = table.insert({"name": "Ali"})
        assert doc_id == 1
        assert table.get(doc_id=1) == {"name": "Ali"}

    def test_insert_empty_dict_is_accepted(self, table):           # EC2 (boundary)
        assert table.insert({}) == 1
        assert len(table) == 1

    @pytest.mark.parametrize("bad_doc", [[1, 2], "abc", 5, None])  # EC3, EC4
    def test_insert_non_mapping_raises_value_error(self, table, bad_doc):
        with pytest.raises(ValueError):
            table.insert(bad_doc)
        assert len(table) == 0

    def test_insert_document_with_existing_id_raises(self, table): # EC5
        table.insert({"a": 1})
        with pytest.raises(ValueError):
            table.insert(Document({"b": 2}, doc_id=1))

    def test_ids_increase_by_one(self, table):                     # BVA: 1 -> 2 -> 3
        assert [table.insert({"n": i}) for i in range(3)] == [1, 2, 3]

    def test_insert_after_truncate_restarts_at_one(self, filled_table):  # BVA
        filled_table.truncate()
        assert filled_table.insert({"new": True}) == 1


class TestInsertMultiple:
    """Table.insert_multiple(documents)"""

    def test_insert_multiple_valid_list(self, table):              # EC1
        assert table.insert_multiple([{"a": 1}, {"a": 2}, {"a": 3}]) == [1, 2, 3]

    def test_insert_multiple_empty_list(self, table):              # EC2 (boundary: 0 items)
        assert table.insert_multiple([]) == []
        assert len(table) == 0

    def test_insert_multiple_single_item(self, table):             # EC3 (boundary: 1 item)
        assert table.insert_multiple([{"a": 1}]) == [1]

    def test_insert_multiple_with_one_invalid_inserts_nothing(self, table):  # EC4
        with pytest.raises(ValueError):
            table.insert_multiple([{"a": 1}, 5])
        assert len(table) == 0          # all-or-nothing behaviour

    def test_insert_multiple_continues_ids(self, filled_table):
        assert filled_table.insert_multiple([{"x": 1}, {"x": 2}]) == [4, 5]
