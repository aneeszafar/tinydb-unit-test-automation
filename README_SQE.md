# SQE Assignment 3 – Unit Test Automation on TinyDB

Project under test: [TinyDB](https://github.com/msiemens/tinydb) (MIT License), forked for this assignment.

## Group members and modules

| Member | Module | Source file(s) |
|---|---|---|
| Muhammad Anees | Module 1 – Queries | `tinydb/queries.py` |
| Muhammad Anees | Module 2 – Storage & Middleware | `tinydb/storages.py`, `tinydb/middlewares.py` |
| Abdullah Jamal | Module 3 – Table | `tinydb/table.py` |

## Repository layout (our additions)

```
sqe_tests/            # our automated unit tests (original TinyDB tests are in tests/)
  anees/              # Module 1 and 2 tests
  abdullah/           # Module 3 tests
  data/               # CSV files for data-driven tests
docs/
  notes/              # ECP / BVA test design notes per module
  setup_video.md      # link to the setup video
```

## Setup

```bash
python -m venv venv
venv\Scripts\activate          # Windows: source venv/bin/activate
pip install -e .
pip install pytest pytest-cov pytest-xdist pytest-order pytest-html pyyaml
pytest                          # runs original TinyDB tests (228 should pass)
```

## Running our tests

All commands are run from the repository root with the virtual environment active.
Our configuration lives in `sqe_tests/pytest.ini`, so it is picked up automatically
whenever the path `sqe_tests` (or a folder inside it) is given to pytest.

### Run everything

```bash
pytest sqe_tests
```

### Test groups (suites)

Tests are divided into groups with pytest markers registered in `sqe_tests/pytest.ini`.

| Marker | What it contains | Command |
|---|---|---|
| `storage` | Module 2 – Storage & Middleware (Anees) | `pytest sqe_tests -m storage` |
| `table` | Module 3 – Table (Abdullah) | `pytest sqe_tests -m table` |
| `queries` | Module 1 – Queries (Anees) | `pytest sqe_tests -m queries` |
| `data_driven` | Tests that read data from CSV files | `pytest sqe_tests -m data_driven` |
| `smoke` | Small set of critical tests | `pytest sqe_tests -m smoke` |
| `negative` | Tests that expect an error for invalid input | `pytest sqe_tests -m negative` |

Markers can be combined: `pytest sqe_tests -m "storage or queries"`, `pytest sqe_tests -m "table and not negative"`.
Tests of one member only: `pytest sqe_tests/anees` or `pytest sqe_tests/abdullah`.

### Parallel execution (pytest-xdist)

```bash
pytest sqe_tests -n auto                  # one worker per CPU core
pytest sqe_tests -n 4 --dist loadfile     # 4 workers, each file stays on one worker
```

### Execution order (pytest-order)

Groups run in this order, set with `pytestmark = pytest.mark.order(n)` in each file and
`--order-group-scope=module` in `pytest.ini`:

1. `anees/test_storage.py` – storage is the lowest layer, so it is checked first
2. `abdullah/test_table.py` – tables are built on top of storage
3. `anees/test_queries.py`
4. `abdullah/test_table_csv.py` – data-driven
5. `anees/test_queries_csv.py` – data-driven

Inside a group, tests run in file order, and tests marked `@pytest.mark.order("last")`
always run at the end of their group (for example the `close()` and `truncate()` tests).
Note: when running in parallel, tests are split between workers, so the order is only
guaranteed in a normal (non-parallel) run.

### Parameterization and data-driven tests

- `@pytest.mark.parametrize` is used for ECP/BVA values, for example ages 17, 18, 19 or invalid
  document types.
- `sqe_tests/data/table_insert_data.csv` and `sqe_tests/data/query_age_data.csv` hold test data
  that is read at run time; the matching test cases are documented in `docs/Test_Cases.xlsx`.

### HTML report and coverage

```bash
pytest sqe_tests --html=report.html --self-contained-html
pytest sqe_tests --cov=tinydb --cov-report=term
```
