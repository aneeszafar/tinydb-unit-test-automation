# Module 1 - Queries (tinydb/queries.py)
# Owner: Muhammad Anees

# Unit tests for the Query and QueryInstance classes, designed with
# Equivalence Class Partitioning (ECP) and Boundary Value Analysis (BVA).
# Test IDs (EC1, BVA, ERR1 ...) match docs/notes/module1_queries_ecp_bva.md

import pytest

from tinydb import Query, where
from tinydb.queries import QueryInstance

q = Query()


# ============================== PART 1 =====================================
class TestComparisonOperators:
    """==, !=, <, <=, >, >= on a field"""

    def test_condition_true(self):                                  # EC1
        assert (q.age >= 18)({"age": 25}) is True

    def test_condition_false(self):                                 # EC2
        assert (q.age >= 18)({"age": 10}) is False

    def test_missing_field_returns_false(self):                     # EC3
        assert (q.age >= 18)({"name": "Ali"}) is False

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
