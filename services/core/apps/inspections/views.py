"""
Inspection API views.

Public (no auth):
    GET /api/v1/inspections/                             — list, filter by restaurant/grade/date
    GET /api/v1/inspections/{id}/                        — full detail with violations
    GET /api/v1/inspections/restaurant/{restaurant_id}/  — history for a single establishment

Health dept / admin (requires 'health_dept' or 'admin' role):
    POST  /api/v1/inspections/                           — submit inspection record
    PATCH /api/v1/inspections/{id}/                      — update
    GET   /api/v1/inspections/export/                    — CSV export of inspections
    GET   /api/v1/inspections/schedule/                  — list scheduled inspections
    POST  /api/v1/inspections/schedule/                  — create scheduled inspection
    PATCH /api/v1/inspections/schedule/{id}/             — update schedule status
"""

import csv

from django.http import StreamingHttpResponse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import filters, generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Inspection, InspectionSchedule
from .serializers import (
    InspectionDetailSerializer,
    InspectionListSerializer,
    InspectionScheduleSerializer,
    InspectionWriteSerializer,
)


class IsHealthDeptOrAdmin(IsAuthenticated):
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.is_staff or getattr(request.user, "role", "") in (
            "health_dept", "admin"
        )


class InspectionListCreateView(APIView):
    """List (public) and create (health dept/admin) inspections."""

    def get_permissions(self):
        if self.request.method == "GET":
            return [AllowAny()]
        return [IsHealthDeptOrAdmin()]

    @method_decorator(cache_page(60 * 10))
    def get(self, request):
        qs = (
            Inspection.objects.select_related("restaurant")
            .prefetch_related("violations")
            .order_by("-inspected_at")
        )

        restaurant_id = request.query_params.get("restaurant")
        if restaurant_id:
            qs = qs.filter(restaurant_id=restaurant_id)

        grade = request.query_params.get("grade")
        if grade:
            qs = qs.filter(grade=grade.upper())

        jurisdiction = request.query_params.get("jurisdiction")
        if jurisdiction:
            qs = qs.filter(source_jurisdiction__icontains=jurisdiction)

        since = request.query_params.get("since")
        if since:
            qs = qs.filter(inspected_at__date__gte=since)

        closed = request.query_params.get("closed")
        if closed is not None:
            qs = qs.filter(closed=closed.lower() == "true")

        page_size = min(int(request.query_params.get("page_size", 50)), 200)
        offset = int(request.query_params.get("offset", 0))
        total = qs.count()

        serializer = InspectionListSerializer(qs[offset:offset + page_size], many=True)
        return Response({"total": total, "offset": offset, "results": serializer.data})

    def post(self, request):
        serializer = InspectionWriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        inspection = serializer.save()
        return Response(
            InspectionDetailSerializer(inspection).data,
            status=status.HTTP_201_CREATED,
        )


class InspectionDetailView(APIView):
    """Public inspection detail."""

    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 10))
    def get(self, request, pk):
        try:
            inspection = Inspection.objects.select_related("restaurant").prefetch_related(
                "violations"
            ).get(pk=pk)
        except Inspection.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(InspectionDetailSerializer(inspection).data)

    def patch(self, request, pk):
        if not (request.user.is_authenticated and (
            request.user.is_staff or getattr(request.user, "role", "") in ("health_dept", "admin")
        )):
            return Response({"detail": "Forbidden."}, status=status.HTTP_403_FORBIDDEN)

        try:
            inspection = Inspection.objects.get(pk=pk)
        except Inspection.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InspectionWriteSerializer(inspection, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        inspection = serializer.save()
        return Response(InspectionDetailSerializer(inspection).data)


class RestaurantInspectionHistoryView(APIView):
    """Public inspection history for a single establishment."""

    permission_classes = [AllowAny]

    @method_decorator(cache_page(60 * 10))
    def get(self, request, restaurant_id):
        qs = (
            Inspection.objects.filter(restaurant_id=restaurant_id)
            .prefetch_related("violations")
            .order_by("-inspected_at")
        )

        limit = min(int(request.query_params.get("limit", 20)), 100)
        serializer = InspectionDetailSerializer(qs[:limit], many=True)
        return Response(serializer.data)


# ---------------------------------------------------------------------------
# Health dept portal views
# ---------------------------------------------------------------------------


class InspectionScheduleView(APIView):
    """List and create scheduled inspections (health dept / admin only)."""

    permission_classes = [IsHealthDeptOrAdmin]

    def get(self, request):
        qs = (
            InspectionSchedule.objects.select_related("restaurant")
            .order_by("scheduled_date")
        )

        status_filter = request.query_params.get("status")
        if status_filter:
            qs = qs.filter(status=status_filter)

        since = request.query_params.get("since")
        if since:
            qs = qs.filter(scheduled_date__gte=since)

        until = request.query_params.get("until")
        if until:
            qs = qs.filter(scheduled_date__lte=until)

        jurisdiction = request.query_params.get("jurisdiction")
        if jurisdiction:
            qs = qs.filter(jurisdiction__icontains=jurisdiction)

        page_size = min(int(request.query_params.get("page_size", 50)), 200)
        offset = int(request.query_params.get("offset", 0))
        total = qs.count()

        serializer = InspectionScheduleSerializer(qs[offset: offset + page_size], many=True)
        return Response({"total": total, "offset": offset, "results": serializer.data})

    def post(self, request):
        serializer = InspectionScheduleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save(created_by=request.user)
        return Response(
            InspectionScheduleSerializer(schedule).data,
            status=status.HTTP_201_CREATED,
        )


class InspectionScheduleDetailView(APIView):
    """Update a single scheduled inspection (health dept / admin only)."""

    permission_classes = [IsHealthDeptOrAdmin]

    def _get(self, pk):
        try:
            return InspectionSchedule.objects.select_related("restaurant").get(pk=pk), None
        except InspectionSchedule.DoesNotExist:
            return None, Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk):
        obj, err = self._get(pk)
        if err:
            return err
        return Response(InspectionScheduleSerializer(obj).data)

    def patch(self, request, pk):
        obj, err = self._get(pk)
        if err:
            return err
        serializer = InspectionScheduleSerializer(obj, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class InspectionExportView(APIView):
    """
    CSV export of inspections (health dept / admin only).

    GET /api/v1/inspections/export/?since=YYYY-MM-DD&jurisdiction=...
    """

    permission_classes = [IsHealthDeptOrAdmin]

    def get(self, request):
        qs = (
            Inspection.objects.select_related("restaurant")
            .prefetch_related("violations")
            .order_by("-inspected_at")
        )

        since = request.query_params.get("since")
        if since:
            qs = qs.filter(inspected_at__date__gte=since)

        jurisdiction = request.query_params.get("jurisdiction")
        if jurisdiction:
            qs = qs.filter(source_jurisdiction__icontains=jurisdiction)

        grade = request.query_params.get("grade")
        if grade:
            qs = qs.filter(grade=grade.upper())

        def generate():
            header = [
                "id", "restaurant", "address", "city", "state",
                "inspected_at", "grade", "score", "passed", "closed",
                "critical_violations", "total_violations", "jurisdiction",
            ]
            yield ",".join(header) + "\n"

            for insp in qs.iterator(chunk_size=500):
                critical = insp.violations.filter(severity="critical").count()
                total = insp.violations.count()
                row = [
                    str(insp.pk),
                    f'"{insp.restaurant.name}"',
                    f'"{insp.restaurant.address}"',
                    insp.restaurant.city,
                    insp.restaurant.state,
                    insp.inspected_at.isoformat(),
                    insp.grade,
                    str(insp.score or ""),
                    str(insp.passed or ""),
                    str(insp.closed),
                    str(critical),
                    str(total),
                    insp.source_jurisdiction,
                ]
                yield ",".join(row) + "\n"

        filename = f"inspections_{timezone.now().date()}.csv"
        response = StreamingHttpResponse(generate(), content_type="text/csv")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response
