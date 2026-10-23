# Task 3 - Data-driven tests for Table.insert()
# Owner: Abdullah Jamal
# Test data is read from sqe_tests/data/table_insert_data.csv

import csv
import json
from pathlib import Path

import pytest

from tinydb import TinyDB
from tinydb.storages import MemoryStorage

CSV_FILE = Path(__file__).parent.parent / "data" / "table_insert_data.csv"


def load_rows():
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.mark.parametrize("row", load_rows(), ids=lambda r: r["tc_id"])
def test_insert_from_csv(row):
    table = TinyDB(storage=MemoryStorage).table("_default")
    document = json.loads(row["document"])      # text in CSV -> Python value

    if row["expected"] == "ok":
        doc_id = table.insert(document)
        assert doc_id == 1
        assert table.get(doc_id=doc_id) == document
    else:
        with pytest.raises(ValueError):
            table.insert(document)
        assert len(table) == 0
