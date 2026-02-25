"""Tests for the Clinical app — models, serializers, and view auth."""

import pytest
from datetime import date
from django.test import TestCase
from rest_framework.test import APIClient

from apps.clinical.models import (
    ClinicalCase,
    ClinicalExposure,
    OutbreakInvestigation,
    ReportingInstitution,
)


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestReportingInstitution(TestCase):
    def test_create_institution(self):
        inst = ReportingInstitution.objects.create(
            name="City General Hospital",
            institution_type="hospital",
            api_key_hash="a" * 64,
            is_active=True,
        )
        assert inst.pk is not None
        assert inst.is_active is True

    def test_str_representation(self):
        inst = ReportingInstitution.objects.create(
            name="Test Hospital",
            institution_type="hospital",
            api_key_hash="b" * 64,
        )
        assert "Test Hospital" in str(inst)


@pytest.mark.django_db
class TestClinicalCaseModel(TestCase):
    def _make_institution(self):
        return ReportingInstitution.objects.create(
            name="Test Clinic",
            institution_type="clinic",
            api_key_hash="c" * 64,
        )

    def test_clinical_case_has_no_pii(self):
        inst = self._make_institution()
        case = ClinicalCase.objects.create(
            reporting_institution=inst,
            subject_hash="d" * 64,
            age_range="18-64",
            zip3="902",
            geohash="9q5f",
            onset_date=date(2026, 2, 1),
            symptoms=["nausea", "vomiting"],
            pathogen="Salmonella",
        )
        assert case.pk is not None
        # No PII fields should exist
        assert not hasattr(case, "patient_name")
        assert not hasattr(case, "date_of_birth")
        assert not hasattr(case, "ssn")
        # Anonymized fields present
        assert case.subject_hash == "d" * 64
        assert case.age_range == "18-64"
        assert case.zip3 == "902"

    def test_geohash_max_length_respected(self):
        inst = self._make_institution()
        # geohash precision 5 = 5 chars; db field should accept it
        case = ClinicalCase.objects.create(
            reporting_institution=inst,
            subject_hash="e" * 64,
            age_range="65+",
            zip3="123",
            geohash="9q5f2",  # precision 5
            onset_date=date(2026, 2, 5),
            symptoms=["fever"],
        )
        assert len(case.geohash) == 5

    def test_symptoms_stored_as_list(self):
        inst = self._make_institution()
        case = ClinicalCase.objects.create(
            reporting_institution=inst,
            subject_hash="f" * 64,
            age_range="18-64",
            zip3="941",
            geohash="9q8v",
            onset_date=date(2026, 2, 10),
            symptoms=["diarrhea", "abdominal cramps", "fever"],
        )
        assert isinstance(case.symptoms, list)
        assert "fever" in case.symptoms


@pytest.mark.django_db
class TestOutbreakInvestigation(TestCase):
    def test_create_investigation(self):
        inv = OutbreakInvestigation.objects.create(
            title="Salmonella cluster — LA County",
            pathogen="Salmonella",
            status="open",
            geographic_scope="Los Angeles County, CA",
            case_count_at_open=8,
        )
        assert inv.pk is not None
        assert inv.status == "open"
        assert inv.case_count_at_open == 8


# ---------------------------------------------------------------------------
# View auth tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestClinicalViews(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_case_submission_requires_auth(self):
        response = self.client.post(
            "/api/v1/clinical/cases/",
            {
                "patient_id": "P-001",
                "age": 30,
                "lat": 34.05,
                "lon": -118.24,
                "zip_code": "90001",
                "onset_date": "2026-02-01",
                "symptoms": ["fever"],
            },
            format="json",
        )
        # Without institution key or JWT, should be 401
        assert response.status_code == 401

    def test_investigation_list_requires_health_dept(self):
        from apps.accounts.models import User
        normal_user = User.objects.create_user(
            username="normalclinical",
            password="pass123",
            email="nc@example.com",
        )
        self.client.force_authenticate(user=normal_user)
        response = self.client.get("/api/v1/clinical/investigations/")
        # Normal users don't have health_dept role
        assert response.status_code in (403, 401)

    def test_investigation_list_allowed_for_staff(self):
        from apps.accounts.models import User
        staff = User.objects.create_user(
            username="staffclinical",
            password="pass123",
            email="staff@example.com",
            is_staff=True,
        )
        self.client.force_authenticate(user=staff)
        response = self.client.get("/api/v1/clinical/investigations/")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_case_submission_with_institution_key(self):
        import hashlib, hmac
        from django.conf import settings

        salt = getattr(settings, "ANONYMIZATION_SALT", "test-salt").encode()
        raw_key = "test-institution-key-001"
        key_hash = hmac.new(salt, raw_key.encode(), hashlib.sha256).hexdigest()

        inst = ReportingInstitution.objects.create(
            name="Test Hospital",
            institution_type="hospital",
            api_key_hash=key_hash,
            is_active=True,
        )

        response = self.client.post(
            "/api/v1/clinical/cases/",
            {
                "patient_id": "P-SUBMIT-001",
                "age": 45,
                "lat": 40.71,
                "lon": -74.00,
                "zip_code": "10001",
                "onset_date": "2026-02-15",
                "symptoms": ["nausea", "vomiting"],
                "pathogen": "E. coli",
            },
            format="json",
            HTTP_X_INSTITUTION_KEY=raw_key,
        )
        # Should create a case (201) or return validation error (400)
        # but NOT 401 if key is valid
        assert response.status_code != 401
