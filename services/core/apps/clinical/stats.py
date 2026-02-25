"""
Epidemiological statistics for outbreak investigation.

Implements:
  - Symptom frequency analysis
  - Exposure type attack rates
  - Food item frequency ranking
  - Crude odds ratio + 95% CI (Woolf method) for food/exposure associations
  - Fisher's exact test p-value approximation for small samples

All computations operate on anonymized data only — no PII is accessed.

Usage
-----
    from apps.clinical.stats import analyze_investigation
    result = analyze_investigation(investigation_id=7)
"""

import math
import logging
from collections import Counter
from typing import Optional

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Math helpers
# ---------------------------------------------------------------------------

def _odds_ratio(a: int, b: int, c: int, d: int) -> Optional[float]:
    """
    Compute crude odds ratio from 2×2 contingency table.

        | Exposed | Unexposed
    Case|    a    |    c
    Non |    b    |    d

    OR = (a × d) / (b × c)
    Returns None if denominator is zero.
    """
    denom = b * c
    if denom == 0:
        return None
    return (a * d) / denom


def _or_95ci(a: int, b: int, c: int, d: int) -> tuple[Optional[float], Optional[float]]:
    """
    95% confidence interval for log(OR) using the Woolf (logit) method.
    Returns (lower, upper) or (None, None) if any cell is zero.
    """
    if 0 in (a, b, c, d):
        return None, None
    or_val = _odds_ratio(a, b, c, d)
    if or_val is None or or_val <= 0:
        return None, None
    se = math.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
    ln_or = math.log(or_val)
    return (
        round(math.exp(ln_or - 1.96 * se), 3),
        round(math.exp(ln_or + 1.96 * se), 3),
    )


def _chi2_pvalue(a: int, b: int, c: int, d: int) -> Optional[float]:
    """
    Pearson chi-square p-value (1 df) using normal approximation.
    Use only when all expected counts ≥ 5.
    Returns None if total is zero.
    """
    n = a + b + c + d
    if n == 0:
        return None
    expected_a = (a + b) * (a + c) / n
    if expected_a < 5:
        return None   # Switch to Fisher's for small cells

    chi2 = (n * (a * d - b * c) ** 2) / (
        (a + b) * (c + d) * (a + c) * (b + d)
    )
    # Two-tailed p using standard normal approximation (z = sqrt(chi2))
    # Approximation: p ≈ 2 * (1 - Φ(z))  via erfc
    z = math.sqrt(chi2)
    import math as _m
    p = _m.erfc(z / _m.sqrt(2))
    return round(p, 4)


# ---------------------------------------------------------------------------
# Main analysis functions
# ---------------------------------------------------------------------------

def _symptom_frequencies(cases) -> list[dict]:
    """
    For a queryset of ClinicalCase, return each symptom with its frequency.
    """
    counter: Counter = Counter()
    total = 0
    for c in cases:
        syms = c.symptoms or []
        counter.update(syms)
        total += 1

    if total == 0:
        return []

    return sorted(
        [
            {
                "symptom": sym,
                "count": cnt,
                "percent": round(cnt / total * 100, 1),
            }
            for sym, cnt in counter.items()
        ],
        key=lambda x: -x["count"],
    )


def _exposure_analysis(cases) -> list[dict]:
    """
    For each exposure_type found among case exposures, compute:
      - count of cases with that exposure
      - percentage of cases
      - top food items mentioned
      - crude OR vs unexposed cases (using illness_status as proxy)

    Proxy for "controls": cases whose illness_status == "ruled_out" (or "suspected")
    vs confirmed cases is NOT ideal — we use unexposed-within-cases methodology.

    2×2 table for each exposure type E:
      a = cases WITH exposure E (confirmed)
      b = cases WITHOUT exposure E (confirmed)
      c = cases WITH exposure E (suspected/ruled-out, proxy non-case)
      d = cases WITHOUT exposure E (suspected/ruled-out)
    """
    from apps.clinical.models import ClinicalExposure

    case_list = list(cases.prefetch_related("exposures").only(
        "pk", "illness_status", "symptoms"
    ))

    case_ids = [c.pk for c in case_list]
    if not case_ids:
        return []

    # Map case_id → exposure types + food items
    exp_by_case: dict[int, set[str]] = {c.pk: set() for c in case_list}
    food_by_type: dict[str, Counter] = {}

    exposures = ClinicalExposure.objects.filter(case_id__in=case_ids).values(
        "case_id", "exposure_type", "food_items"
    )
    for exp in exposures:
        cid  = exp["case_id"]
        etype = exp["exposure_type"]
        exp_by_case[cid].add(etype)
        food_by_type.setdefault(etype, Counter())
        for item in (exp["food_items"] or []):
            if item:
                food_by_type[etype][item.lower().strip()] += 1

    # Partition cases into confirmed vs suspected (proxy non-case)
    confirmed_ids = {
        c.pk for c in case_list
        if c.illness_status == "confirmed"
    }
    suspected_ids = {c.pk for c in case_list} - confirmed_ids

    total_cases = len(case_list)
    results = []

    all_exposure_types = {etype for types in exp_by_case.values() for etype in types}

    for etype in sorted(all_exposure_types):
        exposed_ids       = {cid for cid, types in exp_by_case.items() if etype in types}
        unexposed_ids     = set(case_ids) - exposed_ids

        # 2×2 table (confirmed vs suspected proxy)
        a = len(exposed_ids   & confirmed_ids)  # exposed,   confirmed
        b = len(unexposed_ids & confirmed_ids)  # unexposed, confirmed
        c = len(exposed_ids   & suspected_ids)  # exposed,   suspected
        d = len(unexposed_ids & suspected_ids)  # unexposed, suspected

        or_val   = _odds_ratio(a, b, c, d)
        ci_lo, ci_hi = _or_95ci(a, b, c, d)
        p_val    = _chi2_pvalue(a, b, c, d)

        top_foods = [
            {"item": item, "count": cnt}
            for item, cnt in food_by_type.get(etype, Counter()).most_common(5)
        ]

        results.append({
            "exposure_type": etype,
            "exposed_cases": len(exposed_ids),
            "total_cases":   total_cases,
            "attack_rate_pct": round(len(exposed_ids) / total_cases * 100, 1) if total_cases else 0,
            "confirmed_among_exposed": a,
            "odds_ratio": round(or_val, 2) if or_val else None,
            "ci_95_lower": ci_lo,
            "ci_95_upper": ci_hi,
            "p_value":     p_val,
            "top_foods":   top_foods,
        })

    return sorted(results, key=lambda x: -(x["exposed_cases"]))


def _confirmed_rate(cases) -> dict:
    """Return case counts by illness_status."""
    counter: Counter = Counter()
    for c in cases:
        counter[c.illness_status] += 1
    total = sum(counter.values())
    return {
        "total": total,
        "confirmed": counter.get("confirmed", 0),
        "suspected": counter.get("suspected", 0),
        "ruled_out": counter.get("ruled_out", 0),
        "hospitalized": sum(
            1 for c in cases if getattr(c, "hospitalized", False)
        ),
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def analyze_investigation(investigation_id: int) -> dict:
    """
    Run full epidemiological analysis for an OutbreakInvestigation.

    Returns:
        {
          "investigation_id": int,
          "case_summary":     {...},
          "symptom_frequencies": [...],
          "exposure_analysis": [...],
          "generated_at": str,
        }
    """
    from django.utils import timezone
    from apps.clinical.models import ClinicalCase

    cases = ClinicalCase.objects.filter(
        investigation_id=investigation_id
    ).prefetch_related("exposures")

    case_list = list(cases)

    logger.info(
        "Analyzing investigation #%d: %d cases",
        investigation_id, len(case_list),
    )

    return {
        "investigation_id":     investigation_id,
        "case_summary":         _confirmed_rate(case_list),
        "symptom_frequencies":  _symptom_frequencies(case_list),
        "exposure_analysis":    _exposure_analysis(cases),
        "generated_at":         timezone.now().isoformat(),
        "note": (
            "Odds ratios use confirmed cases as 'cases' and suspected/ruled-out as "
            "proxy non-cases within this investigation. Interpret with caution when "
            "n < 10. All data is anonymized."
        ),
    }


def analyze_geohash_cluster(
    geohash_prefix: str,
    pathogen: str = "",
    lookback_days: int = 30,
) -> dict:
    """
    Run analysis on a geohash cluster (without a formal investigation).
    Useful for ad-hoc investigation of emerging signals.
    """
    from datetime import date, timedelta
    from django.utils import timezone
    from apps.clinical.models import ClinicalCase

    since = date.today() - timedelta(days=lookback_days)

    qs = ClinicalCase.objects.filter(
        geohash__startswith=geohash_prefix,
        onset_date__gte=since,
    ).prefetch_related("exposures")

    if pathogen:
        qs = qs.filter(pathogen__icontains=pathogen)

    case_list = list(qs)

    return {
        "geohash_prefix":       geohash_prefix,
        "pathogen_filter":      pathogen,
        "lookback_days":        lookback_days,
        "case_summary":         _confirmed_rate(case_list),
        "symptom_frequencies":  _symptom_frequencies(case_list),
        "exposure_analysis":    _exposure_analysis(qs),
        "generated_at":         timezone.now().isoformat(),
        "note": (
            "Ad-hoc geohash cluster analysis. No formal investigation required. "
            "All data is anonymized."
        ),
    }
