"""
Spatial-temporal clustering engine for foodborne illness outbreak detection.

Algorithm
---------
1. Scan ClinicalCase rows with onset_date in the last `lookback_days` (default 30).
2. Group by (pathogen, geohash_prefix_4).  Geohash precision-4 cells are roughly
   40 km × 20 km — large enough to catch a shared-source cluster while small
   enough to avoid false positives from background noise.
3. Any group with ≥ CASE_THRESHOLD cases computes a cluster_score and either
   creates a new OutbreakInvestigation or refreshes an existing open one.

cluster_score formula
---------------------
    base       = log2(n + 1) × 10
    temporal   = 10 / (temporal_std_days + 1)   (tighter window → higher)
    severity   = pathogen severity multiplier (1.0–2.5)
    hosp_bonus = hospitalization_rate × 5
    score      = base + temporal + severity_bonus + hosp_bonus

A score > 20 is considered significant; > 35 triggers high-priority status.
"""

import logging
import math
from datetime import date, timedelta
from statistics import stdev
from typing import Optional

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db import transaction
from django.utils import timezone

from .models import ClinicalCase, OutbreakInvestigation

logger = logging.getLogger(__name__)

# -----------------------------------------------------------------------
# Tuneable parameters
# -----------------------------------------------------------------------
CASE_THRESHOLD = 3          # Minimum cases in a cell to form a cluster
LOOKBACK_DAYS  = 30         # How far back to scan
GEOHASH_PREFIX = 4          # Precision level for spatial grouping (~40 km cell)
HIGH_PRIORITY_SCORE = 35.0  # Score above which investigation is auto-escalated

# Pathogen severity multipliers (higher = more urgent)
_SEVERITY = {
    "e. coli o157:h7": 2.5,
    "e.coli o157":     2.5,
    "listeria":        2.5,
    "salmonella":      2.0,
    "shigella":        2.0,
    "vibrio":          2.0,
    "hepatitis a":     2.0,
    "campylobacter":   1.5,
    "norovirus":       1.5,
    "cryptosporidium": 1.5,
    "clostridium":     1.5,
    "staphylococcus":  1.2,
    "bacillus":        1.2,
}


def _broadcast_advisory(inv: "OutbreakInvestigation") -> None:
    """Push the advisory to public WebSocket subscribers (best-effort, non-blocking)."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    payload = {
        "type": "advisory.new",
        "data": {
            "id":                 inv.pk,
            "title":              inv.title,
            "status":             inv.status,
            "pathogen":           inv.pathogen,
            "geographic_scope":   inv.geographic_scope,
            "case_count":         inv.case_count_at_open,
            "cluster_score":      round(inv.cluster_score, 1) if inv.cluster_score else None,
            "cluster_start_date": inv.cluster_start_date.isoformat() if inv.cluster_start_date else None,
            "auto_generated":     inv.auto_generated,
        },
    }
    try:
        async_to_sync(channel_layer.group_send)("advisories_public", payload)
    except Exception:
        logger.warning("WebSocket broadcast to advisories_public failed", exc_info=True)


def _severity_multiplier(pathogen: str) -> float:
    if not pathogen:
        return 1.0
    p = pathogen.lower().strip()
    for key, mult in _SEVERITY.items():
        if key in p:
            return mult
    return 1.0


def _temporal_concentration(onset_dates: list[date]) -> float:
    """
    Return a concentration score in [0, 10] — higher when cases are tightly
    clustered in time.  Uses standard deviation of ordinal date values.
    Single-date clusters (std=0) score the maximum.
    """
    if len(onset_dates) < 2:
        return 10.0
    ordinals = [d.toordinal() for d in onset_dates if d]
    if not ordinals or len(ordinals) < 2:
        return 10.0
    try:
        std_days = stdev(ordinals)
    except Exception:
        return 5.0
    return 10.0 / (std_days + 1.0)


def _cluster_score(cases: list[ClinicalCase]) -> float:
    n = len(cases)
    base = math.log2(n + 1) * 10.0

    onset_dates = [c.onset_date for c in cases if c.onset_date]
    temporal = _temporal_concentration(onset_dates)

    pathogen = (cases[0].pathogen or "").strip() if cases else ""
    severity_bonus = (_severity_multiplier(pathogen) - 1.0) * 10.0

    hospitalized = [c for c in cases if c.hospitalized]
    hosp_bonus = (len(hospitalized) / n) * 5.0 if n else 0.0

    score = base + temporal + severity_bonus + hosp_bonus
    return round(score, 2)


def _geographic_label(geohash_prefix: str, state_hint: str = "") -> str:
    """Produce a human-readable geographic scope label."""
    label = f"Geohash cell {geohash_prefix.upper()}"
    if state_hint:
        label += f" ({state_hint.upper()})"
    return label


def _earliest_onset(cases: list[ClinicalCase]) -> Optional[date]:
    dates = [c.onset_date for c in cases if c.onset_date]
    return min(dates) if dates else None


def _latest_onset(cases: list[ClinicalCase]) -> Optional[date]:
    dates = [c.onset_date for c in cases if c.onset_date]
    return max(dates) if dates else None


# -----------------------------------------------------------------------
# Public entry point
# -----------------------------------------------------------------------

@transaction.atomic
def detect_clusters(lookback_days: int = LOOKBACK_DAYS) -> dict:
    """
    Scan recent ClinicalCase rows for spatial-temporal clusters.

    Returns a summary dict:
        {
          "scanned":   int,   # total cases examined
          "clusters":  int,   # distinct clusters found
          "created":   int,   # new OutbreakInvestigation rows created
          "updated":   int,   # existing investigations refreshed
        }
    """
    since = date.today() - timedelta(days=lookback_days)

    cases_qs = (
        ClinicalCase.objects
        .filter(onset_date__gte=since)
        .exclude(geohash="")
        .values_list(
            "pk", "pathogen", "geohash", "onset_date",
            "hospitalized", "illness_status",
        )
    )

    # Group into (pathogen_normalised, geohash_prefix_4) buckets
    buckets: dict[tuple[str, str], list[int]] = {}
    pk_to_attrs: dict[int, dict] = {}

    for pk, pathogen, geohash, onset_date, hospitalized, illness_status in cases_qs:
        key = (
            (pathogen or "unknown").strip().lower(),
            geohash[:GEOHASH_PREFIX],
        )
        buckets.setdefault(key, []).append(pk)
        pk_to_attrs[pk] = {
            "onset_date":  onset_date,
            "hospitalized": hospitalized,
        }

    scanned  = len(pk_to_attrs)
    clusters = 0
    created  = 0
    updated  = 0

    for (pathogen_key, geohash_prefix), pks in buckets.items():
        if len(pks) < CASE_THRESHOLD:
            continue

        clusters += 1

        # Reconstruct lightweight case objects for scoring
        class _Case:
            def __init__(self, pk):
                attrs = pk_to_attrs[pk]
                self.onset_date  = attrs["onset_date"]
                self.hospitalized = attrs["hospitalized"]
                self.pathogen    = pathogen_key

        pseudo_cases = [_Case(pk) for pk in pks]
        score = _cluster_score(pseudo_cases)

        # Derive display-friendly pathogen name (title-case the key)
        display_pathogen = pathogen_key.title() if pathogen_key != "unknown" else ""
        geo_scope        = _geographic_label(geohash_prefix)
        earliest         = _earliest_onset(pseudo_cases)
        latest           = _latest_onset(pseudo_cases)

        # Try to find an existing open investigation covering this cluster
        existing = (
            OutbreakInvestigation.objects
            .filter(
                pathogen__iexact=display_pathogen,
                auto_generated=True,
                status__in=[
                    OutbreakInvestigation.InvestigationStatus.OPEN,
                    OutbreakInvestigation.InvestigationStatus.ACTIVE,
                ],
                geographic_scope__contains=geohash_prefix.upper(),
            )
            .first()
        )

        if existing:
            existing.case_count_at_open = len(pks)
            existing.cluster_score      = score
            existing.cluster_end_date   = latest
            if (
                score >= HIGH_PRIORITY_SCORE
                and existing.status == OutbreakInvestigation.InvestigationStatus.OPEN
            ):
                existing.status = OutbreakInvestigation.InvestigationStatus.ACTIVE
            existing.save(
                update_fields=[
                    "case_count_at_open", "cluster_score",
                    "cluster_end_date", "status",
                ]
            )
            # Link any new cases to this investigation
            (
                ClinicalCase.objects
                .filter(pk__in=pks, investigation__isnull=True)
                .update(investigation=existing)
            )
            # Broadcast refresh to public advisory WebSocket subscribers
            _broadcast_advisory(existing)
            updated += 1
        else:
            inv_status = (
                OutbreakInvestigation.InvestigationStatus.ACTIVE
                if score >= HIGH_PRIORITY_SCORE
                else OutbreakInvestigation.InvestigationStatus.OPEN
            )
            title = (
                f"Auto-detected cluster: {display_pathogen or 'Unknown pathogen'} "
                f"— {geo_scope}"
            )
            investigation = OutbreakInvestigation.objects.create(
                title            = title[:300],
                status           = inv_status,
                pathogen         = display_pathogen,
                geographic_scope = geo_scope,
                cluster_start_date = earliest,
                cluster_end_date   = latest,
                case_count_at_open = len(pks),
                auto_generated   = True,
                cluster_score    = score,
            )
            # Link cases
            (
                ClinicalCase.objects
                .filter(pk__in=pks)
                .update(investigation=investigation)
            )
            created += 1
            logger.info(
                "Cluster detected: %s | geohash=%s | cases=%d | score=%.1f",
                display_pathogen, geohash_prefix, len(pks), score,
            )
            # Broadcast new investigation to public advisory WebSocket subscribers
            _broadcast_advisory(investigation)

    logger.info(
        "Cluster detection complete: scanned=%d clusters=%d created=%d updated=%d",
        scanned, clusters, created, updated,
    )
    return {
        "scanned":  scanned,
        "clusters": clusters,
        "created":  created,
        "updated":  updated,
    }
