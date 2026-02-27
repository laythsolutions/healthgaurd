"""Tests for JurisdictionAccount and SubmissionBatch models."""

import pytest
from django.test import TestCase

from apps.submissions.models import JurisdictionAccount, SubmissionBatch


@pytest.mark.django_db
class TestJurisdictionAccount(TestCase):
    def _make(self, **kwargs):
        defaults = dict(
            name="Cook County HD",
            fips_code="17031",
            state="IL",
            contact_email="hd@cookcounty.gov",
        )
        defaults.update(kwargs)
        return JurisdictionAccount.objects.create(**defaults)

    def test_create(self):
        acct = self._make()
        assert acct.pk is not None
        assert acct.status == JurisdictionAccount.Status.PENDING

    def test_str(self):
        acct = self._make()
        assert "Cook County HD" in str(acct)
        assert "17031" in str(acct)

    def test_fips_code_unique(self):
        from django.db import IntegrityError
        self._make(fips_code="99999")
        with self.assertRaises(IntegrityError):
            self._make(fips_code="99999")

    def test_schema_map_default_is_empty_dict(self):
        acct = self._make()
        assert acct.schema_map == {}

    def test_score_system_default(self):
        acct = self._make()
        assert acct.score_system == JurisdictionAccount.ScoreSystem.SCORE_0_100

    def test_status_choices(self):
        choices = [c[0] for c in JurisdictionAccount.Status.choices]
        assert "PENDING" in choices
        assert "ACTIVE" in choices
        assert "SUSPENDED" in choices


@pytest.mark.django_db
class TestSubmissionBatch(TestCase):
    def _make_jurisdiction(self):
        return JurisdictionAccount.objects.create(
            name="Test HD", fips_code="00001", state="TX",
            contact_email="hd@test.gov",
        )

    def _make_batch(self, **kwargs):
        j = self._make_jurisdiction()
        defaults = dict(jurisdiction=j, total_rows=3, raw_payload=[{"a": 1}])
        defaults.update(kwargs)
        return SubmissionBatch.objects.create(**defaults)

    def test_create(self):
        batch = self._make_batch()
        assert batch.pk is not None
        assert batch.status == SubmissionBatch.Status.PENDING

    def test_str(self):
        batch = self._make_batch()
        assert str(batch.pk) in str(batch)

    def test_defaults(self):
        batch = self._make_batch()
        assert batch.created_count == 0
        assert batch.skipped_count == 0
        assert batch.error_count == 0
        assert batch.row_errors == []
        assert batch.webhook_delivered is False

    def test_ordering_newest_first(self):
        j = self._make_jurisdiction()
        b1 = SubmissionBatch.objects.create(jurisdiction=j)
        b2 = SubmissionBatch.objects.create(jurisdiction=j)
        qs = list(SubmissionBatch.objects.filter(jurisdiction=j))
        # newest first
        assert qs[0].pk == b2.pk
        assert qs[1].pk == b1.pk
