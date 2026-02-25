#!/usr/bin/env python
"""
MQTT Smart Bridge - Connects local Zigbee sensors to cloud
Works offline with local buffering and automatic sync
"""

import os
import json
import time
import asyncio
import logging
from datetime import datetime
from collections import deque
from pathlib import Path

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

from mqtt_bridge.compliance import ComplianceEngine
from mqtt_bridge.storage import LocalStorage
from mqtt_bridge.sync import CloudSync
from mqtt_bridge.utils import setup_logging

# Load environment
load_dotenv()

# Setup logging
logger = setup_logging()

# Configuration
RESTAURANT_ID = os.getenv('RESTAURANT_ID')
CLOUD_MQTT_URL = os.getenv('CLOUD_MQTT_URL', 'mqtts://mqtt.healthguard.com:8883')
LOCAL_MQTT_URL = os.getenv('LOCAL_MQTT_URL', 'mqtt://mosquitto:1883')
API_KEY = os.getenv('GATEWAY_API_KEY')

# Offline buffer (stores messages when cloud is unavailable)
OFFLINE_BUFFER = deque(maxlen=10000)


class MQTTSmartBridge:
    """Intelligent MQTT bridge with offline support"""

    def __init__(self):
        self.restaurant_id = RESTAURANT_ID
        self.local_client = None
        self.cloud_client = None
        self.is_cloud_connected = False

        # Initialize components
        self.storage = LocalStorage()
        self.compliance = ComplianceEngine(self.storage)
        self.cloud_sync = CloudSync(CLOUD_MQTT_URL, API_KEY)

        # Device configurations
        self.device_configs = self.storage.load_device_configs()

        logger.info(f"MQTT Bridge initialized for {self.restaurant_id}")

    async def start(self):
        """Start the MQTT bridge"""
        logger.info("Starting MQTT Smart Bridge...")

        # Connect to local MQTT broker
        await self.connect_local()

        # Connect to cloud (with retry)
        asyncio.create_task(self.connect_cloud_with_retry())

        # Start sync task
        asyncio.create_task(self.sync_offline_data())

        # Start health monitoring
        asyncio.create_task(self.monitor_health())

        logger.info("MQTT Smart Bridge started successfully")

    async def connect_local(self):
        """Connect to local MQTT broker"""
        try:
            self.local_client = mqtt.Client(client_id=f"bridge_local_{self.restaurant_id}")

            # Setup callbacks
            self.local_client.on_connect = self.on_local_connect
            self.local_client.on_message = self.on_local_message
            self.local_client.on_disconnect = self.on_local_disconnect

            # Connect to local broker
            host, port = LOCAL_MQTT_URL.replace('mqtt://', '').split(':')
            self.local_client.connect(host, int(port), 60)

            # Start loop
            self.local_client.loop_start()

            logger.info(f"Connected to local MQTT broker at {LOCAL_MQTT_URL}")

        except Exception as e:
            logger.error(f"Failed to connect to local MQTT: {e}")
            raise

    def on_local_connect(self, client, userdata, flags, rc):
        """Callback when connected to local broker"""
        if rc == 0:
            logger.info("Successfully connected to local MQTT broker")

            # Subscribe to all Zigbee2MQTT messages
            client.subscribe("zigbee2mqtt/#")
            logger.info("Subscribed to zigbee2mqtt/#")

        else:
            logger.error(f"Failed to connect to local MQTT broker: {rc}")

    def on_local_message(self, client, userdata, msg):
        """Handle incoming message from local sensors"""
        try:
            # Parse topic
            topic_parts = msg.topic.split('/')
            device_id = topic_parts[-1]

            # Parse payload
            data = json.loads(msg.payload)

            # Standardize message format
            message = {
                'restaurant_id': self.restaurant_id,
                'device_id': device_id,
                'timestamp': datetime.utcnow().isoformat(),
                'data': data,
                'processed_locally': True
            }

            logger.debug(f"Received message from {device_id}: {data}")

            # Process locally (works offline!)
            self.process_message_locally(message)

            # Store locally
            self.storage.store_sensor_reading(message)

            # Forward to cloud if connected
            if self.is_cloud_connected:
                self.forward_to_cloud(message)
            else:
                # Buffer for later sync
                OFFLINE_BUFFER.append({
                    'type': 'sensor_reading',
                    'data': message
                })
                logger.debug("Cloud not connected - buffered message for sync")

        except Exception as e:
            logger.error(f"Error processing local message: {e}")

    def process_message_locally(self, message):
        """Process message locally (works offline)"""
        device_id = message['device_id']
        data = message['data']

        # Get device config
        config = self.device_configs.get(device_id, {})

        # Check temperature compliance
        if 'temperature' in data:
            temp = data['temperature']
            min_temp = config.get('temp_min_f')
            max_temp = config.get('temp_max_f')

            if min_temp and max_temp:
                # Check compliance
                if temp < min_temp or temp > max_temp:
                    logger.warning(f"Temperature violation: {device_id} = {temp}°F (range: {min_temp}-{max_temp})")

                    # Generate alert locally
                    alert = self.compliance.generate_alert(
                        device_id=device_id,
                        temperature=temp,
                        min_temp=min_temp,
                        max_temp=max_temp,
                        location=config.get('location', 'Unknown')
                    )

                    # Store alert locally
                    self.storage.store_alert(alert)

                    # Publish to local alert topic
                    alert_topic = f"restaurant/{self.restaurant_id}/alerts/critical"
                    self.local_client.publish(alert_topic, json.dumps(alert))
                    logger.info(f"Published local alert to {alert_topic}")

                    # Forward to cloud if connected
                    if self.is_cloud_connected:
                        self.forward_alert_to_cloud(alert)

    def forward_to_cloud(self, message):
        """Forward message to cloud"""
        try:
            topic = f"restaurant/{self.restaurant_id}/sensor/{message['device_id']}"
            self.cloud_client.publish(topic, json.dumps(message), qos=1)
            logger.debug(f"Forwarded message to cloud: {topic}")
        except Exception as e:
            logger.error(f"Failed to forward message to cloud: {e}")

    def forward_alert_to_cloud(self, alert):
        """Forward alert to cloud"""
        try:
            topic = f"restaurant/{self.restaurant_id}/alerts/critical"
            self.cloud_client.publish(topic, json.dumps(alert), qos=1)
            logger.info(f"Forwarded alert to cloud: {topic}")
        except Exception as e:
            logger.error(f"Failed to forward alert to cloud: {e}")

    async def connect_cloud_with_retry(self):
        """Connect to cloud with automatic retry"""
        while True:
            try:
                await self.cloud_sync.connect()
                self.is_cloud_connected = True
                logger.info("Connected to cloud MQTT broker")

                # Subscribe to cloud commands
                await self.cloud_sync.subscribe(f"restaurant/{self.restaurant_id}/commands/#")

                # Process incoming cloud messages
                asyncio.create_task(self.process_cloud_messages())

            except Exception as e:
                logger.error(f"Failed to connect to cloud: {e}")
                self.is_cloud_connected = False

            # Retry in 30 seconds
            await asyncio.sleep(30)

    async def sync_offline_data(self):
        """Sync buffered data to cloud"""
        while True:
            if self.is_cloud_connected and OFFLINE_BUFFER:
                logger.info(f"Syncing {len(OFFLINE_BUFFER)} buffered messages to cloud...")

                while OFFLINE_BUFFER:
                    item = OFFLINE_BUFFER.popleft()

                    try:
                        if item['type'] == 'sensor_reading':
                            self.forward_to_cloud(item['data'])
                        elif item['type'] == 'alert':
                            self.forward_alert_to_cloud(item['data'])

                        # Small delay to avoid overwhelming the broker
                        await asyncio.sleep(0.1)

                    except Exception as e:
                        logger.error(f"Failed to sync item: {e}")
                        # Put it back in the buffer
                        OFFLINE_BUFFER.appendleft(item)
                        break

                logger.info("Offline data sync complete")

            # Check every 10 seconds
            await asyncio.sleep(10)

    async def process_cloud_messages(self):
        """Process incoming messages from cloud"""
        async for message in self.cloud_sync.messages():
            try:
                data = json.loads(message.payload)
                logger.info(f"Received cloud command: {data}")

                # Handle commands
                command = data.get('command')
                if command == 'update_config':
                    self.device_configs = data.get('configs', {})
                    self.storage.save_device_configs(self.device_configs)
                    logger.info("Updated device configurations from cloud")

            except Exception as e:
                logger.error(f"Error processing cloud message: {e}")

    async def monitor_health(self):
        """Monitor system health"""
        while True:
            try:
                # Publish health status
                health = {
                    'restaurant_id': self.restaurant_id,
                    'timestamp': datetime.utcnow().isoformat(),
                    'cloud_connected': self.is_cloud_connected,
                    'buffered_messages': len(OFFLINE_BUFFER),
                    'uptime': time.time()
                }

                health_topic = f"restaurant/{self.restaurant_id}/health"
                self.local_client.publish(health_topic, json.dumps(health))

            except Exception as e:
                logger.error(f"Error publishing health status: {e}")

            # Every 60 seconds
            await asyncio.sleep(60)

    def on_local_disconnect(self, client, userdata, rc):
        """Callback when disconnected from local broker"""
        logger.warning(f"Disconnected from local MQTT broker: {rc}")


async def main():
    """Main entry point"""
    logger.info("Starting HealthGuard MQTT Smart Bridge...")

    bridge = MQTTSmartBridge()

    try:
        await bridge.start()

        # Keep running
        while True:
            await asyncio.sleep(1)

    except KeyboardInterrupt:
        logger.info("Shutting down...")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
