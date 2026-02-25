"""WebSocket routing for real-time updates"""

from django.urls import re_path
from .consumers import SensorConsumer, AlertConsumer, AdvisoryConsumer, RecallConsumer

websocket_urlpatterns = [
    # Sensor streams — optional restaurant_id capture for restaurant-specific data
    re_path(r'ws/sensors/(?P<restaurant_id>[0-9]+)/$', SensorConsumer.as_asgi()),
    re_path(r'ws/sensors/$',                           SensorConsumer.as_asgi()),

    # Alert streams — per-restaurant or per-user
    re_path(r'ws/alerts/restaurant/(?P<restaurant_id>[0-9]+)/$', AlertConsumer.as_asgi()),
    re_path(r'ws/alerts/$',                                       AlertConsumer.as_asgi()),

    # Public feeds — no auth required
    re_path(r'ws/advisories/$', AdvisoryConsumer.as_asgi()),
    re_path(r'ws/recalls/$',    RecallConsumer.as_asgi()),
]
