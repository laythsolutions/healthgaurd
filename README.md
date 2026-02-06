# HealthGuard - Restaurant Compliance Monitoring Platform

A hybrid edge-cloud IoT platform for automated restaurant health compliance monitoring with real-time sensors, predictive analytics, and intelligent reporting.

## System Status

**Overall Progress: 100% Complete ✅**

| Component | Status | Notes |
|-----------|--------|-------|
| Cloud Backend | ✅ Complete | Django + TimescaleDB + Celery |
| Edge Gateway | ✅ Complete | Raspberry Pi + MQTT + Docker |
| Mobile App | ✅ Complete | Flutter with offline support |
| Web Dashboard | ✅ Complete | Next.js 14 + shadcn/ui |
| Data Intelligence | ✅ Complete | Public data harvesters + ML models |
| OTA Updates | ✅ Complete | RSA-signed updates with rollback |
| Compliance Reports | ✅ Complete | PDF generation + scheduling |
| Alert System | ✅ Complete | SMS (Twilio) + Email (SendGrid) + Push (Firebase) + Webhooks |
| Authentication | ✅ Complete | JWT + OAuth2 + MFA + API Keys + Session Management |

## Quick Start

```bash
# Start all services
docker-compose -f docker-compose.dev.yml up -d

# Access services
# - Web Dashboard: http://localhost:3000
# - API: http://localhost:8000
# - API Docs: http://localhost:8000/api/docs
# - MQTT Broker: mqtt://localhost:1883
```

## Project Structure

```
healthguard/
├── edge-gateway/      # Raspberry Pi edge computing (Python + Docker)
│   ├── mqtt-bridge/   # Offline-first MQTT bridge
│   ├── ota/           # OTA update client
│   └── docker/        # Docker compose for edge services
├── cloud-backend/     # Django REST API + TimescaleDB
│   └── apps/
│       ├── accounts/      # Authentication & authorization
│       ├── restaurants/   # Restaurant & location management
│       ├── devices/       # IoT device management
│       ├── sensors/       # Time-series sensor data
│       ├── alerts/        # Alert rules & notifications
│       ├── analytics/     # Predictive analytics
│       ├── reports/       # PDF compliance reports
│       └── ota/           # OTA update management
├── web-dashboard/     # Next.js multi-location dashboard
├── mobile-app/        # Flutter app for restaurant staff
├── data-intelligence/ # Public data harvesters + ML
│   ├── harvesters/    # State health department APIs
│   ├── processors/    # Risk scoring & lead generation
│   └── analytics/     # Predictive models
├── shared/            # Shared schemas, types, utilities
└── docs/              # Technical documentation
```

## Key Features

### Real-Time Monitoring
- Zigbee temperature sensors (4-hour battery, 2-year life)
- Automatic readings every 15 minutes
- Offline-first operation with edge computing
- Local PostgreSQL caching for 7-30 days

### Compliance Reporting
- 8-12 page comprehensive PDF reports
- Automated scheduling (daily, weekly, monthly, quarterly)
- Inspection preparation checklists
- One-page scorecards for management
- Email delivery with attachments

### Predictive Analytics
- Inspection date prediction (±30 days)
- Risk scoring (5-factor model)
- Lead scoring for sales (6-factor model)
- Market penetration analysis
- Competitor intelligence

### OTA Updates
- RSA-2048 signed updates
- Automatic rollback on failure
- Staged rollout capability
- Zero-downtime deployments

## Tech Stack

### Edge (Raspberry Pi 4)
- Python 3.11, MQTT, Docker Compose
- PostgreSQL (local cache)
- Zigbee2MQTT (sensor communication)

### Cloud Backend
- Django 4.2, Django REST Framework
- TimescaleDB (time-series data)
- PostgreSQL (application data)
- Celery + Redis (background tasks)
- HiveMQ (cloud MQTT broker)

### Web Dashboard
- Next.js 14, React 18
- TypeScript, Tailwind CSS
- shadcn/ui components
- Zustand + React Query

### Mobile App
- Flutter 3.x, Dart
- Riverpod (state management)
- SQLite (local cache)
- MQTT client

### Data Intelligence
- Python 3.11, FastAPI
- Scikit-learn, Pandas
- Async HTTP clients
- Public API integrations

## API Endpoints

### Authentication
- `POST /api/v1/auth/register/` - Register new user
- `POST /api/v1/auth/login/` - Login (returns JWT)
- `POST /api/v1/auth/logout/` - Logout
- `GET /api/v1/auth/me/` - Get current user
- `POST /api/v1/auth/change_password/` - Change password
- `GET /api/v1/auth/oauth_url/` - Get OAuth2 authorization URL
- `POST /api/v1/auth/oauth_callback/` - OAuth2 callback
- `POST /api/v1/auth/forgot_password/` - Request password reset
- `POST /api/v1/auth/reset_password/` - Reset password
- `GET /api/v1/auth/mfa_status/` - Get MFA status
- `POST /api/v1/auth/mfa_setup/` - Set up MFA
- `POST /api/v1/auth/mfa_verify/` - Verify MFA token
- `GET /api/v1/auth/api_keys/` - List API keys
- `POST /api/v1/auth/create_api_key/` - Create API key
- `GET /api/v1/auth/sessions/` - List active sessions

### Restaurants
- `GET /api/v1/restaurants/` - List restaurants
- `POST /api/v1/restaurants/` - Create restaurant
- `GET /api/v1/restaurants/{id}/` - Get details

### Sensors & Devices
- `GET /api/v1/sensors/readings/` - Get sensor data
- `POST /api/v1/devices/` - Register device
- `GET /api/v1/devices/{id}/status/` - Device status

### Alerts
- `GET /api/v1/alerts/` - List alerts
- `POST /api/v1/alerts/rules/` - Create alert rule
- `PUT /api/v1/alerts/{id}/acknowledge/` - Acknowledge alert

### Reports
- `POST /api/v1/reports/generate/` - Generate report
- `GET /api/v1/reports/{id}/` - Get report status
- `POST /api/v1/reports/schedules/` - Create schedule
- `GET /api/v1/reports/summary/` - Get statistics

### OTA Updates
- `GET /api/v1/ota/manifests/` - List available updates
- `POST /api/v1/ota/manifests/` - Create update manifest
- `POST /api/v1/ota/gateways/{id}/deploy/` - Deploy update

## Documentation

- [Compliance Reports Overview](docs/COMPLIANCE_REPORTS_OVERVIEW.md)
- [OTA Update System](docs/OTA_SYSTEM_OVERVIEW.md)
- [Data Intelligence](docs/DATA_INTELLIGENCE_OVERVIEW.md)

## Business Model

- **Hardware**: $299 one-time (Raspberry Pi + sensors)
- **Software**: $99/month per location
- **Gross Margin**: ~95% after hardware recoup
- **Payback Period**: ~3 months for customers

## Architecture

Edge-first design that works completely offline during internet outages. All critical compliance checking happens at the edge with automatic cloud sync when connectivity is restored.

## License

Proprietary - All Rights Reserved
