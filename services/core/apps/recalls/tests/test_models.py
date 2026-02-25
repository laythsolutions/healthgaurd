"""Tests for the Recalls app models."""

import pytest
from datetime import date
from django.test import TestCase

from apps.recalls.models import Recall, RecallProduct, RecallAcknowledgment


@pytest.mark.django_db
class TestRecallModel(TestCase):
    def _make_recall(self, **kwargs) -> Recall:
        defaults = dict(
            source=Recall.Source.FDA,
            external_id="FDA-TEST-001",
            title="Test Recall",
            reason="Possible contamination",
            recalling_firm="Test Corp",
            status=Recall.Status.ACTIVE,
        )
        defaults.update(kwargs)
        return Recall.objects.create(**defaults)

    def test_create_recall(self):
        recall = self._make_recall()
        assert recall.pk is not None
        assert recall.status == Recall.Status.ACTIVE

    def test_recall_str(self):
        recall = self._make_recall()
        assert "FDA" in str(recall).upper() or "Test" in str(recall)

    def test_external_id_uniqueness(self):
        self._make_recall(external_id="UNIQUE-001")
        from django.db import IntegrityError
        with pytest.raises(IntegrityError):
            self._make_recall(external_id="UNIQUE-001")

    def test_affected_states_default_list(self):
        recall = self._make_recall(external_id="STATES-001")
        assert isinstance(recall.affected_states, list)

    def test_affected_states_populated(self):
        recall = self._make_recall(
            external_id="STATES-002",
            affected_states=["CA", "NY", "TX"],
        )
        assert "CA" in recall.affected_states
        assert len(recall.affected_states) == 3

    def test_recall_product_attached(self):
        recall = self._make_recall(external_id="PROD-001")
        product = RecallProduct.objects.create(
            recall=recall,
            product_description="Frozen Chicken 1lb",
            brand_name="FarmFresh",
            upc_codes=["012345678901"],
            lot_numbers=["LOT-A1"],
            best_by_dates=["2026-06-01"],
        )
        assert product.recall_id == recall.pk
        assert recall.products.count() == 1

    def test_classification_choices(self):
        recall = self._make_recall(
            external_id="CLASS-001",
            classification=Recall.Classification.CLASS_I,
        )
        assert recall.classification == "I"


@pytest.mark.django_db
class TestRecallViews(TestCase):
    def setUp(self):
        from rest_framework.test import APIClient
        self.client = APIClient()

    def _make_recall(self, external_id="V-001"):
        return Recall.objects.create(
            source=Recall.Source.FDA,
            external_id=external_id,
            title="Test Recall",
            reason="Contamination risk",
            recalling_firm="Corp Inc",
            status=Recall.Status.ACTIVE,
            classification=Recall.Classification.CLASS_I,
            affected_states=["CA"],
        )

    def test_public_list_no_auth(self):
        self._make_recall()
        response = self.client.get("/api/v1/recalls/")
        assert response.status_code == 200
        data = response.json()
        assert "results" in data or isinstance(data, list)

    def test_public_detail_no_auth(self):
        recall = self._make_recall("V-002")
        response = self.client.get(f"/api/v1/recalls/{recall.pk}/")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == recall.pk

    def test_list_filter_by_status(self):
        self._make_recall("ACTIVE-1")
        Recall.objects.create(
            source=Recall.Source.FDA,
            external_id="COMPLETED-1",
            title="Old Recall",
            reason="Resolved",
            recalling_firm="Corp",
            status=Recall.Status.COMPLETED,
        )
        response = self.client.get("/api/v1/recalls/?status=active")
        data = response.json()
        results = data.get("results", data)
        for r in results:
            assert r["status"] == "active"

    def test_list_filter_by_source(self):
        self._make_recall("FDA-FILT-1")
        Recall.objects.create(
            source=Recall.Source.USDA_FSIS,
            external_id="USDA-FILT-1",
            title="USDA Recall",
            reason="Contamination",
            recalling_firm="Meat Co",
            status=Recall.Status.ACTIVE,
        )
        response = self.client.get("/api/v1/recalls/?source=usda_fsis")
        data = response.json()
        results = data.get("results", data)
        for r in results:
            assert r["source"] == "usda_fsis"
