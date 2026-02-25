"""WebSocket consumers for real-time updates"""

import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async


class SensorConsumer(AsyncJsonWebsocketConsumer):
    """Consumer for real-time sensor updates"""

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return

        # Join restaurant-specific group
        self.restaurant_id = self.scope['url_route']['kwargs'].get('restaurant_id')
        if self.restaurant_id:
            self.group_name = f'sensors_{self.restaurant_id}'
        else:
            # User's default restaurant
            self.group_name = f'sensors_user_{user.id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def sensor_update(self, event):
        """Send sensor update to client"""
        await self.send_json(event['data'])


class AlertConsumer(AsyncJsonWebsocketConsumer):
    """Consumer for real-time alert updates"""

    async def connect(self):
        user = self.scope["user"]
        if user.is_anonymous:
            await self.close()
            return

        # Join user's alert group
        self.group_name = f'alerts_user_{user.id}'

        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def alert_update(self, event):
        """Send alert update to client"""
        await self.send_json(event['data'])
