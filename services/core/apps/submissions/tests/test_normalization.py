"""Tests for submissions normalization — apply_schema_map and normalize_score."""

import pytest
from django.test import TestCase

from apps.submissions.normalization import (
    apply_schema_map,
    normalize_record,
    normalize_score,
)


class TestApplySchemaMap(TestCase):
    def test_renames_mapped_keys(self):
        record = {"facility_name": "Taco Spot", "inspection_date": "2024-01-01"}
        schema_map = {"facility_name": "restaurant_name"}
        result = apply_schema_map(record, schema_map)
        assert result["restaurant_name"] == "Taco Spot"
        assert "facility_name" not in result

    def test_unmapped_keys_pass_through(self):
        record = {"restaurant_name": "A", "score": 90, "extra_col": "yes"}
        result = apply_schema_map(record, {"score": "score_raw"})
        assert result["extra_col"] == "yes"
        assert result["restaurant_name"] == "A"

    def test_empty_schema_map_is_identity(self):
        record = {"a": 1, "b": 2}
        assert apply_schema_map(record, {}) == record

    def test_returns_copy_not_mutates_original(self):
        record = {"x": 1}
        result = apply_schema_map(record, {"x": "y"})
        assert "x" in record  # original untouched
        assert "y" in result


class TestNormalizeScore(TestCase):
    # SCORE_0_100
    def test_score_0_100_grade_a(self):
        assert normalize_score("95", "SCORE_0_100") == (95, "A")

    def test_score_0_100_grade_b(self):
        assert normalize_score("82", "SCORE_0_100") == (82, "B")

    def test_score_0_100_grade_c(self):
        assert normalize_score("72", "SCORE_0_100") == (72, "C")

    def test_score_0_100_grade_x(self):
        assert normalize_score("55", "SCORE_0_100") == (55, "X")

    def test_score_0_100_boundary_90(self):
        assert normalize_score("90", "SCORE_0_100") == (90, "A")

    def test_score_0_100_out_of_range(self):
        assert normalize_score("101", "SCORE_0_100") == (None, None)

    def test_score_0_100_negative(self):
        assert normalize_score("-1", "SCORE_0_100") == (None, None)

    def test_score_0_100_non_numeric(self):
        assert normalize_score("excellent", "SCORE_0_100") == (None, None)

    def test_score_0_100_float_string(self):
        score, grade = normalize_score("87.6", "SCORE_0_100")
        assert score == 87
        assert grade == "B"

    # GRADE_A_F
    def test_grade_a_f_a(self):
        assert normalize_score("A", "GRADE_A_F") == (95, "A")

    def test_grade_a_f_f(self):
        assert normalize_score("F", "GRADE_A_F") == (30, "F")

    def test_grade_a_f_lowercase(self):
        assert normalize_score("b", "GRADE_A_F") == (82, "B")

    def test_grade_a_f_invalid(self):
        assert normalize_score("Z", "GRADE_A_F") == (None, None)

    # PASS_FAIL
    def test_pass_fail_pass(self):
        assert normalize_score("pass", "PASS_FAIL") == (100, "A")

    def test_pass_fail_fail(self):
        assert normalize_score("fail", "PASS_FAIL") == (40, "X")

    def test_pass_fail_passed(self):
        assert normalize_score("passed", "PASS_FAIL") == (100, "A")

    def test_pass_fail_yes(self):
        assert normalize_score("yes", "PASS_FAIL") == (100, "A")

    def test_pass_fail_1(self):
        assert normalize_score("1", "PASS_FAIL") == (100, "A")

    def test_pass_fail_unknown(self):
        assert normalize_score("maybe", "PASS_FAIL") == (None, None)

    # LETTER_NUMERIC — numeric path
    def test_letter_numeric_number(self):
        score, grade = normalize_score("85", "LETTER_NUMERIC")
        assert score == 85
        assert grade == "B"

    # LETTER_NUMERIC — letter path
    def test_letter_numeric_letter(self):
        assert normalize_score("A", "LETTER_NUMERIC") == (95, "A")

    # None input
    def test_none_input(self):
        assert normalize_score(None, "SCORE_0_100") == (None, None)


@pytest.mark.django_db
class TestNormalizeRecord(TestCase):
    def _make_jurisdiction(self):
        from apps.submissions.models import JurisdictionAccount
        return JurisdictionAccount.objects.create(
            name="Test County HD",
            fips_code="99001",
            state="AZ",
            contact_email="hd@test.gov",
            score_system="SCORE_0_100",
            schema_map={"facility_name": "restaurant_name"},
        )

    def test_schema_map_applied(self):
        j = self._make_jurisdiction()
        result = normalize_record({"facility_name": "Taco", "address": "1 Main", "inspected_at": "2024-01-01"}, j)
        assert result["restaurant_name"] == "Taco"
        assert "facility_name" not in result

    def test_inspected_at_renamed_to_inspection_date(self):
        j = self._make_jurisdiction()
        result = normalize_record({"restaurant_name": "A", "address": "1", "inspected_at": "2024-01-01"}, j)
        assert "inspection_date" in result
        assert "inspected_at" not in result

    def test_source_jurisdiction_stamped(self):
        j = self._make_jurisdiction()
        result = normalize_record({"restaurant_name": "A", "address": "1", "inspected_at": "2024-01-01"}, j)
        assert result["source_jurisdiction"] == "99001"

    def test_state_stamped_when_missing(self):
        j = self._make_jurisdiction()
        result = normalize_record({"restaurant_name": "A", "address": "1", "inspected_at": "2024-01-01"}, j)
        assert result["state"] == "AZ"

    def test_score_normalised(self):
        j = self._make_jurisdiction()
        result = normalize_record({"restaurant_name": "A", "address": "1", "inspected_at": "2024-01-01", "score": "92"}, j)
        assert result["score"] == 92
        assert result["grade"] == "A"
