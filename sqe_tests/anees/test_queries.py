# Module 1 - Queries (tinydb/queries.py)
# Owner: Muhammad Anees

# Unit tests for the Query and QueryInstance classes, designed with
# Equivalence Class Partitioning (ECP) and Boundary Value Analysis (BVA).
# Test IDs (EC1, BVA, ERR1 ...) match docs/notes/module1_queries_ecp_bva.md

import pytest

from tinydb import Query, where
from tinydb.queries import QueryInstance

q = Query()


# Task 4: group marker + group execution order (queries group runs 3rd)
pytestmark = [pytest.mark.queries, pytest.mark.order(3)]


# ============================== PART 1 =====================================
class TestComparisonOperators:
    """==, !=, <, <=, >, >= on a field"""

    @pytest.mark.smoke
    def test_condition_true(self):                                  # EC1
        assert (q.age >= 18)({"age": 25}) is True

    def test_condition_false(self):                                 # EC2
        assert (q.age >= 18)({"age": 10}) is False

    def test_missing_field_returns_false(self):                     # EC3
        assert (q.age >= 18)({"name": "Ali"}) is False

    @pytest.mark.negative
    def test_wrong_type_raises_type_error(self):                    # EC4
        with pytest.raises(TypeError):
            (q.age >= 18)({"age": "abc"})

    @pytest.mark.parametrize("age, expected", [(17, False), (18, True), (19, True)])
    def test_greater_equal_boundary(self, age, expected):           # BVA >= 18
        assert (q.age >= 18)({"age": age}) is expected

    @pytest.mark.parametrize("age, expected", [(17, False), (18, False), (19, True)])
    def test_greater_than_boundary(self, age, expected):            # BVA > 18
        assert (q.age > 18)({"age": age}) is expected

    @pytest.mark.parametrize("age, expected", [(17, True), (18, True), (19, False)])
    def test_less_equal_boundary(self, age, expected):              # BVA <= 18
        assert (q.age <= 18)({"age": age}) is expected

    def test_equal_and_not_equal(self):
        assert (q.city == "Lahore")({"city": "Lahore"}) is True
        assert (q.city != "Lahore")({"city": "Lahore"}) is False

    def test_nested_field(self):
        assert (q.address.city == "Islamabad")({"address": {"city": "Islamabad"}}) is True


class TestExists:
    """Query.exists()"""

    def test_field_with_value(self):                                # EC1
        assert q.email.exists()({"email": "a@b.com"}) is True

    def test_field_with_none_value(self):                           # EC2
        assert q.email.exists()({"email": None}) is True

    def test_field_absent(self):                                    # EC3
        assert q.email.exists()({}) is False

    def test_nested_field_absent(self):
        assert q.address.city.exists()({"address": {}}) is False

    def test_exists_with_where_helper(self):
        assert where("email").exists()({"email": ""}) is True


# ============================== PART 2 =====================================
class TestRegex:
    """Query.matches() (from start) vs Query.search() (anywhere)"""

    @pytest.mark.parametrize("pattern, value, expected_match, expected_search", [
        ("Jo", "John", True, True),       # EC1
        ("oh", "John", False, True),      # EC2
        ("xyz", "John", False, False),    # EC3
        ("^$", "", True, True),           # BVA: empty string
    ])
    def test_matches_vs_search(self, pattern, value, expected_match, expected_search):
        doc = {"name": value}
        assert q.name.matches(pattern)(doc) is expected_match
        assert q.name.search(pattern)(doc) is expected_search

    def test_matches_case_sensitive_by_default(self):
        assert q.name.matches("john")({"name": "John"}) is False

    def test_matches_with_ignorecase_flag(self):
        import re
        assert q.name.matches("john", flags=re.IGNORECASE)({"name": "John"}) is True

    def test_regex_on_missing_field(self):
        assert q.name.search("a")({}) is False


class TestOneOf:
    """Query.one_of(items)"""

    def test_value_in_list(self):                                   # EC1
        assert q.role.one_of(["admin", "user"])({"role": "admin"}) is True

    def test_value_not_in_list(self):                               # EC2
        assert q.role.one_of(["admin", "user"])({"role": "guest"}) is False

    def test_empty_list(self):                                      # BVA: 0 items
        assert q.role.one_of([])({"role": "admin"}) is False

    def test_single_item_list(self):                                # BVA: 1 item
        assert q.role.one_of(["admin"])({"role": "admin"}) is True

    def test_missing_field(self):
        assert q.role.one_of(["admin"])({}) is False


# ============================== PART 3 =====================================
class TestAnyAll:
    """Query.any() and Query.all() on list fields"""

    def test_any_some_match(self):                                  # EC1
        assert q.tags.any(["b", "z"])({"tags": ["a", "b"]}) is True

    def test_any_no_match(self):                                    # EC2
        assert q.tags.any(["x", "z"])({"tags": ["a", "b"]}) is False

    def test_all_every_item_present(self):                          # EC3
        assert q.tags.all(["a", "b"])({"tags": ["a", "b"]}) is True

    def test_all_one_item_missing(self):                            # EC4
        assert q.tags.all(["a", "b"])({"tags": ["a"]}) is False

    def test_any_on_empty_list_field(self):                         # BVA
        assert q.tags.any(["a"])({"tags": []}) is False

    def test_any_with_sub_query(self):
        doc = {"items": [{"price": 50}, {"price": 150}]}
        assert q.items.any(Query().price > 100)(doc) is True


class TestLogicalOperators:
    """&, |, ~ and error cases on QueryInstance"""

    @pytest.mark.smoke
    def test_and_both_true(self):                                   # EC1
        cond = (q.age > 18) & (q.city == "Lahore")
        assert cond({"age": 25, "city": "Lahore"}) is True

    def test_and_one_false(self):                                   # EC2
        cond = (q.age > 18) & (q.city == "Lahore")
        assert cond({"age": 25, "city": "Karachi"}) is False

    def test_or_one_true(self):                                     # EC3
        cond = (q.age > 18) | (q.city == "Lahore")
        assert cond({"age": 10, "city": "Lahore"}) is True

    def test_not(self):                                             # EC4
        assert (~(q.age > 18))({"age": 25}) is False

    def test_result_is_query_instance(self):
        assert isinstance((q.age > 1) & (q.age < 5), QueryInstance)

    @pytest.mark.negative
    @pytest.mark.order("last")   # Task 4: this test always runs last in its group
    def test_empty_query_raises_runtime_error(self):                # ERR1
        with pytest.raises(RuntimeError):
            Query()({"age": 1})

    def test_custom_test_function(self):
        is_even = lambda value: value % 2 == 0
        assert q.num.test(is_even)({"num": 4}) is True
        assert q.num.test(is_even)({"num": 3}) is False
