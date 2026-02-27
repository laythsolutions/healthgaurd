"""
Views for the jurisdiction submission API.

Public (unauthenticated)
────────────────────────
POST  /register/                 — JurisdictionRegisterView

Authenticated (X-Submission-Key)
─────────────────────────────────
POST  /inspections/              — SubmitInspectionsView
GET   /batches/                  — BatchListView
GET   /batches/<pk>/             — BatchDetailView

Admin only (IsAdminUser / staff JWT)
─────────────────────────────────────
GET   /admin/registrations/      — AdminRegistrationListView
POST  /admin/registrations/<pk>/review/  — AdminRegistrationReviewView
"""

import logging

from django.utils import timezone
from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from apps.accounts.models import APIKey
from .auth import SubmissionAPIKeyAuthentication
from .models import JurisdictionAccount, SubmissionBatch
from .serializers import (
    BatchStatusSerializer,
    JurisdictionAccountSerializer,
    JurisdictionRegistrationSerializer,
    SubmitInspectionsSerializer,
)
from .tasks import process_submission_batch

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Public
# ---------------------------------------------------------------------------

class JurisdictionRegisterView(APIView):
    """
    POST /api/v1/submissions/register/

    Public registration form.  Creates a JurisdictionAccount with
    status=PENDING awaiting admin review.
    """

    permission_classes = [AllowAny]
    throttle_classes   = [ScopedRateThrottle]
    throttle_scope     = "submission_register"

    def post(self, request):
        serializer = JurisdictionRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        account = serializer.save()
        logger.info(
            "[submissions] New registration: %s (%s)", account.name, account.fips_code
        )
        return Response(
            {"id": account.pk, "status": account.status, "fips_code": account.fips_code},
            status=status.HTTP_201_CREATED,
        )


# ---------------------------------------------------------------------------
# Authenticated — X-Submission-Key
# ---------------------------------------------------------------------------

class SubmitInspectionsView(APIView):
    """
    POST /api/v1/submissions/inspections/

    Accepts a JSON body ``{"records": [...]}`` (max 500 rows).
    Creates a SubmissionBatch and enqueues async processing.
    Returns 202 Accepted with batch_id.
    """

    authentication_classes = [SubmissionAPIKeyAuthentication]
    permission_classes     = [IsAuthenticated]
    throttle_classes       = [ScopedRateThrottle]
    throttle_scope         = "submission_bulk"

    def post(self, request):
        # api_key stored as request.auth by SubmissionAPIKeyAuthentication
        api_key = request.auth
        try:
            jurisdiction = api_key.jurisdiction_account
        except JurisdictionAccount.DoesNotExist:
            return Response(
                {"detail": "API key is not linked to any jurisdiction account."},
                status=status.HTTP_403_FORBIDDEN,
            )

        if jurisdiction.status != JurisdictionAccount.Status.ACTIVE:
            return Response(
                {"detail": "Jurisdiction account is not active."},
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = SubmitInspectionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        records = serializer.validated_data["records"]

        batch = SubmissionBatch.objects.create(
            jurisdiction=jurisdiction,
            total_rows=len(records),
            raw_payload=records,
        )
        process_submission_batch.delay(batch.pk)

        logger.info(
            "[submissions] Batch %d queued for %s (%d rows)",
            batch.pk, jurisdiction.name, len(records),
        )
        return Response(
            {
                "batch_id":   batch.pk,
                "status":     batch.status,
                "total_rows": batch.total_rows,
            },
            status=status.HTTP_202_ACCEPTED,
        )


class BatchListView(generics.ListAPIView):
    """
    GET /api/v1/submissions/batches/

    Lists own jurisdiction's batches, newest first.
    """

    authentication_classes = [SubmissionAPIKeyAuthentication]
    permission_classes     = [IsAuthenticated]
    serializer_class       = BatchStatusSerializer

    def get_queryset(self):
        api_key = self.request.auth
        try:
            jurisdiction = api_key.jurisdiction_account
        except JurisdictionAccount.DoesNotExist:
            return SubmissionBatch.objects.none()
        return SubmissionBatch.objects.filter(jurisdiction=jurisdiction).select_related(
            "jurisdiction"
        )


class BatchDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/submissions/batches/<pk>/

    Returns full batch status including row-level errors.
    """

    authentication_classes = [SubmissionAPIKeyAuthentication]
    permission_classes     = [IsAuthenticated]
    serializer_class       = BatchStatusSerializer

    def get_queryset(self):
        api_key = self.request.auth
        try:
            jurisdiction = api_key.jurisdiction_account
        except JurisdictionAccount.DoesNotExist:
            return SubmissionBatch.objects.none()
        return SubmissionBatch.objects.filter(jurisdiction=jurisdiction).select_related(
            "jurisdiction"
        )


# ---------------------------------------------------------------------------
# Admin
# ---------------------------------------------------------------------------

class AdminRegistrationListView(generics.ListAPIView):
    """
    GET /api/v1/submissions/admin/registrations/

    Lists all PENDING registrations for admin review.
    """

    permission_classes = [IsAdminUser]
    serializer_class   = JurisdictionAccountSerializer

    def get_queryset(self):
        status_filter = self.request.query_params.get("status", "PENDING")
        return JurisdictionAccount.objects.filter(status=status_filter).order_by("created_at")


class AdminRegistrationReviewView(APIView):
    """
    POST /api/v1/submissions/admin/registrations/<pk>/review/

    Body: ``{"action": "approve"|"reject", "notes": "..."}``

    On approve:
      1. Creates an APIKey with scopes=['submissions:write']
      2. Links it to the JurisdictionAccount
      3. Sets status=ACTIVE + stamps approved_by/approved_at
      4. Returns the one-time key value (hg_live_...)

    On reject: sets status=SUSPENDED.
    """

    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            account = JurisdictionAccount.objects.get(pk=pk)
        except JurisdictionAccount.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        action = (request.data.get("action") or "").lower()
        if action not in ("approve", "reject"):
            return Response(
                {"detail": "action must be 'approve' or 'reject'."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if action == "reject":
            account.status = JurisdictionAccount.Status.SUSPENDED
            account.save(update_fields=["status"])
            return Response(
                {"id": account.pk, "status": account.status},
                status=status.HTTP_200_OK,
            )

        # approve
        if account.status == JurisdictionAccount.Status.ACTIVE:
            return Response(
                {"detail": "Account is already active."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        full_key, key_hash = APIKey.generate_key()
        api_key = APIKey.objects.create(
            user=request.user,
            name=f"Submission key — {account.name}",
            key_type=APIKey.KeyType.SERVICE,
            key_prefix=full_key[:10],
            key_hash=key_hash,
            scopes=["submissions:write"],
            is_active=True,
        )

        account.api_key     = api_key
        account.status      = JurisdictionAccount.Status.ACTIVE
        account.approved_by = request.user
        account.approved_at = timezone.now()
        account.save(update_fields=["api_key", "status", "approved_by", "approved_at"])

        logger.info(
            "[submissions] Approved jurisdiction %s (%s) by %s",
            account.name, account.fips_code, request.user.email,
        )

        return Response(
            {
                "id":      account.pk,
                "status":  account.status,
                "api_key": full_key,   # shown once — store securely
            },
            status=status.HTTP_200_OK,
        )
