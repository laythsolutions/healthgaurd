# MQTT message handler for OTA updates

import json
import logging
import paho.mqtt.client as mqtt
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)


class OTAUpdateMQTTHandler:
    """Handle OTA update MQTT messages"""

    def __init__(self):
        self.broker = settings.MQTT_BROKER
        self.port = settings.MQTT_BROKER.get('PORT', 1883)

    def start(self):
        """Start MQTT listener for OTA updates"""

        client = mqtt.Client(client_id="ota_update_handler")
        client.on_connect = self.on_connect
        client.on_message = self.on_message

        client.connect(self.broker, self.port, 60)
        client.loop_forever()

    def on_connect(self, client, userdata, flags, rc):
        """Subscribe to OTA update topics"""

        # Subscribe to update progress messages
        client.subscribe('gateway/+/ota/progress')
        client.subscribe('gateway/+/ota/success')
        client.subscribe('gateway/+/ota/failure')

        logger.info("OTA MQTT handler connected and subscribed")

    def on_message(self, client, userdata, msg):
        """Handle incoming OTA update messages"""

        try:
            # Extract gateway_id from topic
            topic_parts = msg.topic.split('/')
            gateway_id = topic_parts[1]
            message_type = topic_parts[3]

            payload = json.loads(msg.payload.decode())

            if message_type == 'progress':
                self.handle_progress_update(gateway_id, payload)
            elif message_type == 'success':
                self.handle_success(gateway_id, payload)
            elif message_type == 'failure':
                self.handle_failure(gateway_id, payload)

        except Exception as e:
            logger.error(f"Error handling OTA message: {e}")

    def handle_progress_update(self, gateway_id: str, payload: dict):
        """Handle progress update from gateway"""

        from .models import GatewayUpdateStatus

        update_id = payload.get('update_id')
        state = payload.get('state')
        progress = payload.get('progress_percentage')
        step = payload.get('current_step')
        log = payload.get('log')

        try:
            update_status = GatewayUpdateStatus.objects.get(id=update_id)

            if state:
                update_status.state = state
            if progress is not None:
                update_status.progress_percentage = progress
            if step:
                update_status.current_step = step
            if log:
                update_status.log(log)

            update_status.save()

            logger.info(f"Updated progress for {gateway_id}: {progress}%")

        except GatewayUpdateStatus.DoesNotExist:
            logger.error(f"Update status {update_id} not found")

    def handle_success(self, gateway_id: str, payload: dict):
        """Handle successful update"""

        from .models import GatewayUpdateStatus
        from .tasks import calculate_rollout_statistics

        version = payload.get('version')

        try:
            manifest = OTAManifest.objects.get(version=version)
            update_status = GatewayUpdateStatus.objects.get(
                gateway_id=gateway_id,
                manifest=manifest
            )

            update_status.state = 'SUCCESS'
            update_status.completed_at = timezone.now()
            if update_status.started_at:
                duration = update_status.completed_at - update_status.started_at
                update_status.duration_seconds = int(duration.total_seconds())
            update_status.save()

            # Update statistics
            calculate_rollout_statistics.delay(manifest.id)

            logger.info(f"Gateway {gateway_id} successfully updated to {version}")

        except Exception as e:
            logger.error(f"Error handling success for {gateway_id}: {e}")

    def handle_failure(self, gateway_id: str, payload: dict):
        """Handle failed update"""

        from .models import GatewayUpdateStatus
        from .tasks import calculate_rollout_statistics, trigger_gateway_rollback

        version = payload.get('version')
        error = payload.get('error')

        try:
            manifest = OTAManifest.objects.get(version=version)
            update_status = GatewayUpdateStatus.objects.get(
                gateway_id=gateway_id,
                manifest=manifest
            )

            update_status.state = 'FAILED'
            update_status.completed_at = timezone.now()
            update_status.error_message = error
            update_status.save()

            # Update statistics
            calculate_rollout_statistics.delay(manifest.id)

            # Trigger rollback if safe
            if manifest.rollback_safe:
                trigger_gateway_rollback.delay(update_status.id)

            logger.warning(f"Gateway {gateway_id} update failed: {error}")

        except Exception as e:
            logger.error(f"Error handling failure for {gateway_id}: {e}")
