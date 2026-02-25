# OTA Update System for Edge Gateways

Over-The-Air update system for Raspberry Pi gateways with automatic rollback on failure.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│                    CLOUD OTA SERVICE                     │
│  • Update manifests                                      │
│  • Docker image registry                                │
│  • Version management                                    │
│  • Rollback triggers                                    │
└────────────────────┬─────────────────────────────────────┘
                     │ HTTPS
                     ▼
┌──────────────────────────────────────────────────────────┐
│              EDGE GATEWAY (OTA AGENT)                    │
│  ┌────────────────────────────────────────────────────┐ │
│  │ 1. Check for updates                               │ │
│  │ 2. Download update package                         │ │
│  │ 3. Verify signature                                │ │
│  │ 4. Create system backup                            │ │
│  │ 5. Stop services                                   │ │
│  │ 6. Apply update                                    │ │
│  │ 7. Start services                                  │ │
│  │ 8. Health check                                    │ │
│  │ 9. Report success OR rollback                      │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
```

## Features

- **Zero-Downtime Updates**: Graceful service restart
- **Automatic Rollback**: Revert on failure
- **Signature Verification**: Security validation
- **Health Checks**: Post-update verification
- **Backup/Restore**: System state protection
- **Staged Rollout**: Deploy to subset first
- **Monitoring**: Real-time update status

## Update Flow

```
Gateway → Check Update → Download → Verify → Backup
   ↓                                                ↓
Rollback ← Health Check ← Apply Update ← Stop Services
   ↓           ↓
  Success    Report Status
```

## Quick Start

```bash
# On cloud - Create update
python ota_manager.py create-update \
  --version 1.2.0 \
  --docker-image healthguard/mqtt-bridge:1.2.0

# On gateway - Check for updates
python ota_client.py check

# Apply update
python ota_client.py update
```
