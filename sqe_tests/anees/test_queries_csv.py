# Task 3 - Data-driven boundary tests for Query comparison operators
# Owner: Muhammad Anees
# Test data is read from sqe_tests/data/query_age_data.csv

import csv
from pathlib import Path

import pytest

from tinydb import Query

CSV_FILE = Path(__file__).parent.parent / "data" / "query_age_data.csv"


def load_rows():
    with open(CSV_FILE, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_query(operator, limit):
    age = Query().age
    return {
        ">=": age >= limit,
        ">": age > limit,
        "<": age < limit,
        "<=": age <= limit,
        "==": age == limit,
    }[operator]


@pytest.mark.parametrize("row", load_rows(), ids=lambda r: r["tc_id"])
def test_age_query_from_csv(row):
    query = build_query(row["operator"], int(row["limit"]))
    expected = row["expected"] == "True"
    assert query({"age": int(row["age"])}) is expected
