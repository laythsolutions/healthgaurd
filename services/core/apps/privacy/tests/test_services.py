"""Tests for the Privacy & Anonymization service layer."""

import pytest
from apps.privacy.services import AnonymizationService, ConsentManager


class TestAnonymizationService:
    def test_encode_geohash_returns_string(self):
        result = AnonymizationService.encode_geohash(34.0522, -118.2437)
        assert isinstance(result, str)
        assert len(result) > 0

    def test_encode_geohash_precision(self):
        result = AnonymizationService.encode_geohash(34.0522, -118.2437, precision=5)
        assert len(result) == 5

    def test_encode_geohash_same_coords_same_result(self):
        a = AnonymizationService.encode_geohash(40.7128, -74.0060, precision=6)
        b = AnonymizationService.encode_geohash(40.7128, -74.0060, precision=6)
        assert a == b

    def test_truncate_zip_5_digit(self):
        assert AnonymizationService.truncate_zip("90210") == "902"

    def test_truncate_zip_9_digit(self):
        assert AnonymizationService.truncate_zip("90210-1234") == "902"

    def test_truncate_zip_short(self):
        assert AnonymizationService.truncate_zip("12") == "12"

    def test_truncate_zip_empty(self):
        assert AnonymizationService.truncate_zip("") == ""

    def test_age_to_range_child(self):
        assert AnonymizationService.age_to_range(7) == "0-17"

    def test_age_to_range_adult(self):
        assert AnonymizationService.age_to_range(35) == "18-64"

    def test_age_to_range_senior(self):
        assert AnonymizationService.age_to_range(70) == "65+"

    def test_age_to_range_none(self):
        assert AnonymizationService.age_to_range(None) == "unknown"

    def test_strip_pii_email(self):
        text = "Patient email is john.doe@example.com, please call"
        result = AnonymizationService.strip_pii(text)
        assert "john.doe@example.com" not in result
        assert "[REDACTED]" in result

    def test_strip_pii_phone(self):
        text = "Contact at 555-867-5309"
        result = AnonymizationService.strip_pii(text)
        assert "555-867-5309" not in result

    def test_strip_pii_ssn(self):
        text = "SSN: 123-45-6789"
        result = AnonymizationService.strip_pii(text)
        assert "123-45-6789" not in result

    def test_hash_identifier_returns_hex(self):
        result = AnonymizationService.hash_identifier("patient-001", namespace="clinical")
        assert isinstance(result, str)
        assert len(result) == 64  # SHA-256 hex

    def test_hash_identifier_same_input_same_output(self):
        a = AnonymizationService.hash_identifier("abc", namespace="test")
        b = AnonymizationService.hash_identifier("abc", namespace="test")
        assert a == b

    def test_hash_identifier_different_namespaces(self):
        a = AnonymizationService.hash_identifier("abc", namespace="clinical")
        b = AnonymizationService.hash_identifier("abc", namespace="sensor")
        assert a != b

    def test_anonymize_clinical_case_removes_pii(self):
        raw = {
            "patient_id": "PATIENT-001",
            "age": 42,
            "lat": 34.0522,
            "lon": -118.2437,
            "zip_code": "90210",
        }
        result = AnonymizationService.anonymize_clinical_case(raw)

        assert "patient_id" not in result or result.get("patient_id") is None
        assert result.get("age_range") == "18-64"
        assert result.get("zip3") == "902"
        assert "subject_hash" in result
        assert "geohash" in result
        # Geohash should be precision 5 for clinical
        assert len(result["geohash"]) == 5
