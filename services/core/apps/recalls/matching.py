"""
Recall-to-restaurant matching logic.

Determines which restaurants need to acknowledge a given recall, based on:
  1. Geographic overlap — recall.affected_states vs restaurant.state
  2. (Optional) Category overlap — coming in v2 when product categories are indexed

The matching intentionally casts a wide net for Class I recalls: any restaurant
in an affected state is considered potentially impacted and receives a PENDING
acknowledgment.  Restaurants can self-resolve via NOT_AFFECTED.

This module is intentionally side-effect-free: matching only reads data.
`auto_create_acknowledgments()` is the only function that writes to the DB.
"""

import logging
from typing import Optional

from django.db import transaction

logger = logging.getLogger(__name__)


def _affected_states_set(recall) -> set[str]:
    """Return a normalised set of two-letter state codes from recall.affected_states."""
    raw = recall.affected_states
    if not raw:
        return set()
    if isinstance(raw, str):
        import json
        try:
            raw = json.loads(raw)
        except (ValueError, TypeError):
            raw = [raw]
    return {s.strip().upper() for s in raw if s}


def match_restaurants_for_recall(recall):
    """
    Return a QuerySet of Restaurant records that match the given recall.

    Matching rules (in priority order):
      - If recall.affected_states is empty, return no restaurants (national
        distribution handled at UI level).
      - Match restaurants whose state (upper-cased) is in affected_states.
      - For Class I recalls, include all active restaurants in affected states.
      - For Class II/III, include only ACTIVE restaurants (suspended/closed
        establishments still carry inventory risk, so we include SUSPENDED too).
    """
    from apps.restaurants.models import Restaurant

    affected = _affected_states_set(recall)
    if not affected:
        logger.debug("Recall %d has no affected_states — skipping matching", recall.pk)
        return Restaurant.objects.none()

    qs = Restaurant.objects.filter(
        state__in=affected,
        status__in=["ACTIVE", "SUSPENDED"],
    )
    return qs


@transaction.atomic
def auto_create_acknowledgments(recall, dry_run: bool = False) -> dict:
    """
    Create RecallAcknowledgment(status=PENDING) rows for every restaurant that
    matches the given recall.

    Skips restaurants that already have an acknowledgment for this recall
    (unique_together constraint on (recall, restaurant)).

    Args:
        recall:   A Recall model instance.
        dry_run:  If True, compute match count but do not write anything.

    Returns:
        {"matched": int, "created": int, "skipped": int}
    """
    from apps.recalls.models import RecallAcknowledgment

    restaurants = match_restaurants_for_recall(recall)
    matched  = 0
    created  = 0
    skipped  = 0

    # Fetch existing acks for this recall in one query
    existing_ids = set(
        RecallAcknowledgment.objects
        .filter(recall=recall)
        .values_list("restaurant_id", flat=True)
    )

    batch: list[RecallAcknowledgment] = []
    for restaurant in restaurants.iterator(chunk_size=200):
        matched += 1
        if restaurant.pk in existing_ids:
            skipped += 1
            continue
        if not dry_run:
            batch.append(
                RecallAcknowledgment(
                    recall=recall,
                    restaurant=restaurant,
                    status=RecallAcknowledgment.AckStatus.PENDING,
                )
            )

    if batch:
        RecallAcknowledgment.objects.bulk_create(batch, ignore_conflicts=True)
        created = len(batch)

    logger.info(
        "Recall #%d auto-acks: matched=%d created=%d skipped=%d dry_run=%s",
        recall.pk, matched, created, skipped, dry_run,
    )
    return {"matched": matched, "created": created, "skipped": skipped}
