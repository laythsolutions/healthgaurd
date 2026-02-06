# Data Intelligence Layer

Public health inspection data harvesting and analytics platform for predictive lead scoring and sales enablement.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│               DATA INTELLIGENCE PLATFORM                     │
├─────────────────────────────────────────────────────────────┤
│  1. DATA HARVESTING                                          │
│     • 50+ State Health Department APIs                      │
│     • Municipal portal scrapers (1,000+ jurisdictions)       │
│     • FOIA automation system                                 │
│     • Business registry correlation                          │
│     • Real-time violation monitoring                        │
├─────────────────────────────────────────────────────────────┤
│  2. DATA PROCESSING                                          │
│     • Violation pattern recognition                          │
│     • Risk scoring algorithms                                │
│     • Predictive modeling (ML)                               │
│     • Competitive intelligence                               │
├─────────────────────────────────────────────────────────────┤
│  3. ANALYTICS & INSIGHTS                                     │
│     • Health inspection risk prediction                      │
│     • Financial impact analysis                              │
│     • Acquisition probability scoring                        │
│     • Optimal intervention timing                            │
├─────────────────────────────────────────────────────────────┤
│  4. SALES ENABLEMENT                                         │
│     • Lead generation & scoring                              │
│     • Personalized outreach packages                         │
│     • ROI calculators with real data                         │
│     • Battle cards & playbooks                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Harvesters (`/harvesters`)
- Public API clients
- Web scrapers
- FOIA automation

### Processors (`/processors`)
- Data normalization
- Risk scoring
- Pattern recognition

### Analytics (`/analytics`)
- ML models
- Predictive analytics
- Business intelligence

### API (`/api`)
- FastAPI endpoints
- Sales enablement tools
- Dashboard integration

## Quick Start

```bash
cd data-intelligence

# Install dependencies
pip install -r requirements.txt

# Run harvesters
python harvesters/run_harvesters.py

# Start analytics API
uvicorn api.main:app --reload
```

## Data Sources

### Federal
- FDA Food Inspections
- CDC Outbreak Database
- USDA Inspection Data

### State (All 50)
- California Retail Food Inspection
- NYC Restaurant Inspections
- Chicago Food Inspections
- Texas Food Establishments
- Florida Restaurants and Pools
- ... 45+ more states

### Municipal (Top 500)
- County health departments
- City inspection portals
- Township permits

## Infrastructure

- **Queue**: Redis/Celery for async processing
- **Database**: PostgreSQL + TimescaleDB
- **Cache**: Redis for hot data
- **Storage**: S3 for raw data
- **ML**: Scikit-learn + XGBoost
