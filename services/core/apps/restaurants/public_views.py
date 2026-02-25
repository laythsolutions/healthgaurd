"""
Public (no-auth) restaurant endpoints consumed by the public web frontend.

GET /api/v1/public/restaurants/          — search + paginate
GET /api/v1/public/restaurants/{pk}/     — single restaurant with current_grade
"""

from django.db.models import OuterRef, Subquery
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, ScopedRateThrottle
from rest_framework.views import APIView

from .models import Restaurant


def _annotate_current_grade(qs):
    """Annotate queryset with current_grade from the latest inspection."""
    from apps.inspections.models import Inspection

    latest_grade = (
        Inspection.objects.filter(restaurant=OuterRef("pk"))
        .order_by("-inspected_at")
        .values("grade")[:1]
    )
    return qs.annotate(current_grade=Subquery(latest_grade))


def _serialize(restaurant) -> dict:
    return {
        "id": restaurant.pk,
        "name": restaurant.name,
        "code": restaurant.code,
        "address": restaurant.address,
        "city": restaurant.city,
        "state": restaurant.state,
        "zip_code": restaurant.zip_code,
        "latitude": float(restaurant.latitude) if restaurant.latitude else None,
        "longitude": float(restaurant.longitude) if restaurant.longitude else None,
        "cuisine_type": restaurant.cuisine_type,
        "current_grade": getattr(restaurant, "current_grade", None) or "",
        "last_inspection_date": (
            restaurant.last_inspection_date.isoformat()
            if restaurant.last_inspection_date
            else None
        ),
        "last_inspection_score": restaurant.last_inspection_score,
        "compliance_score": float(restaurant.compliance_score or 0),
        "status": restaurant.status,
        "health_department_id": restaurant.health_department_id,
    }


class PublicRestaurantListView(APIView):
    """
    Public paginated search over restaurants.

    Query params:
        search      — name / address full-text fragment
        city        — exact city (case-insensitive)
        state       — two-letter state code
        grade       — A / B / C / P / X (filters on last inspection grade)
        page_size   — default 20, max 100
        offset      — default 0
    """

    permission_classes = [AllowAny]
    throttle_classes   = [ScopedRateThrottle]
    throttle_scope     = "public_data"

    @method_decorator(cache_page(60))
    def get(self, request):
        qs = Restaurant.objects.all()

        search = request.query_params.get("search")
        if search:
            qs = qs.filter(name__icontains=search) | Restaurant.objects.filter(
                address__icontains=search
            )
            # Re-merge with correct base
            qs = Restaurant.objects.filter(
                pk__in=qs.values_list("pk", flat=True)
            )

        city = request.query_params.get("city")
        if city:
            qs = qs.filter(city__iexact=city)

        state = request.query_params.get("state")
        if state:
            qs = qs.filter(state__iexact=state)

        qs = _annotate_current_grade(qs)

        grade = request.query_params.get("grade")
        if grade:
            qs = qs.filter(current_grade=grade.upper())

        qs = qs.order_by("name")

        page_size = min(int(request.query_params.get("page_size", 20)), 100)
        offset = int(request.query_params.get("offset", 0))
        total = qs.count()

        results = [_serialize(r) for r in qs[offset: offset + page_size]]
        return Response({"total": total, "offset": offset, "results": results})


class PublicRestaurantDetailView(APIView):
    """Single restaurant detail — public, no auth."""

    permission_classes = [AllowAny]
    throttle_classes   = [ScopedRateThrottle]
    throttle_scope     = "public_data"

    @method_decorator(cache_page(60))
    def get(self, request, pk):
        try:
            restaurant = _annotate_current_grade(
                Restaurant.objects.all()
            ).get(pk=pk)
        except Restaurant.DoesNotExist:
            return Response({"detail": "Not found."}, status=404)

        return Response(_serialize(restaurant))
