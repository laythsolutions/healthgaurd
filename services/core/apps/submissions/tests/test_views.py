"""
Integration tests for the submissions views.

Covers:
  - JurisdictionRegisterView (public, throttled)
  - SubmitInspectionsView (X-Submission-Key auth)
  - BatchListView / BatchDetailView
  - AdminRegistrationListView / AdminRegistrationReviewView
"""

import hashlib

import pytest
from django.test import TestCase
from rest_framework.test import APIClient

from apps.accounts.models import APIKey, User
from apps.submissions.models import JurisdictionAccount, SubmissionBatch


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_jurisdiction(**kwargs):
    defaults = dict(
        name="Test HD",
        fips_code="55001",
        state="WI",
        contact_email="hd@test.gov",
        status=JurisdictionAccount.Status.ACTIVE,
    )
    defaults.update(kwargs)
    return JurisdictionAccount.objects.create(**defaults)


def _make_api_key(user, jurisdiction):
    """Create an APIKey with submissions:write scope and link to jurisdiction."""
    full_key = "hg_live_testkey123456789012345678901"
    key_hash = hashlib.sha256(full_key.encode()).hexdigest()
    api_key = APIKey.objects.create(
        user=user,
        name="Test submission key",
        key_type=APIKey.KeyType.SERVICE,
        key_prefix=full_key[:10],
        key_hash=key_hash,
        scopes=["submissions:write"],
        is_active=True,
    )
    jurisdiction.api_key = api_key
    jurisdiction.save(update_fields=["api_key"])
    return full_key, api_key


# ---------------------------------------------------------------------------
# Registration (public)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestJurisdictionRegisterView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/submissions/register/"

    def test_valid_registration_returns_201(self):
        resp = self.client.post(self.url, {
            "name": "Maricopa County HD",
            "fips_code": "04013",
            "state": "AZ",
            "contact_email": "hd@maricopa.gov",
            "jurisdiction_type": "COUNTY",
            "score_system": "SCORE_0_100",
        }, format="json")
        assert resp.status_code == 201
        data = resp.json()
        assert data["status"] == "PENDING"
        assert data["fips_code"] == "04013"

    def test_duplicate_fips_returns_400(self):
        _make_jurisdiction(fips_code="04013", status="PENDING")
        resp = self.client.post(self.url, {
            "name": "Another HD",
            "fips_code": "04013",
            "state": "AZ",
            "contact_email": "other@hd.gov",
            "jurisdiction_type": "COUNTY",
            "score_system": "SCORE_0_100",
        }, format="json")
        assert resp.status_code == 400
        assert "fips_code" in resp.json()

    def test_invalid_fips_format_returns_400(self):
        resp = self.client.post(self.url, {
            "name": "Bad HD",
            "fips_code": "ABCDE",
            "state": "AZ",
            "contact_email": "hd@bad.gov",
            "jurisdiction_type": "COUNTY",
            "score_system": "SCORE_0_100",
        }, format="json")
        assert resp.status_code == 400
        assert "fips_code" in resp.json()

    def test_missing_required_field_returns_400(self):
        resp = self.client.post(self.url, {
            "fips_code": "01001",
            "state": "AL",
        }, format="json")
        assert resp.status_code == 400

    def test_get_not_allowed(self):
        resp = self.client.get(self.url)
        assert resp.status_code == 405


# ---------------------------------------------------------------------------
# Submit inspections (authenticated)
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestSubmitInspectionsView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.url = "/api/v1/submissions/inspections/"
        self.user = User.objects.create_user(email="hd@submit.gov", password="testpass12!")
        self.jurisdiction = _make_jurisdiction(fips_code="55001")
        self.raw_key, self.api_key = _make_api_key(self.user, self.jurisdiction)

    def _post(self, records, key=None):
        headers = {"HTTP_X_SUBMISSION_KEY": key or self.raw_key}
        return self.client.post(self.url, {"records": records}, format="json", **headers)

    def test_valid_batch_returns_202(self):
        resp = self._post([{
            "restaurant_name": "Taco Palace",
            "address": "1 Main St",
            "inspected_at": "2024-03-15",
        }])
        assert resp.status_code == 202
        data = resp.json()
        assert data["status"] == "PENDING"
        assert data["total_rows"] == 1
        assert "batch_id" in data

    def test_batch_created_in_db(self):
        self._post([{
            "restaurant_name": "Burger Barn",
            "address": "2 Elm St",
            "inspected_at": "2024-03-16",
        }])
        assert SubmissionBatch.objects.filter(jurisdiction=self.jurisdiction).exists()

    def test_no_key_returns_401(self):
        resp = self.client.post(self.url, {"records": []}, format="json")
        assert resp.status_code == 401

    def test_invalid_key_returns_401(self):
        resp = self._post([{"restaurant_name": "A", "address": "B", "inspected_at": "2024-01-01"}],
                          key="hg_live_badkey")
        assert resp.status_code == 401

    def test_missing_required_field_returns_400(self):
        resp = self._post([{"address": "1 Main", "inspected_at": "2024-01-01"}])
        assert resp.status_code == 400

    def test_empty_records_returns_400(self):
        resp = self._post([])
        assert resp.status_code == 400

    def test_suspended_account_returns_403(self):
        self.jurisdiction.status = JurisdictionAccount.Status.SUSPENDED
        self.jurisdiction.save(update_fields=["status"])
        resp = self._post([{"restaurant_name": "A", "address": "B", "inspected_at": "2024-01-01"}])
        assert resp.status_code == 403

    def test_key_missing_scope_returns_401(self):
        from django.utils import timezone
        full_key = "hg_live_noscope000000000000000000000"
        key_hash = hashlib.sha256(full_key.encode()).hexdigest()
        APIKey.objects.create(
            user=self.user,
            name="No-scope key",
            key_type=APIKey.KeyType.SERVICE,
            key_prefix=full_key[:10],
            key_hash=key_hash,
            scopes=["read:restaurants"],  # wrong scope
            is_active=True,
        )
        resp = self._post([{"restaurant_name": "A", "address": "B", "inspected_at": "2024-01-01"}],
                          key=full_key)
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Batch list / detail
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestBatchViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(email="hd@batch.gov", password="testpass12!")
        self.jurisdiction = _make_jurisdiction(fips_code="55002")
        self.raw_key, _ = _make_api_key(self.user, self.jurisdiction)

    def _auth_header(self):
        return {"HTTP_X_SUBMISSION_KEY": self.raw_key}

    def test_batch_list_empty(self):
        resp = self.client.get("/api/v1/submissions/batches/", **self._auth_header())
        assert resp.status_code == 200
        assert resp.json()["results"] == []

    def test_batch_list_shows_own_batches(self):
        SubmissionBatch.objects.create(jurisdiction=self.jurisdiction, total_rows=5)
        resp = self.client.get("/api/v1/submissions/batches/", **self._auth_header())
        assert resp.json()["count"] == 1

    def test_batch_detail_returns_200(self):
        batch = SubmissionBatch.objects.create(jurisdiction=self.jurisdiction, total_rows=2)
        resp = self.client.get(f"/api/v1/submissions/batches/{batch.pk}/", **self._auth_header())
        assert resp.status_code == 200
        assert resp.json()["id"] == batch.pk

    def test_batch_detail_other_jurisdiction_404(self):
        other_j = _make_jurisdiction(fips_code="55003")
        other_batch = SubmissionBatch.objects.create(jurisdiction=other_j)
        resp = self.client.get(f"/api/v1/submissions/batches/{other_batch.pk}/",
                               **self._auth_header())
        assert resp.status_code == 404

    def test_batch_list_requires_auth(self):
        resp = self.client.get("/api/v1/submissions/batches/")
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Admin views
# ---------------------------------------------------------------------------

@pytest.mark.django_db
class TestAdminViews(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            email="admin@platform.io", password="adminpass12!", is_staff=True
        )
        self.client.force_authenticate(user=self.admin)

    def test_admin_registrations_lists_pending(self):
        _make_jurisdiction(fips_code="66001", status="PENDING")
        _make_jurisdiction(fips_code="66002", status="ACTIVE")
        resp = self.client.get("/api/v1/submissions/admin/registrations/")
        assert resp.status_code == 200
        fips_list = [r["fips_code"] for r in resp.json()["results"]]
        assert "66001" in fips_list
        assert "66002" not in fips_list

    def test_admin_registrations_filter_by_status(self):
        _make_jurisdiction(fips_code="66003", status="ACTIVE")
        resp = self.client.get("/api/v1/submissions/admin/registrations/?status=ACTIVE")
        assert resp.status_code == 200
        fips_list = [r["fips_code"] for r in resp.json()["results"]]
        assert "66003" in fips_list

    def test_approve_creates_api_key_and_sets_active(self):
        acct = _make_jurisdiction(fips_code="66010", status="PENDING")
        resp = self.client.post(
            f"/api/v1/submissions/admin/registrations/{acct.pk}/review/",
            {"action": "approve"}, format="json",
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "ACTIVE"
        assert data["api_key"].startswith("hg_live_")

        acct.refresh_from_db()
        assert acct.status == JurisdictionAccount.Status.ACTIVE
        assert acct.api_key is not None
        assert acct.approved_by == self.admin

    def test_reject_sets_suspended(self):
        acct = _make_jurisdiction(fips_code="66011", status="PENDING")
        resp = self.client.post(
            f"/api/v1/submissions/admin/registrations/{acct.pk}/review/",
            {"action": "reject"}, format="json",
        )
        assert resp.status_code == 200
        acct.refresh_from_db()
        assert acct.status == JurisdictionAccount.Status.SUSPENDED

    def test_invalid_action_returns_400(self):
        acct = _make_jurisdiction(fips_code="66012", status="PENDING")
        resp = self.client.post(
            f"/api/v1/submissions/admin/registrations/{acct.pk}/review/",
            {"action": "banana"}, format="json",
        )
        assert resp.status_code == 400

    def test_admin_requires_staff(self):
        normal = User.objects.create_user(email="norm@x.com", password="normalpass12!")
        self.client.force_authenticate(user=normal)
        resp = self.client.get("/api/v1/submissions/admin/registrations/")
        assert resp.status_code == 403

    def test_admin_unauthenticated_returns_401(self):
        self.client.force_authenticate(user=None)
        resp = self.client.get("/api/v1/submissions/admin/registrations/")
        assert resp.status_code == 401
