"""
Privacy & Consent API views.

Endpoints:
    GET  /api/v1/privacy/consent/{subject_hash}/      — full consent summary
    GET  /api/v1/privacy/consent/{subject_hash}/{scope}/ — single scope status
    POST /api/v1/privacy/consent/{subject_hash}/      — grant or revoke a scope
    GET  /api/v1/privacy/audit/                       — audit log (admin only)
    POST /api/v1/privacy/anonymize/test/              — test anonymization rules
"""

from rest_framework import status
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import ConsentRecord, ConsentScope, DataSubject
from .serializers import (
    AuditLogSerializer,
    ConsentRecordSerializer,
    ConsentUpdateSerializer,
    DataSubjectConsentSummarySerializer,
)
from .services import AnonymizationService, ConsentManager


class ConsentSummaryView(APIView):
    """GET/POST consent for a data subject."""

    permission_classes = [IsAuthenticated]

    def get(self, request, subject_hash):
        try:
            subject = DataSubject.objects.prefetch_related("consent_records").get(
                subject_hash=subject_hash
            )
        except DataSubject.DoesNotExist:
            return Response(
                {"detail": "Data subject not found."},
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = DataSubjectConsentSummarySerializer(subject)
        return Response(serializer.data)

    def post(self, request, subject_hash):
        serializer = ConsentUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        ip = request.META.get("REMOTE_ADDR", "")
        ua = request.META.get("HTTP_USER_AGENT", "")

        if data["status"] == ConsentRecord.Status.GRANTED:
            ConsentManager.grant(
                subject_hash=subject_hash,
                scope=data["scope"],
                source_system="api",
                legal_basis=data.get("legal_basis", "consent"),
                recorded_by_user=request.user,
                ip=ip,
                user_agent=ua,
                notes=data.get("notes", ""),
            )
        else:
            ConsentManager.revoke(
                subject_hash=subject_hash,
                scope=data["scope"],
                source_system="api",
                recorded_by_user=request.user,
                notes=data.get("notes", ""),
            )

        return Response(
            {"detail": f"Consent {data['status']} for scope '{data['scope']}'."},
            status=status.HTTP_200_OK,
        )


class ConsentScopeView(APIView):
    """GET a single scope's current consent status."""

    permission_classes = [IsAuthenticated]

    def get(self, request, subject_hash, scope):
        if scope not in dict(ConsentScope.choices):
            return Response(
                {"detail": f"Unknown scope '{scope}'."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        current = ConsentManager.get_current_status(subject_hash, scope)
        if current is None:
            return Response(
                {"subject_hash": subject_hash, "scope": scope, "status": "unknown"},
                status=status.HTTP_200_OK,
            )
        return Response({"subject_hash": subject_hash, "scope": scope, "status": current})


class ConsentHistoryView(APIView):
    """GET full consent event history for a subject+scope (admin)."""

    permission_classes = [IsAdminUser]

    def get(self, request, subject_hash, scope):
        try:
            subject = DataSubject.objects.get(subject_hash=subject_hash)
        except DataSubject.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        records = ConsentRecord.objects.filter(subject=subject, scope=scope).order_by(
            "-created_at"
        )
        serializer = ConsentRecordSerializer(records, many=True)
        return Response(serializer.data)


class AuditLogView(APIView):
    """GET audit log entries (admin only)."""

    permission_classes = [IsAdminUser]

    def get(self, request):
        from .models import DataProcessingAuditLog

        qs = DataProcessingAuditLog.objects.all().order_by("-created_at")

        # Optional filters
        subject_hash = request.query_params.get("subject_hash")
        action = request.query_params.get("action")
        record_type = request.query_params.get("record_type")

        if subject_hash:
            qs = qs.filter(subject__subject_hash=subject_hash)
        if action:
            qs = qs.filter(action=action)
        if record_type:
            qs = qs.filter(record_type=record_type)

        # Simple pagination
        page_size = min(int(request.query_params.get("page_size", 50)), 200)
        offset = int(request.query_params.get("offset", 0))
        total = qs.count()
        serializer = AuditLogSerializer(qs[offset : offset + page_size], many=True)
        return Response({"total": total, "offset": offset, "results": serializer.data})


class AnonymizeTestView(APIView):
    """
    POST a sample payload to preview anonymization output (development helper).
    Returns both the original and anonymized versions.
    Only accessible to admin users.
    """

    permission_classes = [IsAdminUser]

    def post(self, request):
        raw = request.data
        svc = AnonymizationService()

        result = {}

        if "text" in raw:
            result["stripped_text"] = svc.strip_pii(str(raw["text"]))

        if "latitude" in raw and "longitude" in raw:
            result["geohash_p6"] = svc.encode_geohash(
                float(raw["latitude"]), float(raw["longitude"]), precision=6
            )
            result["geohash_p5"] = svc.encode_geohash(
                float(raw["latitude"]), float(raw["longitude"]), precision=5
            )

        if "zip_code" in raw:
            result["zip3"] = svc.truncate_zip(str(raw["zip_code"]))

        if "age" in raw:
            result["age_range"] = svc.age_to_range(int(raw["age"]))

        if "identifier" in raw:
            result["subject_hash"] = svc.hash_identifier(
                str(raw["identifier"]),
                namespace=raw.get("namespace", ""),
            )

        return Response(result)
