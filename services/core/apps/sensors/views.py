"""Views for sensors app"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import SensorReading, SensorAggregate, TemperatureLog
from .serializers import (
    SensorReadingSerializer,
    SensorAggregateSerializer,
    TemperatureLogSerializer,
)


class SensorReadingViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SensorReading model (read-only - created via MQTT)"""

    queryset = SensorReading.objects.select_related('device').all()
    serializer_class = SensorReadingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        device_id = self.request.query_params.get('device')
        restaurant_id = self.request.query_params.get('restaurant')
        start = self.request.query_params.get('start')
        end = self.request.query_params.get('end')

        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if restaurant_id:
            queryset = queryset.filter(device__restaurant_id=restaurant_id)

        # Date range filtering
        if start:
            queryset = queryset.filter(timestamp__gte=start)
        if end:
            queryset = queryset.filter(timestamp__lte=end)

        return queryset.order_by('-timestamp')[:1000]  # Limit to 1000 readings

    @action(detail=False, methods=['get'])
    def latest(self, request):
        """Get latest readings for all devices in a restaurant"""
        from apps.devices.models import Device

        restaurant_id = request.query_params.get('restaurant')
        if not restaurant_id:
            return Response({'error': 'restaurant parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        devices = Device.objects.filter(restaurant_id=restaurant_id, status='active')
        latest_readings = []

        for device in devices:
            latest = self.queryset.filter(device=device).first()
            if latest:
                latest_readings.append({
                    'device_id': device.device_id,
                    'device_name': device.name,
                    'location': device.location.name if device.location else None,
                    'temperature': latest.temperature,
                    'humidity': latest.humidity,
                    'battery': latest.battery_percent,
                    'timestamp': latest.timestamp,
                })

        return Response(latest_readings)

    @action(detail=False, methods=['get'])
    def history(self, request):
        """Get historical data for a device"""
        device_id = request.query_params.get('device')
        hours = int(request.query_params.get('hours', 24))

        if not device_id:
            return Response({'error': 'device parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        start_time = timezone.now() - timedelta(hours=hours)
        readings = self.queryset.filter(
            device_id=device_id,
            timestamp__gte=start_time
        )

        serializer = self.get_serializer(readings, many=True)
        return Response(serializer.data)


class SensorAggregateViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for SensorAggregate model"""

    queryset = SensorAggregate.objects.select_related('device').all()
    serializer_class = SensorAggregateSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        device_id = self.request.query_params.get('device')
        aggregate_type = self.request.query_params.get('aggregate_type', 'DAILY')

        if device_id:
            queryset = queryset.filter(device_id=device_id)
        if aggregate_type:
            queryset = queryset.filter(aggregate_type=aggregate_type)

        return queryset


class TemperatureLogViewSet(viewsets.ModelViewSet):
    """ViewSet for TemperatureLog model"""

    queryset = TemperatureLog.objects.select_related('device', 'logged_by', 'restaurant').all()
    serializer_class = TemperatureLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(logged_by=self.request.user)

    @action(detail=False, methods=['get'])
    def today(self, request):
        """Get today's temperature logs for a restaurant"""
        restaurant_id = request.query_params.get('restaurant')
        if not restaurant_id:
            return Response({'error': 'restaurant parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        today = timezone.now().date()
        logs = self.queryset.filter(
            restaurant_id=restaurant_id,
            logged_at__date=today
        )

        serializer = self.get_serializer(logs, many=True)
        return Response(serializer.data)
