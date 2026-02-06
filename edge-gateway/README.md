# Edge Gateway - Restaurant Local Processing

Local edge computing gateway that runs on Raspberry Pi. Processes sensor data locally and syncs to cloud when available.

## Features

- Works completely offline during internet outages
- Real-time temperature compliance checking
- Local data buffering (7-30 days)
- Zigbee sensor network management
- Automatic cloud sync when connectivity restored

## Hardware Requirements

- Raspberry Pi 4 (4GB+ RAM recommended)
- Zigbee Coordinator (SONOFF Zigbee 3.0 USB Dongle Plus)
- 32GB+ SD Card
- 5V 3A Power Supply

## Quick Start

```bash
# Copy to Raspberry Pi
scp -r edge-gateway/ pi@raspberrypi.local:/home/pi/healthguard-gateway

# SSH into Pi
ssh pi@raspberrypi.local

# Start services
cd /home/pi/healthguard-gateway
docker-compose up -d
```

## Services

- **zigbee2mqtt** - Zigbee device communication
- **mosquitto** - Local MQTT broker
- **mqtt-bridge** - Python bridge for cloud sync
- **local-db** - PostgreSQL for local data storage

## Configuration

Edit `.env` file:

```env
RESTAURANT_ID=boston_001
GATEWAY_API_KEY=your-api-key
CLOUD_MQTT_URL=mqtts://mqtt.healthguard.com:8883
LOCAL_DB_PASSWORD=secure-password
```

## Development

```bash
# Build and run locally
docker-compose -f docker-compose.dev.yml up

# View logs
docker-compose logs -f mqtt-bridge

# Connect to local MQTT
mosquitto_sub -h localhost -t "restaurant/+/sensor/#"
```
