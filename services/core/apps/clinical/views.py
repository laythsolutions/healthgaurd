"""
Clinical reporting API views.

Institution API key endpoints (header: X-Institution-Key):
    POST /api/v1/clinical/cases/              — submit anonymized case
    GET  /api/v1/clinical/cases/              — list own institution's cases

Health dept / admin:
    GET  /api/v1/clinical/cases/              — list all (with filters)
    GET  /api/v1/clinical/cases/{id}/         — detail
    GET  /api/v1/clinical/investigations/     — list investigations
    POST /api/v1/clinical/investigations/     — create investigation
    PATCH /api/v1/clinical/investigations/{id}/ — update
"""

import hashlib
import hmac

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ClinicalCase, OutbreakInvestigation, ReportingInstitution
from .serializers import (
    ClinicalCaseSerializer,
    ClinicalCaseSubmissionSerializer,
    OutbreakInvestigationSerializer,
)


def _resolve_institution(request):
    """Resolve and validate the reporting institution from API key header."""
    raw_key = request.headers.get("X-Institution-Key", "")
    if not raw_key:
        return None
    salt = getattr(settings, "ANONYMIZATION_SALT", "").encode()
    key_hash = hmac.new(salt, raw_key.encode(), hashlib.sha256).hexdigest()
    return ReportingInstitution.objects.filter(api_key_hash=key_hash, is_active=True).first()


class IsHealthDeptOrAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff or getattr(request.user, "role", "") in (
            "health_dept", "admin"
        )


class ClinicalCaseView(APIView):
    """Submit and list clinical cases."""

    def _check_auth(self, request):
        """Returns (institution, user, error_response)."""
        institution = _resolve_institution(request)
        if institution:
            return institution, None, None

        # Fall back to JWT auth for health dept users
        if request.user and request.user.is_authenticated and (
            request.user.is_staff
            or getattr(request.user, "role", "") in ("health_dept", "admin")
        ):
            return None, request.user, None

        return None, None, Response(
            {"detail": "Authentication required. Provide X-Institution-Key or a valid JWT."},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    def post(self, request):
        institution, user, err = self._check_auth(request)
        if err:
            return err

        serializer = ClinicalCaseSubmissionSerializer(
            data=request.data,
            context={"institution": institution, "user": user},
        )
        serializer.is_valid(raise_exception=True)
        case = serializer.save()

        # Write audit log
        from apps.privacy.services import ConsentManager
        ConsentManager.log_access(
            action="write",
            data_categories=["health", "location", "demographics"],
            purpose="clinical_case_submission",
            subject_hash=case.subject_hash,
            performed_by_system=institution.name if institution else "api",
            endpoint=request.path,
            record_type="ClinicalCase",
            record_id=case.pk,
        )

        return Response(
            ClinicalCaseSerializer(case).data,
            status=status.HTTP_201_CREATED,
        )

    def get(self, request):
        institution, user, err = self._check_auth(request)
        if err:
            return err

        qs = ClinicalCase.objects.prefetch_related("exposures").order_by("-onset_date", "-created_at")

        # Institutions only see their own submissions
        if institution:
            qs = qs.filter(reporting_institution=institution)

        # Health dept can filter
        if user:
            pathogen = request.query_params.get("pathogen")
            if pathogen:
                qs = qs.filter(pathogen__icontains=pathogen)

            since = request.query_params.get("since")
            if since:
                qs = qs.filter(onset_date__gte=since)

            investigation = request.query_params.get("investigation")
            if investigation:
                qs = qs.filter(investigation_id=investigation)

        page_size = min(int(request.query_params.get("page_size", 50)), 200)
        offset = int(request.query_params.get("offset", 0))
        total = qs.count()
        serializer = ClinicalCaseSerializer(qs[offset: offset + page_size], many=True)
        return Response({"total": total, "offset": offset, "results": serializer.data})


class ClinicalCaseDetailView(APIView):
    permission_classes = [IsHealthDeptOrAdmin]

    def get(self, request, pk):
        try:
            case = ClinicalCase.objects.prefetch_related("exposures").get(pk=pk)
        except ClinicalCase.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ClinicalCaseSerializer(case).data)


class OutbreakInvestigationView(APIView):
    permission_classes = [IsHealthDeptOrAdmin]

    def get(self, request):
        qs = OutbreakInvestigation.objects.annotate_case_count() if hasattr(
            OutbreakInvestigation.objects, "annotate_case_count"
        ) else OutbreakInvestigation.objects.prefetch_related("cases")

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        serializer = OutbreakInvestigationSerializer(qs.order_by("-opened_at"), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = OutbreakInvestigationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        investigation = serializer.save(lead_investigator=request.user)
        return Response(
            OutbreakInvestigationSerializer(investigation).data,
            status=status.HTTP_201_CREATED,
        )


class OutbreakInvestigationDetailView(APIView):
    permission_classes = [IsHealthDeptOrAdmin]

    def get(self, request, pk):
        try:
            investigation = OutbreakInvestigation.objects.prefetch_related("cases").get(pk=pk)
        except OutbreakInvestigation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(OutbreakInvestigationSerializer(investigation).data)

    def patch(self, request, pk):
        try:
            investigation = OutbreakInvestigation.objects.get(pk=pk)
        except OutbreakInvestigation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OutbreakInvestigationSerializer(
            investigation, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InvestigationStatsView(APIView):
    """
    GET /api/v1/clinical/investigations/{id}/stats/
    Returns odds ratios and symptom frequencies for an investigation.
    Health dept / staff only.
    """
    permission_classes = [IsHealthDeptOrAdmin]

    def get(self, request, pk):
        try:
            OutbreakInvestigation.objects.get(pk=pk)
        except OutbreakInvestigation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        from apps.clinical.stats import analyze_investigation
        result = analyze_investigation(investigation_id=pk)
        return Response(result)


class InvestigationTracebackView(APIView):
    """
    GET /api/v1/clinical/investigations/{id}/traceback/
    Returns a supply-chain traceback graph for an investigation.
    Health dept / staff only.
    """
    permission_classes = [IsHealthDeptOrAdmin]

    def get(self, request, pk):
        try:
            OutbreakInvestigation.objects.get(pk=pk)
        except OutbreakInvestigation.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        from apps.clinical.traceback import build_traceback
        graph = build_traceback(investigation_id=pk)
        return Response(graph)


class GeohashStatsView(APIView):
    """
    GET /api/v1/clinical/stats/geohash/?prefix=9q5f&pathogen=Salmonella&days=30
    Ad-hoc analysis for an emerging geohash cluster (no formal investigation required).
    Health dept / staff only.
    """
    permission_classes = [IsHealthDeptOrAdmin]

    def get(self, request):
        prefix = request.query_params.get("prefix", "").strip()
        if len(prefix) < 3:
            return Response(
                {"detail": "Provide a geohash prefix of at least 3 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        pathogen = request.query_params.get("pathogen", "")
        try:
            lookback = min(int(request.query_params.get("days", 30)), 90)
        except (ValueError, TypeError):
            lookback = 30

        from apps.clinical.stats import analyze_geohash_cluster
        result = analyze_geohash_cluster(
            geohash_prefix=prefix,
            pathogen=pathogen,
            lookback_days=lookback,
        )
        return Response(result)
