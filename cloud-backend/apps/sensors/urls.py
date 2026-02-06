"""URL configuration for sensors app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    SensorReadingViewSet,
    SensorAggregateViewSet,
    TemperatureLogViewSet,
)

router = DefaultRouter()
router.register(r'readings', SensorReadingViewSet, basename='sensor-reading')
router.register(r'aggregates', SensorAggregateViewSet, basename='sensor-aggregate')
router.register(r'temperature-logs', TemperatureLogViewSet, basename='temperature-log')

urlpatterns = [
    path('', include(router.urls)),
]
