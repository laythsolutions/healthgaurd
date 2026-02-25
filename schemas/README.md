# Shared Data Schemas

This directory contains canonical schema definitions for all data domains and APIs
in healthgaurd. These serve as contracts between services, external integrations,
and contributors.

## Files

### API specifications

| File | Format | Description |
|------|--------|-------------|
| `openapi.yaml` | OpenAPI 3.1.0 | Full REST API specification — all HTTP endpoints, auth schemes, request/response shapes |
| `asyncapi.yaml` | AsyncAPI 2.6.0 | WebSocket channels — real-time sensor data, alerts, advisories, recalls |

### JSON Schema — data model definitions

| Schema | Domain | Version |
|--------|--------|---------|
| `establishments.json` | Food service establishments | 1.0.0 |
| `inspections.json` | Health department inspections | 1.0.0 |
| `recalls.json` | Product recalls (FDA/USDA) | 1.0.0 |
| `clinical_cases.json` | Anonymized clinical cases | 1.0.0 |
| `sensor_readings.json` | IoT sensor time-series | 1.0.0 |

## Versioning

Schemas follow semantic versioning (`MAJOR.MINOR.PATCH`):
- **PATCH:** Clarifications, description updates, no structural change.
- **MINOR:** Backward-compatible additions (new optional fields).
- **MAJOR:** Breaking changes — requires RFC and migration plan.

The `$id` field in each schema encodes the version:
```
https://schemas.[project-domain]/v1/establishments.json
```

## Viewing the OpenAPI spec

Use any OpenAPI-compatible tool:

```bash
# Swagger UI (Docker)
docker run -p 8080:8080 -e SWAGGER_JSON=/spec/openapi.yaml \
  -v $(pwd)/schemas:/spec swaggerapi/swagger-ui

# Or: paste schemas/openapi.yaml into https://editor.swagger.io
```

## Validating JSON Schema

```python
import jsonschema, json

with open("schemas/recalls.json") as f:
    schema = json.load(f)

jsonschema.validate(instance=my_recall_dict, schema=schema)
```

## Privacy notes

- `clinical_cases.json` contains no PII fields by design.
- `establishments.json` includes full address; access controls are enforced at the API layer.
- Schemas with `"sensitivity": "high"` in their metadata require role-based access.
