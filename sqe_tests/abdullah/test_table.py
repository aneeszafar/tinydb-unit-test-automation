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

# ============================== PART 2 =====================================
class TestGet:
    """Table.get(cond / doc_id / doc_ids)"""

    def test_get_existing_doc_id(self, filled_table):              # EC1
        assert filled_table.get(doc_id=2)["name"] == "Sara"

    @pytest.mark.parametrize("missing_id", [99, 0, -1])            # EC2, EC3 (boundaries)
    def test_get_missing_doc_id_returns_none(self, filled_table, missing_id):
        assert filled_table.get(doc_id=missing_id) is None

    def test_get_doc_ids_ignores_missing(self, filled_table):      # EC4
        docs = filled_table.get(doc_ids=[1, 99])
        assert [d.doc_id for d in docs] == [1]

    def test_get_by_condition_returns_first_match(self, filled_table):  # EC5
        assert filled_table.get(q.age > 15).doc_id == 2

    def test_get_by_condition_no_match(self, filled_table):
        assert filled_table.get(q.age > 100) is None

    def test_get_without_arguments_raises(self, filled_table):     # ERR1
        with pytest.raises(RuntimeError):
            filled_table.get()


class TestUpdate:
    """Table.update(fields, cond / doc_ids)"""

    def test_update_without_condition_updates_all(self, filled_table):  # EC1
        assert filled_table.update({"active": True}) == [1, 2, 3]
        assert all(d["active"] for d in filled_table.all())

    def test_update_with_condition_updates_matching(self, filled_table):  # EC2
        assert filled_table.update({"adult": True}, q.age > 15) == [2, 3]
        assert "adult" not in filled_table.get(doc_id=1)

    def test_update_condition_matches_none(self, filled_table):    # EC3
        assert filled_table.update({"x": 1}, q.age > 100) == []

    def test_update_missing_doc_ids(self, filled_table):           # EC4
        assert filled_table.update({"x": 1}, doc_ids=[99]) == []

    def test_update_with_function(self, filled_table):             # EC5
        def birthday(doc):
            doc["age"] += 1
        filled_table.update(birthday, doc_ids=[1])
        assert filled_table.get(doc_id=1)["age"] == 11

    def test_update_overwrites_existing_field(self, filled_table):
        filled_table.update({"name": "Ahmed"}, doc_ids=[1])
        assert filled_table.get(doc_id=1)["name"] == "Ahmed"

# ============================== PART 3 =====================================
class TestRemoveAndTruncate:
    """Table.remove(cond / doc_ids) and Table.truncate()"""

    def test_remove_by_condition(self, filled_table):              # EC1
        assert filled_table.remove(q.age < 15) == [1]
        assert len(filled_table) == 2

    def test_remove_by_doc_ids(self, filled_table):
        assert filled_table.remove(doc_ids=[2, 3]) == [2, 3]
        assert len(filled_table) == 1

    def test_remove_missing_doc_ids(self, filled_table):           # EC2
        assert filled_table.remove(doc_ids=[99]) == []
        assert len(filled_table) == 3

    def test_remove_without_arguments_raises(self, filled_table):  # ERR1
        with pytest.raises(RuntimeError):
            filled_table.remove()

    def test_truncate_empties_table(self, filled_table):           # EC3
        filled_table.truncate()
        assert len(filled_table) == 0

    def test_truncate_on_empty_table(self, table):                 # boundary
        table.truncate()
        assert len(table) == 0


class TestCountContainsUpsert:
    """Table.count(), Table.contains(), Table.upsert()"""

    @pytest.mark.parametrize("min_age, expected", [
        (20, 2),     # EC1
        (30, 1),     # BVA: on the highest value
        (31, 0),     # BVA: just above the highest value
        (10, 3),     # BVA: on the lowest value
    ])
    def test_count_with_boundaries(self, filled_table, min_age, expected):
        assert filled_table.count(q.age >= min_age) == expected

    def test_contains_doc_id(self, filled_table):                  # EC2
        assert filled_table.contains(doc_id=1) is True
        assert filled_table.contains(doc_id=99) is False

    def test_contains_condition(self, filled_table):
        assert filled_table.contains(q.name == "Sara") is True
        assert filled_table.contains(q.name == "Nobody") is False

    def test_contains_without_arguments_raises(self, filled_table):  # ERR1
        with pytest.raises(RuntimeError):
            filled_table.contains()

    def test_upsert_updates_when_match_exists(self, filled_table):  # EC3
        assert filled_table.upsert({"name": "Ali", "age": 11}, q.name == "Ali") == [1]
        assert filled_table.get(doc_id=1)["age"] == 11
        assert len(filled_table) == 3

    def test_upsert_inserts_when_no_match(self, filled_table):     # EC4
        assert filled_table.upsert({"name": "Zara"}, q.name == "Zara") == [4]
        assert len(filled_table) == 4

    def test_upsert_without_condition_raises(self, filled_table):  # ERR2
        with pytest.raises(ValueError):
            filled_table.upsert({"name": "X"})


class TestDocument:
    """Document class"""

    def test_document_keeps_doc_id(self):
        assert Document({"a": 1}, doc_id=7).doc_id == 7

    def test_document_behaves_like_dict(self):
        doc = Document({"a": 1}, doc_id=1)
        assert doc["a"] == 1 and doc == {"a": 1}

    def test_returned_documents_have_correct_ids(self, filled_table):
        assert [d.doc_id for d in filled_table.all()] == [1, 2, 3]
