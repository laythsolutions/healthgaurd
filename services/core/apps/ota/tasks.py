"""Celery tasks for OTA updates"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
import logging

from .models import OTAManifest, GatewayUpdateStatus, GatewayBackup

logger = logging.getLogger(__name__)


@shared_task
def check_for_pending_updates():
    """Check for gateways that need updates"""

    pending_updates = GatewayUpdateStatus.objects.filter(
        state='PENDING'
    ).select_related('manifest', 'restaurant')

    logger.info(f"Found {pending_updates.count()} pending updates")

    for update_status in pending_updates:
        trigger_gateway_update.delay(update_status.id)


@shared_task
def trigger_gateway_update(update_status_id: int):
    """Trigger update on gateway via MQTT"""

    try:
        update_status = GatewayUpdateStatus.objects.get(id=update_status_id)
        manifest = update_status.manifest

        logger.info(f"Triggering update for {update_status.gateway_id}")

        # Update state
        update_status.state = 'DOWNLOADING'
        update_status.save()

        # Publish MQTT message to gateway
        # This would use your MQTT client
        update_message = {
            'command': 'update',
            'version': manifest.version,
            'manifest_url': manifest.manifest_url,
            'signature_url': manifest.signature_url,
            'critical': manifest.critical,
            'update_id': update_status_id
        }

        # Publish to gateway topic
        import paho.mqtt.client as mqtt
        import json

        client = mqtt.Client()
        client.connect('localhost', 1883, 60)
        client.publish(f"gateway/{update_status.gateway_id}/commands/update", json.dumps(update_message))
        client.disconnect()

        logger.info(f"Update command sent to {update_status.gateway_id}")

    except Exception as e:
        logger.error(f"Failed to trigger update: {e}")
        # Mark as failed
        update_status.state = 'FAILED'
        update_status.error_message = str(e)
        update_status.save()


@shared_task
def monitor_update_progress(update_status_id: int):
    """Monitor update progress and handle timeouts"""

    update_status = GatewayUpdateStatus.objects.get(id=update_status_id)

    # Check if update is taking too long
    if update_status.state == 'APPLYING':
        timeout_minutes = 30
        timeout = timezone.now() - timedelta(minutes=timeout_minutes)

        if update_status.started_at < timeout:
            logger.warning(f"Update {update_status_id} timed out after {timeout_minutes} minutes")

            # Mark as failed
            update_status.state = 'FAILED'
            update_status.error_message = f'Update timed out after {timeout_minutes} minutes'
            update_status.save()

            # Trigger rollback if safe
            if update_status.manifest.rollback_safe:
                trigger_gateway_rollback.delay(update_status_id)


@shared_task
def trigger_gateway_rollback(update_status_id: int):
    """Trigger rollback on gateway"""

    try:
        update_status = GatewayUpdateStatus.objects.get(id=update_status_id)

        logger.info(f"Triggering rollback for {update_status.gateway_id}")

        # Publish rollback command via MQTT
        rollback_message = {
            'command': 'rollback',
            'update_id': update_status_id
        }

        import paho.mqtt.client as mqtt
        import json

        client = mqtt.Client()
        client.connect('localhost', 1883, 60)
        client.publish(f"gateway/{update_status.gateway_id}/commands/rollback", json.dumps(rollback_message))
        client.disconnect()

        logger.info(f"Rollback command sent to {update_status.gateway_id}")

    except Exception as e:
        logger.error(f"Failed to trigger rollback: {e}")


@shared_task
def cleanup_old_backups():
    """Clean up old gateway backups"""

    # Keep backups for 30 days
    cleanup_date = timezone.now() - timedelta(days=30)

    old_backups = GatewayBackup.objects.filter(
        created_at__lt=cleanup_date,
        is_cleaned_up=False
    )

    logger.info(f"Found {old_backups.count()} old backups to clean up")

    for backup in old_backups:
        try:
            # Delete from S3 or wherever backups are stored
            # This is a placeholder - implement based on your storage

            backup.is_cleaned_up = True
            backup.save()

            logger.info(f"Cleaned up backup {backup.id}")

        except Exception as e:
            logger.error(f"Failed to cleanup backup {backup.id}: {e}")


@shared_task
def calculate_rollout_statistics(manifest_id: int):
    """Calculate rollout statistics for a manifest"""

    manifest = OTAManifest.objects.get(id=manifest_id)

    # Count gateway statuses
    total = GatewayUpdateStatus.objects.filter(manifest=manifest).count()
    updated = GatewayUpdateStatus.objects.filter(manifest=manifest, state='SUCCESS').count()
    failed = GatewayUpdateStatus.objects.filter(manifest=manifest, state='FAILED').count()

    manifest.total_gateways = total
    manifest.updated_gateways = updated
    manifest.failed_gateways = failed
    manifest.save()

    logger.info(f"Manifest {manifest.version}: {updated}/{total} updated")

    # Check if rollout is complete
    if total > 0 and (updated + failed) == total:
        manifest.status = 'COMPLETED'
        manifest.save()

        logger.info(f"Rollout complete for {manifest.version}")
