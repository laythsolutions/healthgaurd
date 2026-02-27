# RFC-002: Retail & Transaction Data Pipeline

**Status:** Accepted — Implemented
**Author(s):** Core maintainers
**Created:** 2026-02-25
**Updated:** 2026-02-25

---

## Summary

Add a product-and-transaction data store plus retail partner ingestion connectors to enable UPC-level traceback: when clinical cases share a purchased product, compute exposure odds ratios against controls and map the implicated lot numbers to distribution locations for targeted recall workflows.

## Motivation

The existing supply chain traceback (`clinical/traceback.py`) links cases to restaurants and recalls. It cannot link cases to specific purchased products because the platform has no product or transaction data. Retail-level traceback is the missing piece for multi-source outbreaks where exposure happened at home (packaged goods) rather than a restaurant.

## Detailed Design

### New Django App: `products`

**Models:**

```python
class Product(models.Model):
    upc = models.CharField(max_length=14, unique=True)
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=128)
    category = models.CharField(max_length=64)
    manufacturer = models.CharField(max_length=128, blank=True)

class ProductLot(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    lot_code = models.CharField(max_length=64)
    production_date = models.DateField(null=True)
    use_by_date = models.DateField(null=True)
    distribution_states = ArrayField(models.CharField(max_length=2))

class RetailTransaction(models.Model):
    """De-identified purchase record."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    consumer_hash = models.CharField(max_length=64)  # HMAC of loyalty ID — not reversible
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    lot = models.ForeignKey(ProductLot, null=True, on_delete=models.SET_NULL)
    retailer = models.CharField(max_length=64)
    store_geohash = models.CharField(max_length=8)  # precision-4, ~40km
    purchase_date = models.DateField()
    quantity = models.PositiveSmallIntegerField(default=1)
    # No name, no exact address, no full loyalty ID

class RetailPartnerConfig(models.Model):
    name = models.CharField(max_length=64, unique=True)
    connector_type = models.CharField(max_length=32)  # 'api' | 'sftp' | 'webhook'
    endpoint_url = models.URLField(blank=True)
    auth_type = models.CharField(max_length=16)  # 'apikey' | 'oauth2' | 'basic'
    enabled = models.BooleanField(default=False)
    last_sync = models.DateTimeField(null=True)
```

### Ingestion

New intelligence harvester: `services/intelligence/harvesters/retail_connector.py`

- Base class `RetailConnector` with `fetch_transactions(since: datetime) -> list[dict]`
- Concrete implementations: `APIConnector`, `SFTPConnector`
- All connectors apply anonymization before writing to the DB:
  - Loyalty ID → HMAC-SHA256 with `ANONYMIZATION_SALT` → `consumer_hash`
  - Exact address → geohash precision-4
  - Lot code linked if present in GTIN-128 barcode data; otherwise NULL

Celery task `sync_retail_transactions` runs every 6 hours per enabled `RetailPartnerConfig`.

### Retail Traceback Extension

Extend `clinical/traceback.py` with `trace_product_exposure()`:

```python
def trace_product_exposure(investigation_id: int) -> dict:
    """
    For cases in an investigation:
    1. Find shared purchased products via consumer_hash × purchase_date proximity
    2. Compute odds ratio vs. control transactions (same retailer, same period, no case)
    3. Return implicated products ranked by OR, with lot codes and distribution states
    """
```

New endpoint: `GET /api/v1/clinical/investigations/{id}/product-traceback/`

### API Changes

New endpoints (all require `IsHealthDepartmentStaff` or `IsInvestigator` permission):

- `GET /api/v1/products/` — product search (UPC, name, brand)
- `GET /api/v1/products/{upc}/lots/` — lot codes and distribution
- `GET /api/v1/clinical/investigations/{id}/product-traceback/`

New schemas: `schemas/products.json`, `schemas/transactions.json`

## Privacy & Security Impact

- `consumer_hash` is a one-way HMAC — not reversible without `ANONYMIZATION_SALT`
- Store geohash precision-4 only (~40km radius) — no store-level precision
- Transaction data classified as **internal** (not PHI)
- Retail partner connection credentials stored encrypted in `RetailPartnerConfig`
- Requires Security & Privacy Board review: this is a new category of data about consumer behavior

## Alternatives Considered

**Direct consumer self-report of purchases** — Lower data quality, relies on recall. Retail connectors give ground-truth purchase records.

**Partner-pushed data (webhook)** — Supported via `connector_type='webhook'` but not the only option; some partners can only do SFTP or API pull.

## Open Questions

1. What is the minimum number of matched transactions needed before product traceback is surfaced in the portal?
2. Should retail transaction data have a maximum retention period (e.g., 18 months)?
3. Which specific retailers are candidates for the first pilot connector?
4. Does HMAC-SHA256 of loyalty ID meet de-identification requirements under HIPAA Safe Harbor given it's keyed with a per-deployment salt?

## References

- `services/core/apps/clinical/traceback.py`
- `services/core/apps/recalls/matching.py`
