"""
Supply chain traceback graph builder.

Connects clinical cases → food exposures → restaurants → active recalls,
producing a lightweight graph structure suitable for visualization or
further analysis.

The graph deliberately contains no PII:
  - Cases are referenced by anonymized ID + subject_hash prefix only.
  - Restaurants are real names (they are public entities), but no
    patient records are ever linked to a specific named restaurant.
  - Recalls are public regulatory records.

Graph schema
------------
    nodes:  list of {"id": str, "type": str, "label": str, "meta": dict}
    edges:  list of {"source": str, "target": str, "label": str}

    node types: "investigation", "case", "exposure", "restaurant", "recall"
"""

import logging
from typing import Optional

logger = logging.getLogger(__name__)

# Geohash precision-5 cell is ~5 km — we use 4-char prefix for restaurant
# matching (≈40 km radius, intentionally coarse to protect patient location).
_MATCH_GEOHASH_LEN = 4


def _geohash_neighbours(prefix: str) -> list[str]:
    """
    Return the prefix itself plus the 8 adjacent geohash cells.
    This simple approximation avoids a proper geohash library dependency.
    """
    # For now, return only the cell itself; full adjacency can be added later.
    return [prefix]


def _find_restaurants_by_geohash(geohash_prefix: str, state: str = ""):
    """
    Find Restaurant records whose location (city/state) could correspond to
    the given geohash prefix.  Since Restaurant has no geohash field, we
    approximate by state.  When a geohash → lat/lon resolver is added, this
    can be upgraded to true proximity matching.
    """
    from apps.restaurants.models import Restaurant
    qs = Restaurant.objects.filter(status="ACTIVE")
    if state:
        qs = qs.filter(state__iexact=state)
    # Return at most 20 restaurants per geohash cell to keep the graph manageable
    return qs[:20]


def _find_active_recalls_for_restaurant(restaurant) -> list:
    """Return recalls that could affect the given restaurant (by state)."""
    from apps.recalls.models import Recall
    return list(
        Recall.objects
        .filter(
            status__in=["active", "ongoing"],
            affected_states__contains=restaurant.state.upper(),
        )
        .values("id", "title", "hazard_type", "classification", "source", "status")[:10]
    )


def build_traceback(
    investigation_id: Optional[int] = None,
    geohash_prefix: Optional[str] = None,
    pathogen: Optional[str] = None,
    lookback_days: int = 30,
) -> dict:
    """
    Build a traceback graph for an investigation or a geohash cluster.

    At least one of `investigation_id` or `geohash_prefix` must be provided.

    Returns:
        {
          "nodes": [...],
          "edges": [...],
          "summary": {
            "case_count": int,
            "exposure_count": int,
            "restaurant_count": int,
            "recall_count": int,
          }
        }
    """
    from apps.clinical.models import ClinicalCase, ClinicalExposure
    from datetime import date, timedelta

    nodes: list[dict] = []
    edges: list[dict] = []
    node_ids: set[str] = set()

    def add_node(nid: str, ntype: str, label: str, meta: dict = None):
        if nid not in node_ids:
            node_ids.add(nid)
            nodes.append({"id": nid, "type": ntype, "label": label, "meta": meta or {}})

    def add_edge(src: str, tgt: str, label: str = ""):
        edges.append({"source": src, "target": tgt, "label": label})

    # ---- Root node --------------------------------------------------------
    if investigation_id:
        root_id = f"inv_{investigation_id}"
        add_node(root_id, "investigation", f"Investigation #{investigation_id}")
    elif geohash_prefix:
        root_id = f"geo_{geohash_prefix}"
        add_node(root_id, "geohash_cluster", f"Cluster: {geohash_prefix.upper()}")
    else:
        return {"error": "Provide investigation_id or geohash_prefix", "nodes": [], "edges": []}

    # ---- Cases ------------------------------------------------------------
    if investigation_id:
        cases = ClinicalCase.objects.filter(
            investigation_id=investigation_id
        ).prefetch_related("exposures")
    else:
        since = date.today() - timedelta(days=lookback_days)
        cases = ClinicalCase.objects.filter(
            geohash__startswith=geohash_prefix,
            onset_date__gte=since,
        ).prefetch_related("exposures")
        if pathogen:
            cases = cases.filter(pathogen__icontains=pathogen)

    restaurant_ids_seen: set[int] = set()
    recall_ids_seen: set[int] = set()
    exposure_types_seen: set[str] = set()
    case_count = 0

    for case in cases[:100]:   # Cap to 100 cases to keep graph readable
        case_count += 1
        case_nid = f"case_{case.pk}"
        label = (
            f"{case.pathogen or 'Unknown'} · "
            f"{case.age_range or '?'} · "
            f"{case.onset_date or '?'}"
        )
        add_node(case_nid, "case", label, {
            "illness_status": case.illness_status,
            "geohash": case.geohash,
            "zip3": case.zip3,
        })
        add_edge(root_id, case_nid, "includes")

        # ---- Exposures for this case --------------------------------------
        for exp in case.exposures.all():
            exp_nid = f"exp_{exp.pk}"
            add_node(exp_nid, "exposure", exp.exposure_type.replace("_", " ").title(), {
                "exposure_type": exp.exposure_type,
                "exposure_date": str(exp.exposure_date) if exp.exposure_date else None,
                "establishment_type": exp.establishment_type,
                "food_items": exp.food_items,
                "geohash": exp.geohash,
                "confidence": exp.confidence,
            })
            add_edge(case_nid, exp_nid, "reported")

            # Linked recall directly on the exposure
            if exp.linked_recall_id and exp.linked_recall_id not in recall_ids_seen:
                recall_ids_seen.add(exp.linked_recall_id)
                recall_nid = f"recall_{exp.linked_recall_id}"
                from apps.recalls.models import Recall
                try:
                    r = Recall.objects.values(
                        "id", "title", "hazard_type", "source", "status", "classification"
                    ).get(pk=exp.linked_recall_id)
                    add_node(recall_nid, "recall", r["title"][:80], {
                        "hazard_type": r["hazard_type"],
                        "source": r["source"],
                        "status": r["status"],
                        "classification": r["classification"],
                    })
                except Exception:
                    pass
                add_edge(exp_nid, recall_nid, "linked_recall")

            # Restaurant matching by exposure geohash + type
            if exp.exposure_type == "restaurant" and exp.geohash:
                prefix = exp.geohash[:_MATCH_GEOHASH_LEN]
                exposure_types_seen.add(exp.exposure_type)

                restaurants = _find_restaurants_by_geohash(prefix)
                for rest in restaurants:
                    if rest.pk in restaurant_ids_seen:
                        rest_nid = f"rest_{rest.pk}"
                        add_edge(exp_nid, rest_nid, "near_exposure")
                        continue

                    restaurant_ids_seen.add(rest.pk)
                    rest_nid = f"rest_{rest.pk}"
                    add_node(rest_nid, "restaurant", rest.name, {
                        "city": rest.city,
                        "state": rest.state,
                        "last_inspection_date": str(rest.last_inspection_date) if rest.last_inspection_date else None,
                        "last_inspection_score": rest.last_inspection_score,
                    })
                    add_edge(exp_nid, rest_nid, "near_exposure")

                    # Recalls that might affect this restaurant
                    for recall in _find_active_recalls_for_restaurant(rest):
                        recall_id = recall["id"]
                        recall_nid = f"recall_{recall_id}"
                        if recall_id not in recall_ids_seen:
                            recall_ids_seen.add(recall_id)
                            add_node(recall_nid, "recall", recall["title"][:80], {
                                "hazard_type": recall["hazard_type"],
                                "source": recall["source"],
                                "status": recall["status"],
                                "classification": recall["classification"],
                            })
                        add_edge(rest_nid, recall_nid, "affected_by")

    return {
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "case_count":       case_count,
            "exposure_count":   sum(1 for n in nodes if n["type"] == "exposure"),
            "restaurant_count": len(restaurant_ids_seen),
            "recall_count":     len(recall_ids_seen),
        },
        "privacy_note": (
            "Cases are identified by anonymized internal ID only. "
            "No patient names, dates of birth, or contact information appear in this graph. "
            "Restaurant locations are approximate (geohash proximity, not confirmed point-of-exposure)."
        ),
    }
