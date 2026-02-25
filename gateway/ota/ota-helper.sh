#!/bin/bash
# OTA Update Helper Script for Edge Gateway
# Run on the gateway to facilitate updates

set -e

GATEWAY_DIR="/opt/restaurant-gateway"
BACKUP_DIR="$GATEWAY_DIR/backups"
TEMP_DIR="/tmp/ota"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Create backup
create_backup() {
    log_info "Creating system backup..."

    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_PATH="$BACKUP_DIR/backup_$TIMESTAMP"
    mkdir -p "$BACKUP_PATH"

    # Backup docker-compose.yml
    cp "$GATEWAY_DIR/docker-compose.yml" "$BACKUP_PATH/"

    # Backup .env
    if [ -f "$GATEWAY_DIR/.env" ]; then
        cp "$GATEWAY_DIR/.env" "$BACKUP_PATH/"
    fi

    # Backup configs
    if [ -d "$GATEWAY_DIR/config" ]; then
        cp -r "$GATEWAY_DIR/config" "$BACKUP_PATH/"
    fi

    # Backup database
    log_info "Backing up database..."
    docker exec local-db pg_dump -U local_user restaurant_local \
        -f "/backups/backup_${TIMESTAMP}.sql"

    # Save metadata
    cat > "$BACKUP_PATH/metadata.json" <<EOF
{
  "version": "$(cat $GATEWAY_DIR/VERSION 2>/dev/null || echo 'unknown')",
  "timestamp": "$TIMESTAMP",
  "backup_path": "$BACKUP_PATH"
}
EOF

    log_info "Backup created at $BACKUP_PATH"
    echo "$BACKUP_PATH"
}

# Restore from backup
restore_backup() {
    BACKUP_PATH=$1

    if [ ! -d "$BACKUP_PATH" ]; then
        log_error "Backup path not found: $BACKUP_PATH"
        exit 1
    fi

    log_info "Restoring from $BACKUP_PATH..."

    # Stop services
    log_info "Stopping services..."
    cd "$GATEWAY_DIR"
    docker-compose down

    # Restore docker-compose.yml
    cp "$BACKUP_PATH/docker-compose.yml" "$GATEWAY_DIR/"

    # Restore .env
    if [ -f "$BACKUP_PATH/.env" ]; then
        cp "$BACKUP_PATH/.env" "$GATEWAY_DIR/"
    fi

    # Restore configs
    if [ -d "$BACKUP_PATH/config" ]; then
        rm -rf "$GATEWAY_DIR/config"
        cp -r "$BACKUP_PATH/config" "$GATEWAY_DIR/"
    fi

    # Restore database
    log_info "Restoring database..."
    BACKUP_FILE=$(ls $BACKUP_PATH/database_*.sql 2>/dev/null | head -1)
    if [ -n "$BACKUP_FILE" ]; then
        docker-compose up -d local-db
        sleep 10
        docker exec local-db psql -U local_user -d restaurant_local \
            -f "/backups/$(basename $BACKUP_FILE)"
    fi

    # Start services
    log_info "Starting services..."
    docker-compose up -d

    # Wait for services to be healthy
    log_info "Waiting for services to start..."
    sleep 30

    log_info "✅ Restore complete"
}

# Health check
health_check() {
    log_info "Running health checks..."

    REQUIRED_SERVICES=("zigbee2mqtt" "mosquitto" "mqtt-bridge" "local-db")
    ALL_HEALTHY=true

    for service in "${REQUIRED_SERVICES[@]}"; do
        if docker inspect -f '{{.State.Running}}' "$service" | grep -q "true"; then
            log_info "✓ $service is running"
        else
            log_error "✗ $service is NOT running"
            ALL_HEALTHY=false
        fi
    done

    # Check MQTT connection
    log_info "Checking MQTT connection..."
    if timeout 5 mosquitto_sub -h localhost -t '$SYS/# -C 1' > /dev/null 2>&1; then
        log_info "✓ MQTT broker is responding"
    else
        log_error "✗ MQTT broker is NOT responding"
        ALL_HEALTHY=false
    fi

    if [ "$ALL_HEALTHY" = true ]; then
        log_info "✅ All health checks passed"
        return 0
    else
        log_error "❌ Health checks failed"
        return 1
    fi
}

# Pull Docker images
pull_images() {
    IMAGES_JSON=$1

    log_info "Pulling Docker images..."

    # Parse JSON and pull images
    echo "$IMAGES_JSON" | python3 -c "
import json
import sys
import subprocess

images = json.load(sys.stdin)
for service, image in images.items():
    print(f'Pulling {service}: {image}')
    subprocess.run(['docker', 'pull', image], check=True)
"

    log_info "✅ Images pulled"
}

# Apply update
apply_update() {
    MANIFEST_FILE=$1

    log_info "Applying update from $MANIFEST_FILE..."

    # Load manifest
    VERSION=$(python3 -c "import json; m=json.load(open('$MANIFEST_FILE')); print(m['version'])")
    DESCRIPTION=$(python3 -c "import json; m=json.load(open('$MANIFEST_FILE')); print(m['description'])")
    IMAGES=$(python3 -c "import json; m=json.load(open('$MANIFEST_FILE')); print(json.dumps(m.get('docker_images', {})))")

    log_info "Update: $VERSION"
    log_info "Description: $DESCRIPTION"

    # Create backup
    BACKUP_PATH=$(create_backup)

    # Pull new images
    if [ -n "$IMAGES" ] && [ "$IMAGES" != "{}" ]; then
        pull_images "$IMAGES"
    fi

    # Stop services
    log_info "Stopping services..."
    cd "$GATEWAY_DIR"
    docker-compose down

    # Apply update (this would be more sophisticated)
    log_info "Applying update..."

    # Start services
    log_info "Starting services..."
    docker-compose up -d

    # Wait for services
    log_info "Waiting for services to stabilize..."
    sleep 30

    # Health check
    if health_check; then
        # Update version
        echo "$VERSION" > "$GATEWAY_DIR/VERSION"

        log_info "✅ Update $VERSION applied successfully!"
        return 0
    else
        log_error "❌ Health check failed, rolling back..."

        restore_backup "$BACKUP_PATH"

        log_info "✅ Rollback complete"
        return 1
    fi
}

# Main command dispatcher
case "${1:-}" in
    backup)
        create_backup
        ;;
    restore)
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 restore <backup_path>"
            exit 1
        fi
        restore_backup "$2"
        ;;
    health-check)
        health_check
        ;;
    update)
        if [ -z "${2:-}" ]; then
            log_error "Usage: $0 update <manifest_file>"
            exit 1
        fi
        apply_update "$2"
        ;;
    *)
        echo "Usage: $0 {backup|restore|health-check|update}"
        echo ""
        echo "Commands:"
        echo "  backup                - Create system backup"
        echo "  restore <path>        - Restore from backup"
        echo "  health-check          - Run health checks"
        echo "  update <manifest>     - Apply update from manifest file"
        exit 1
        ;;
esac
