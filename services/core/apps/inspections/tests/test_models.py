"""Tests for the Inspections app models, utils, and views."""

import pytest
from datetime import datetime, timezone as tz
from django.test import TestCase
from rest_framework.test import APIClient

from apps.restaurants.models import Organization, Restaurant
from apps.inspections.models import Inspection, InspectionViolation, InspectionSchedule
from apps.inspections.utils import (
    get_or_create_system_org,
    get_or_create_public_restaurant,
    ingest_inspection_record,
    SYSTEM_ORG_NAME,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_restaurant(name="Test Restaurant", state="CA", city="Los Angeles"):
    org, _ = Organization.objects.get_or_create(
        name="Test Org",
        defaults={"tier": "STARTER", "subscription_status": "active", "monthly_fee": 99},
    )
    code = f"test_{name[:10].replace(' ', '_').lower()}"
    restaurant, _ = Restaurant.objects.get_or_create(
        code=code,
        defaults={
            "organization": org,
            "name": name,
            "address": "123 Main St",
            "city": city,
            "state": state,
            "zip_code": "90210",
            "gateway_id": f"gw_{code}",
            "status": "ACTIVE",
        },
    )
    return restaurant


def make_inspection(restaurant, grade="A", score=95):
    return Inspection.objects.create(
        restaurant=restaurant,
        source_jurisdiction="CA",
        inspection_type=Inspection.InspectionType.ROUTINE,
        inspected_at=datetime(2026, 1, 15, tzinfo=tz.utc),
        score=score,
        grade=grade,
    )


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestInspectionModel(TestCase):
    def test_create_inspection(self):
        restaurant = make_restaurant()
        inspection = make_inspection(restaurant)
        assert inspection.pk is not None
        assert inspection.grade == "A"
        assert inspection.score == 95

    def test_str_representation(self):
        restaurant = make_restaurant()
        inspection = make_inspection(restaurant)
        s = str(inspection)
        assert "routine" in s.lower() or restaurant.name[:5] in s

    def test_violation_attached(self):
        restaurant = make_restaurant(name="Vio Rest")
        inspection = make_inspection(restaurant)
        v = InspectionViolation.objects.create(
            inspection=inspection,
            description="Handwashing station blocked",
            severity=InspectionViolation.Severity.CRITICAL,
            violation_status=InspectionViolation.Status.OBSERVED,
        )
        assert v.severity == "critical"
        assert inspection.violations.count() == 1

    def test_inspection_schedule_model(self):
        from datetime import date
        restaurant = make_restaurant(name="Sched Rest")
        schedule = InspectionSchedule.objects.create(
            restaurant=restaurant,
            scheduled_date=date(2026, 3, 1),
            inspection_type=Inspection.InspectionType.ROUTINE,
            status=InspectionSchedule.ScheduleStatus.SCHEDULED,
        )
        assert schedule.pk is not None
        assert schedule.status == "scheduled"


# ---------------------------------------------------------------------------
# Utils tests
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestIngestUtils(TestCase):
    def test_get_or_create_system_org(self):
        org = get_or_create_system_org()
        assert org.name == SYSTEM_ORG_NAME
        # idempotent
        org2 = get_or_create_system_org()
        assert org.pk == org2.pk

    def test_get_or_create_public_restaurant(self):
        record = {
            "restaurant_name": "Farmhouse Bistro",
            "address": "456 Oak Ave",
            "city": "Sacramento",
            "state": "CA",
            "zip_code": "95814",
        }
        r = get_or_create_public_restaurant(record)
        assert r.pk is not None
        assert r.name == "Farmhouse Bistro"
        assert r.code.startswith("pub_")
        assert r.gateway_id.startswith("pub_")

    def test_get_or_create_public_restaurant_idempotent(self):
        record = {
            "restaurant_name": "Idempotent Cafe",
            "address": "999 Repeat Rd",
            "city": "Oakland",
            "state": "CA",
            "zip_code": "94601",
        }
        r1 = get_or_create_public_restaurant(record)
        r2 = get_or_create_public_restaurant(record)
        assert r1.pk == r2.pk

    def test_ingest_inspection_record_creates_inspection(self):
        record = {
            "restaurant_name": "Ingest Cafe",
            "address": "1 Ingest Ln",
            "city": "San Francisco",
            "state": "CA",
            "zip_code": "94105",
            "inspection_date": "2026-02-01T12:00:00",
            "score": 88,
            "grade": "B",
            "violations": [
                {"code": "7E", "description": "Improper cooling", "severity": "serious"},
            ],
        }
        inspection = ingest_inspection_record(record)
        assert inspection is not None
        assert inspection.score == 88
        assert inspection.grade == "B"
        assert inspection.violations.count() == 1
        assert inspection.violations.first().severity == "serious"

    def test_ingest_inspection_record_deduplicates(self):
        record = {
            "restaurant_name": "Dedup Diner",
            "address": "2 Dedup St",
            "city": "San Jose",
            "state": "CA",
            "zip_code": "95101",
            "inspection_date": "2026-02-10T09:00:00",
            "score": 92,
            "grade": "A",
        }
        i1 = ingest_inspection_record(record)
        i2 = ingest_inspection_record(record)
        assert i1 is not None
        assert i2 is None  # duplicate skipped

    def test_ingest_record_missing_date_returns_none(self):
        record = {
            "restaurant_name": "No Date",
            "address": "3 Missing St",
            "city": "LA",
            "state": "CA",
            "inspection_date": None,
        }
        result = ingest_inspection_record(record)
        assert result is None

    def test_ingest_updates_restaurant_last_inspection(self):
        record = {
            "restaurant_name": "Update Check",
            "address": "4 Check Ave",
            "city": "Fresno",
            "state": "CA",
            "zip_code": "93701",
            "inspection_date": "2026-02-20T10:00:00",
            "score": 95,
            "grade": "A",
        }
        inspection = ingest_inspection_record(record)
        assert inspection is not None
        inspection.restaurant.refresh_from_db()
        assert inspection.restaurant.last_inspection_score == 95
        from datetime import date
        assert inspection.restaurant.last_inspection_date == date(2026, 2, 20)

    def test_ingest_out_of_range_score_becomes_none(self):
        record = {
            "restaurant_name": "Bad Score",
            "address": "5 Bad Rd",
            "city": "Modesto",
            "state": "CA",
            "inspection_date": "2026-01-05T08:00:00",
            "score": 999,
            "grade": "",
        }
        inspection = ingest_inspection_record(record)
        assert inspection is not None
        assert inspection.score is None


# ---------------------------------------------------------------------------
# View tests (public endpoints)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestInspectionViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.restaurant = make_restaurant()

    def test_list_no_auth(self):
        response = self.client.get("/api/v1/inspections/")
        assert response.status_code == 200

    def test_detail_no_auth(self):
        inspection = make_inspection(self.restaurant)
        response = self.client.get(f"/api/v1/inspections/{inspection.pk}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == inspection.pk

    def test_restaurant_history_no_auth(self):
        make_inspection(self.restaurant, grade="A")
        make_inspection(self.restaurant, grade="B")
        response = self.client.get(
            f"/api/v1/inspections/restaurant/{self.restaurant.pk}/"
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1

    def test_post_inspection_requires_auth(self):
        response = self.client.post("/api/v1/inspections/", {}, format="json")
        assert response.status_code in (401, 403)

    def test_schedule_requires_auth(self):
        response = self.client.get("/api/v1/inspections/schedule/")
        assert response.status_code in (401, 403)

    def test_export_requires_auth(self):
        response = self.client.get("/api/v1/inspections/export/")
        assert response.status_code in (401, 403)
