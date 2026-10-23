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
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -e .
pip install pytest pytest-cov pytest-xdist pytest-order pytest-html pyyaml
pytest                          # runs original TinyDB tests (228 should pass)
```

## Running our tests

Instructions for suites, parallel runs and execution order will be added in Task 4.
