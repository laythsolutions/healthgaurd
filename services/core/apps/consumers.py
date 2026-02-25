"""WebSocket consumers for real-time updates"""

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class SensorConsumer(AsyncJsonWebsocketConsumer):
    """Consumer for real-time sensor updates (auth required)."""

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return

        # Join restaurant-specific group if restaurant_id given in URL
        self.restaurant_id = self.scope['url_route']['kwargs'].get('restaurant_id')
        if self.restaurant_id:
            self.group_name = f'sensors_{self.restaurant_id}'
        else:
            self.group_name = f'sensors_user_{user.id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def sensor_update(self, event):
        """Relay sensor update to client."""
        await self.send_json(event['data'])


class AlertConsumer(AsyncJsonWebsocketConsumer):
    """
    Consumer for real-time alert updates (auth required).

    Supports two modes:
      ws/alerts/                              → user-level group  alerts_user_{id}
      ws/alerts/restaurant/<restaurant_id>/   → restaurant group  alerts_restaurant_{id}
    """

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return

        restaurant_id = self.scope['url_route']['kwargs'].get('restaurant_id')
        if restaurant_id:
            self.group_name = f'alerts_restaurant_{restaurant_id}'
        else:
            self.group_name = f'alerts_user_{user.id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def alert_update(self, event):
        """Relay alert to client."""
        await self.send_json(event['data'])


class AdvisoryConsumer(AsyncJsonWebsocketConsumer):
    """
    Public (no-auth) consumer for outbreak advisory updates.

    Clients subscribe to ws/advisories/ to receive push notifications when
    a new OutbreakInvestigation is published or escalated.

    Message envelope:
        { "type": "advisory.new", "data": { ...advisory fields... } }
    """

    GROUP = 'advisories_public'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    # Handler for group_send type "advisory.new"
    async def advisory_new(self, event):
        await self.send_json(event['data'])


class RecallConsumer(AsyncJsonWebsocketConsumer):
    """
    Public (no-auth) consumer for recall alerts.

    Clients subscribe to ws/recalls/ to receive push notifications when
    a new FDA or USDA recall is ingested.

    Message envelope:
        { "type": "recall.new", "data": { ...recall fields... } }
    """

    GROUP = 'recalls_public'

    async def connect(self):
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    # Handler for group_send type "recall.new"
    async def recall_new(self, event):
        await self.send_json(event['data'])
