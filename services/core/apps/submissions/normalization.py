"""
Field-name and score normalization for jurisdiction submission records.

apply_schema_map  — rename incoming field names to canonical names
normalize_score   — convert jurisdiction-specific score/grade to (int|None, str|None)
normalize_record  — full pipeline: schema map → score → stamp source_jurisdiction
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from apps.submissions.models import JurisdictionAccount

logger = logging.getLogger(__name__)

# Score bands for SCORE_0_100 → grade derivation
_SCORE_GRADE_BANDS = [
    (90, "A"),
    (80, "B"),
    (70, "C"),
]

# Grade letter → canonical score midpoint
_GRADE_SCORE_MAP: dict[str, int] = {
    "A": 95,
    "B": 82,
    "C": 72,
    "D": 62,
    "F": 30,
}


def apply_schema_map(record: dict, schema_map: dict) -> dict:
    """
    Rename fields in *record* according to *schema_map*.

    schema_map example::

        {"facility_name": "restaurant_name", "inspection_date": "inspected_at"}

    Keys not present in schema_map pass through unchanged.
    """
    if not schema_map:
        return dict(record)
    result = {}
    for key, value in record.items():
        result[schema_map.get(key, key)] = value
    return result


def normalize_score(raw, score_system: str) -> tuple[int | None, str | None]:
    """
    Convert a raw score/grade value to (score_0_100, grade_letter).

    Returns (None, None) on unrecognisable input — the caller can decide
    whether that is an error or should be skipped.
    """
    if raw is None:
        return None, None

    raw_str = str(raw).strip()

    if score_system == "SCORE_0_100":
        try:
            score = int(float(raw_str))
            if not (0 <= score <= 100):
                return None, None
        except (ValueError, TypeError):
            return None, None
        grade = "X"
        for threshold, letter in _SCORE_GRADE_BANDS:
            if score >= threshold:
                grade = letter
                break
        return score, grade

    elif score_system == "GRADE_A_F":
        letter = raw_str.upper()
        if letter not in _GRADE_SCORE_MAP:
            return None, None
        return _GRADE_SCORE_MAP[letter], letter

    elif score_system == "PASS_FAIL":
        lower = raw_str.lower()
        if lower in ("pass", "passed", "yes", "1", "true"):
            return 100, "A"
        if lower in ("fail", "failed", "no", "0", "false"):
            return 40, "X"
        return None, None

    elif score_system == "LETTER_NUMERIC":
        # Try numeric first
        try:
            score = int(float(raw_str))
            if 0 <= score <= 100:
                grade = "X"
                for threshold, letter in _SCORE_GRADE_BANDS:
                    if score >= threshold:
                        grade = letter
                        break
                return score, grade
        except (ValueError, TypeError):
            pass
        # Fall back to letter grade
        letter = raw_str.upper()
        if letter in _GRADE_SCORE_MAP:
            return _GRADE_SCORE_MAP[letter], letter
        return None, None

    return None, None


def normalize_record(record: dict, jurisdiction: "JurisdictionAccount") -> dict:
    """
    Full normalization pipeline for one submitted row:

    1. Apply jurisdiction's schema_map (rename fields)
    2. Normalize score/grade to canonical values
    3. Stamp ``source_jurisdiction`` with the jurisdiction's FIPS code
    4. Map ``inspected_at`` → ``inspection_date`` (ingest_inspection_record expects
       the latter key)

    Returns a dict compatible with ``apps.inspections.utils.ingest_inspection_record()``.
    """
    out = apply_schema_map(record, jurisdiction.schema_map or {})

    # inspected_at is the user-facing name; ingest_inspection_record uses inspection_date
    if "inspected_at" in out and "inspection_date" not in out:
        out["inspection_date"] = out.pop("inspected_at")

    # Score / grade normalization
    raw_score = out.get("score") or out.get("grade")
    if raw_score is not None:
        score, grade = normalize_score(raw_score, jurisdiction.score_system)
        if score is not None:
            out["score"] = score
        if grade is not None:
            out["grade"] = grade

    # Stamp jurisdiction
    out["source_jurisdiction"] = jurisdiction.fips_code
    # Also expose state for restaurant fingerprinting
    if "state" not in out:
        out["state"] = jurisdiction.state

    return out
