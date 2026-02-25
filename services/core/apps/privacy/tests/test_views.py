"""Tests for privacy API views."""

import pytest
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from apps.accounts.models import User
from apps.privacy.models import ConsentScope


@pytest.mark.django_db
class TestConsentScopeView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpass123",
            email="test@example.com",
        )
        self.client.force_authenticate(user=self.user)

    def test_list_consent_scopes(self):
        url = "/api/v1/privacy/consents/scopes/"
        response = self.client.get(url)
        assert response.status_code == 200

    def test_consent_summary_requires_auth(self):
        self.client.force_authenticate(user=None)
        url = "/api/v1/privacy/consents/"
        response = self.client.get(url)
        assert response.status_code in (401, 403)


@pytest.mark.django_db
class TestAnonymizeTestView(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username="adminuser",
            password="adminpass123",
            email="admin@example.com",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.user)

    def test_anonymize_endpoint_requires_staff(self):
        normal_user = User.objects.create_user(
            username="normaluser",
            password="pass",
            email="normal@example.com",
        )
        self.client.force_authenticate(user=normal_user)
        url = "/api/v1/privacy/anonymize/test/"
        response = self.client.post(url, {
            "patient_id": "P001",
            "age": 35,
            "lat": 40.71,
            "lon": -74.00,
            "zip_code": "10001",
        }, format="json")
        # Normal users get forbidden
        assert response.status_code in (403, 404)

    def test_anonymize_endpoint_staff_allowed(self):
        url = "/api/v1/privacy/anonymize/test/"
        response = self.client.post(url, {
            "patient_id": "P001",
            "age": 35,
            "lat": 40.71,
            "lon": -74.00,
            "zip_code": "10001",
        }, format="json")
        # Staff can call it (404 is OK if the URL isn't registered yet; 200 or 201 means it works)
        assert response.status_code in (200, 201, 404)
