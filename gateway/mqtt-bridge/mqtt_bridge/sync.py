"""Cloud synchronization (async MQTT)"""

import asyncio
import json
import logging
from urllib.parse import urlparse

import aiohttp

logger = logging.getLogger(__name__)


class CloudSync:
    """Handle cloud connection and synchronization"""

    def __init__(self, cloud_mqtt_url, api_key):
        self.cloud_mqtt_url = cloud_mqtt_url
        self.api_key = api_key
        self.client = None
        self.message_queue = asyncio.Queue()

    async def connect(self):
        """Connect to cloud MQTT broker"""
        try:
            # Parse URL
            parsed = urlparse(self.cloud_mqtt_url)

            # Use asyncio-mqtt for async MQTT
            from asyncio_mqtt import Client as MQTTClient

            self.client = MQTTClient(
                hostname=parsed.hostname,
                port=parsed.port,
                username=self.api_key,
                password='',
                tls_context=None if parsed.scheme == 'mqtt' else True
            )

            await self.client.connect()
            logger.info(f"Connected to cloud MQTT at {self.cloud_mqtt_url}")

        except Exception as e:
            logger.error(f"Failed to connect to cloud MQTT: {e}")
            raise

    async def subscribe(self, topic):
        """Subscribe to cloud topic"""
        if self.client:
            await self.client.subscribe(topic)
            logger.info(f"Subscribed to cloud topic: {topic}")

    async def messages(self):
        """Get messages from cloud"""
        if self.client:
            async for message in self.client.messages():
                yield message

    async def publish(self, topic, payload, qos=1):
        """Publish message to cloud"""
        if self.client:
            try:
                await self.client.publish(topic, payload, qos=qos)
            except Exception as e:
                logger.error(f"Failed to publish to cloud: {e}")
                raise

    async def sync_data(self, storage):
        """Sync local data to cloud"""
        # Get unsynced readings
        readings = storage.get_unsynced_readings(limit=100)

        for reading in readings:
            try:
                message = {
                    'device_id': reading['device_id'],
                    'timestamp': reading['timestamp'],
                    'data': reading['data']
                }

                topic = f"restaurant/{storage.restaurant_id}/sensor/{reading['device_id']}"
                await self.publish(topic, json.dumps(message))

                # Mark as synced
                storage.mark_as_synced('sensor_readings', [reading['id']])

            except Exception as e:
                logger.error(f"Failed to sync reading {reading['id']}: {e}")
                break

        logger.info(f"Synced {len(readings)} readings to cloud")
