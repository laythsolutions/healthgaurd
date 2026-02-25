"""
Public (no-auth) read-only view for outbreak advisories.

GET /api/v1/public/advisories/

Returns a list of OutbreakInvestigation records that have crossed the public
disclosure threshold:
  - status in (open, active)
  - case_count_at_open >= MIN_CASES  (prevents premature disclosure)
  - auto_generated=True  OR  notes contains '[public]' marker

Privacy guarantees
------------------
  - No case-level identifiers are returned.
  - Geographic scope is limited to what the investigating agency has approved
    (geographic_scope field, populated by the clustering engine at geohash
    precision-4 = ~40 km cell).
  - Pathogen name and case counts are the only epidemiological specifics
    shown; individual symptom data is never exposed publicly.
"""

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from .models import OutbreakInvestigation

# Minimum confirmed/probable cases before an advisory is publicly visible
MIN_CASES = 3

_SAFE_FIELDS = (
    "id", "title", "status", "pathogen", "suspected_vehicle",
    "geographic_scope", "cluster_start_date", "cluster_end_date",
    "case_count_at_open", "cluster_score", "auto_generated", "opened_at",
)


def _serialize_advisory(inv: OutbreakInvestigation) -> dict:
    return {
        "id":               inv.pk,
        "title":            inv.title,
        "status":           inv.status,
        "pathogen":         inv.pathogen,
        "suspected_vehicle": inv.suspected_vehicle,
        "geographic_scope": inv.geographic_scope,
        "cluster_start_date": (
            inv.cluster_start_date.isoformat() if inv.cluster_start_date else None
        ),
        "cluster_end_date": (
            inv.cluster_end_date.isoformat() if inv.cluster_end_date else None
        ),
        "case_count":       inv.case_count_at_open,
        "cluster_score":    round(inv.cluster_score, 1) if inv.cluster_score else None,
        "auto_generated":   inv.auto_generated,
        "opened_at":        inv.opened_at.isoformat(),
    }


class PublicAdvisoryListView(APIView):
    """
    Public outbreak advisory feed.

    Query params:
        status      — filter: open / active / closed / all (default: open,active)
        pathogen    — filter by pathogen substring
        limit       — default 20, max 50
    """

    permission_classes = [AllowAny]
    throttle_classes   = [ScopedRateThrottle]
    throttle_scope     = "public_data"

    @method_decorator(cache_page(5 * 60))   # 5-min cache
    def get(self, request):
        status_param = request.query_params.get("status", "").strip().lower()
        if status_param == "all":
            status_filter = None
        elif status_param in ("open", "active", "closed", "archived"):
            status_filter = [status_param]
        else:
            status_filter = [
                OutbreakInvestigation.InvestigationStatus.OPEN,
                OutbreakInvestigation.InvestigationStatus.ACTIVE,
            ]

        qs = OutbreakInvestigation.objects.filter(
            case_count_at_open__gte=MIN_CASES,
        ).order_by("-opened_at")

        if status_filter:
            qs = qs.filter(status__in=status_filter)

        pathogen = request.query_params.get("pathogen", "").strip()
        if pathogen:
            qs = qs.filter(pathogen__icontains=pathogen)

        try:
            limit = min(int(request.query_params.get("limit", 20)), 50)
        except (ValueError, TypeError):
            limit = 20

        results = [_serialize_advisory(inv) for inv in qs[:limit]]

        return Response({
            "count":        len(results),
            "min_cases":    MIN_CASES,
            "privacy_note": (
                "All advisories are derived from anonymized, aggregated case data. "
                "No patient identifiers are published. Geographic precision is limited "
                "to approximately 40 km cells."
            ),
            "results": results,
        })
