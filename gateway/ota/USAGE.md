# OTA Update System

## Quick Start

### On Cloud - Create Update

```bash
cd ~/healthguard/edge-gateway/ota

python ota_manager.py create-update \
  --version 1.2.0 \
  --description "Add humidity sensor support" \
  --images '{"mqtt-bridge": "healthguard/mqtt-bridge:1.2.0"}' \
  --critical
```

### On Cloud - Rollout Update

```bash
python ota_manager.py rollout \
  --version 1.2.0 \
  --gateways "boston_001,boston_002,boston_003" \
  --percentage 50 \
  --stagger 5
```

### On Gateway - Check for Updates

```bash
cd /opt/restaurant-gateway/ota

# Check if update available
python ota_client.py check

# Apply latest update
python ota_client.py update

# Apply specific version
python ota_client.py update --version 1.2.0

# Rollback to previous version
python ota_client.py rollback
```

### Using Helper Script

```bash
cd /opt/restaurant-gateway/ota

# Create backup
./ota-helper.sh backup

# Health check
./ota-helper.sh health-check

# Manual update
./ota-helper.sh update /tmp/update_manifest.json
```

## Update Flow

```
1. Cloud creates update manifest
   ├─ Sign manifest with private key
   ├─ Upload to S3
   └─ Mark as 'STAGED'

2. Gateway checks for updates
   ├─ Poll API or listen to MQTT
   └─ Download manifest + signature

3. Gateway verifies update
   ├─ Verify signature with public key
   └─ Check version compatibility

4. Gateway applies update
   ├─ Create system backup
   ├─ Pull new Docker images
   ├─ Stop services
   ├─ Apply update
   ├─ Start services
   └─ Health check

5a. Success → Report to cloud
5b. Failure → Automatic rollback
```

## Security

- **Signature Verification**: RSA-2048 signing
- **Public Key**: Installed on gateways
- **Private Key**: Kept secure on cloud
- **Manifest Validation**: Before applying

## Rollback

Automatic rollback triggered on:
- Health check failure
- Service startup failure
- MQTT connection failure
- Timeout (30 minutes default)

Rollback restores:
- docker-compose.yml
- Configuration files
- Database (from backup)
- Previous Docker images

## Monitoring

Track updates via Django admin or API:
- Gateway update status
- Rollout progress
- Success/failure rates
- Rollback occurrences
