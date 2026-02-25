"""Celery tasks for periodic recall feed synchronization."""

import logging
from datetime import datetime, timedelta

from asgiref.sync import async_to_sync
from celery import shared_task
from channels.layers import get_channel_layer
from django.utils import timezone

logger = logging.getLogger(__name__)


def _broadcast_recall(recall) -> None:
    """Push new recall to public WebSocket subscribers (best-effort)."""
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    payload = {
        "type": "recall.new",
        "data": {
            "id":              recall.pk,
            "title":           recall.title,
            "hazard_type":     recall.hazard_type,
            "classification":  recall.classification,
            "status":          recall.status,
            "recalling_firm":  recall.recalling_firm,
            "affected_states": recall.affected_states,
            "source":          recall.source,
            "recall_initiation_date": (
                recall.recall_initiation_date.isoformat()
                if recall.recall_initiation_date else None
            ),
        },
    }
    try:
        async_to_sync(channel_layer.group_send)("recalls_public", payload)
    except Exception:
        logger.warning("WebSocket broadcast to recalls_public failed", exc_info=True)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def sync_fda_recalls(self, days_back: int = 7):
    """
    Fetch recent recall events from the FDA Enforcement API and upsert into
    the Recall + RecallProduct tables.

    Runs nightly via Celery Beat. On first run, set days_back=365 for
    a full backfill.
    """
    from apps.recalls.models import Recall, RecallProduct

    try:
        import httpx

        since = (datetime.now() - timedelta(days=days_back)).strftime("%Y%m%d")
        url = "https://api.fda.gov/food/enforcement.json"
        params = {
            "search": f"recall_initiation_date:[{since}+TO+9999-12-31]",
            "limit": 100,
            "skip": 0,
        }

        created_count = 0
        updated_count = 0

        while True:
            with httpx.Client(timeout=30) as client:
                resp = client.get(url, params=params)
                resp.raise_for_status()
                data = resp.json()

            results = data.get("results", [])
            if not results:
                break

            for item in results:
                recall_number = item.get("recall_number", "")
                if not recall_number:
                    continue

                external_id = f"fda:{recall_number}"

                # Parse affected states from distribution_pattern text or dedicated field
                affected_states = _parse_states(
                    item.get("distribution_pattern", "")
                )

                defaults = {
                    "title": item.get("product_description", "")[:500],
                    "reason": item.get("reason_for_recall", ""),
                    "hazard_type": _extract_hazard(item.get("reason_for_recall", "")),
                    "classification": item.get("classification", "").replace("Class ", "").strip(),
                    "status": _map_status(item.get("status", "")),
                    "recalling_firm": item.get("recalling_firm", "")[:300],
                    "firm_city": item.get("city", "")[:100],
                    "firm_state": item.get("state", "")[:50],
                    "firm_country": item.get("country", "US")[:50],
                    "distribution_pattern": item.get("distribution_pattern", ""),
                    "affected_states": affected_states,
                    "recall_initiation_date": _parse_date(item.get("recall_initiation_date")),
                    "center_classification_date": _parse_date(item.get("center_classification_date")),
                    "termination_date": _parse_date(item.get("termination_date")),
                    "voluntary_mandated": item.get("voluntary_mandated", "")[:50],
                    "initial_firm_notification": item.get("initial_firm_notification", "")[:200],
                    "product_quantity": item.get("product_quantity", "")[:200],
                    "raw_data": item,
                    "last_synced_at": timezone.now(),
                }

                recall, created = Recall.objects.update_or_create(
                    source=Recall.Source.FDA,
                    external_id=external_id,
                    defaults=defaults,
                )

                if created:
                    created_count += 1
                    # Create a product record from the description
                    RecallProduct.objects.get_or_create(
                        recall=recall,
                        product_description=item.get("product_description", "")[:500],
                        defaults={
                            "brand_name": "",
                            "code_info": item.get("code_info", ""),
                        },
                    )
                    _broadcast_recall(recall)
                else:
                    updated_count += 1

            total = data.get("meta", {}).get("results", {}).get("total", 0)
            params["skip"] += len(results)
            if params["skip"] >= total or len(results) < params["limit"]:
                break

        logger.info(
            "FDA recall sync complete: %d created, %d updated",
            created_count,
            updated_count,
        )
        return {"created": created_count, "updated": updated_count}

    except Exception as exc:
        logger.error("FDA recall sync failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=3, default_retry_delay=300)
def sync_usda_recalls(self, days_back: int = 7):
    """
    Fetch recent recall events from the USDA FSIS recall API.
    USDA covers meat, poultry, and egg products (distinct from FDA).
    """
    from apps.recalls.models import Recall, RecallProduct

    try:
        import httpx

        url = "https://www.fsis.usda.gov/fsis/api/recall/v/1"
        params = {"lang": "en", "extended": "true"}

        with httpx.Client(timeout=30) as client:
            resp = client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        created_count = 0
        updated_count = 0
        cutoff = datetime.now() - timedelta(days=days_back)

        for item in data:
            recall_id = str(item.get("field_recalls_release_number") or item.get("nid", ""))
            if not recall_id:
                continue

            initiation_date = _parse_date(
                item.get("field_recalls_recall_date") or item.get("field_recalls_last_modified")
            )
            if initiation_date and initiation_date < cutoff.date():
                continue

            external_id = f"usda:{recall_id}"
            defaults = {
                "title": (item.get("title") or item.get("field_recalls_title", ""))[:500],
                "reason": item.get("field_recalls_reason", ""),
                "hazard_type": _extract_hazard(item.get("field_recalls_reason", "")),
                "classification": item.get("field_recalls_class", "")[:5],
                "status": _map_status(item.get("field_recalls_active_status", "")),
                "recalling_firm": item.get("field_recalls_company", "")[:300],
                "firm_state": item.get("field_recalls_state", "")[:50],
                "distribution_pattern": item.get("field_recalls_states", ""),
                "affected_states": _parse_states(item.get("field_recalls_states", "")),
                "recall_initiation_date": initiation_date,
                "voluntary_mandated": "Voluntary",
                "raw_data": item,
                "last_synced_at": timezone.now(),
            }

            recall, created = Recall.objects.update_or_create(
                source=Recall.Source.USDA_FSIS,
                external_id=external_id,
                defaults=defaults,
            )

            if created:
                created_count += 1
                product_desc = item.get("field_recalls_products_in", "")
                if product_desc:
                    RecallProduct.objects.get_or_create(
                        recall=recall,
                        product_description=product_desc[:500],
                        defaults={
                            "code_info": item.get("field_recalls_code_info", ""),
                        },
                    )
                _broadcast_recall(recall)
            else:
                updated_count += 1

        logger.info(
            "USDA recall sync complete: %d created, %d updated",
            created_count,
            updated_count,
        )
        return {"created": created_count, "updated": updated_count}

    except Exception as exc:
        logger.error("USDA recall sync failed: %s", exc)
        raise self.retry(exc=exc)


@shared_task(bind=True, max_retries=2, default_retry_delay=300)
def auto_create_acknowledgments_for_active(self):
    """
    For every active recall without complete acknowledgment coverage,
    run the matching engine and create PENDING acks for new restaurants.

    Runs every 6 hours via Celery Beat so newly added restaurants are
    covered after each sync cycle.
    """
    from apps.recalls.models import Recall
    from apps.recalls.matching import auto_create_acknowledgments

    active_recalls = Recall.objects.filter(
        status__in=[Recall.Status.ACTIVE, Recall.Status.ONGOING],
        affected_states__isnull=False,
    ).exclude(affected_states=[])

    total_created = 0
    try:
        for recall in active_recalls:
            result = auto_create_acknowledgments(recall)
            total_created += result["created"]
        logger.info("Acknowledgment sweep complete: %d new acks created", total_created)
        return {"new_acks": total_created}
    except Exception as exc:
        logger.error("Acknowledgment sweep failed: %s", exc)
        raise self.retry(exc=exc)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_HAZARD_KEYWORDS = {
    "Salmonella": "Salmonella",
    "Listeria": "Listeria",
    "E. coli": "E. coli",
    "E.coli": "E. coli",
    "Hepatitis A": "Hepatitis A",
    "Norovirus": "Norovirus",
    "Botulism": "Botulism",
    "allergen": "Undeclared allergen",
    "undeclared": "Undeclared allergen",
    "foreign": "Foreign material",
    "metal": "Foreign material",
    "glass": "Foreign material",
    "mislabel": "Mislabeling",
    "contamination": "Contamination",
}

_US_STATES = {
    "AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN",
    "IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV",
    "NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN",
    "TX","UT","VT","VA","WA","WV","WI","WY","DC","PR","GU","VI",
}


def _extract_hazard(text: str) -> str:
    if not text:
        return ""
    for keyword, label in _HAZARD_KEYWORDS.items():
        if keyword.lower() in text.lower():
            return label
    return ""


def _parse_states(text: str) -> list:
    import re
    tokens = re.findall(r"\b([A-Z]{2})\b", text.upper())
    return sorted({t for t in tokens if t in _US_STATES})


def _map_status(raw: str) -> str:
    raw_lower = raw.lower()
    if "terminated" in raw_lower or "completed" in raw_lower or "closed" in raw_lower:
        return "completed"
    if "ongoing" in raw_lower or "open" in raw_lower:
        return "ongoing"
    return "active"


def _parse_date(value):
    if not value:
        return None
    from datetime import datetime
    for fmt in ("%Y%m%d", "%Y-%m-%d", "%m/%d/%Y", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(str(value)[:10], fmt).date()
        except (ValueError, TypeError):
            continue
    return None
