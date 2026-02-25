"""
Django signals for the alerts app.

post_save on Alert → broadcast to the restaurant's WebSocket channel group
so connected dashboard clients receive real-time notifications without polling.
"""

import logging

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Alert

logger = logging.getLogger(__name__)


def _serialize_alert(alert: Alert) -> dict:
    return {
        "id":         alert.pk,
        "alert_type": alert.alert_type,
        "severity":   alert.severity,
        "status":     alert.status,
        "title":      alert.title,
        "message":    alert.message,
        "restaurant_id": alert.restaurant_id,
        "device_id":  alert.device_id,
        "created_at": alert.created_at.isoformat() if alert.created_at else None,
    }


@receiver(post_save, sender=Alert)
def broadcast_alert(sender, instance: Alert, created: bool, **kwargs):
    """
    Broadcast newly created (or updated) alerts to the restaurant-level
    WebSocket channel group.  Only fires for ACTIVE alerts to avoid
    flooding clients with ack/resolve noise.
    """
    if instance.status != Alert.AlertStatus.ACTIVE:
        return

    channel_layer = get_channel_layer()
    if channel_layer is None:
        return

    group_name = f'alerts_restaurant_{instance.restaurant_id}'
    payload = {
        "type": "alert.update",
        "data": _serialize_alert(instance),
    }

    try:
        async_to_sync(channel_layer.group_send)(group_name, payload)
    except Exception:
        logger.warning(
            "WebSocket broadcast failed for alert %d to group %s",
            instance.pk, group_name, exc_info=True,
        )
