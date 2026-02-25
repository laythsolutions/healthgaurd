"""Views for devices app"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Device, DeviceCalibration, DeviceMaintenance
from .serializers import (
    DeviceSerializer,
    DeviceDetailSerializer,
    DeviceCalibrationSerializer,
    DeviceMaintenanceSerializer,
)


class DeviceViewSet(viewsets.ModelViewSet):
    """ViewSet for Device model"""

    queryset = Device.objects.select_related('restaurant', 'location').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DeviceDetailSerializer
        return DeviceSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')
        device_type = self.request.query_params.get('device_type')
        status_filter = self.request.query_params.get('status')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if device_type:
            queryset = queryset.filter(device_type=device_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=['post'])
    def calibrate(self, request, pk=None):
        """Add calibration record"""
        device = self.get_object()
        serializer = DeviceCalibrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(device=device, calibrated_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='risk')
    def risk(self, request, pk=None):
        """
        Compute and return the equipment failure risk score for this device.

        GET /api/v1/devices/{id}/risk/?days=14
        """
        device = self.get_object()
        try:
            lookback = int(request.query_params.get('days', 14))
            lookback = max(1, min(lookback, 90))
        except (ValueError, TypeError):
            lookback = 14

        from apps.devices.risk import compute_device_risk
        result = compute_device_risk(device.pk, lookback_days=lookback)
        return Response(result)

    @action(detail=False, methods=['get'], url_path='risk/restaurant/(?P<restaurant_id>[0-9]+)')
    def restaurant_risk(self, request, restaurant_id=None):
        """
        Aggregate risk summary for all devices in a restaurant.

        GET /api/v1/devices/risk/restaurant/{restaurant_id}/
        """
        try:
            rid = int(restaurant_id)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid restaurant_id'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            lookback = int(request.query_params.get('days', 14))
            lookback = max(1, min(lookback, 90))
        except (ValueError, TypeError):
            lookback = 14

        from apps.devices.risk import compute_restaurant_risk_summary
        result = compute_restaurant_risk_summary(rid, lookback_days=lookback)
        return Response(result)

    @action(detail=True, methods=['get'], url_path='health')
    def health(self, request, pk=None):
        """
        Unified health status for a device.

        GET /api/v1/devices/{id}/health/

        Returns battery level, signal strength, online status, last calibration
        offset, and current failure risk score — all in a single call so
        dashboards can render a device health card without multiple round-trips.
        """
        from django.utils import timezone
        from datetime import timedelta
        from apps.devices.risk import compute_device_risk

        device = self.get_object()

        # Online heuristic: last_seen within 3× reporting_interval
        online = False
        minutes_since_seen = None
        if device.last_seen:
            delta = timezone.now() - device.last_seen
            minutes_since_seen = round(delta.total_seconds() / 60, 1)
            threshold_seconds = device.reporting_interval * 3
            online = delta.total_seconds() <= threshold_seconds

        # Most recent calibration record
        last_cal = device.calibrations.order_by('-calibrated_at').first()
        calibration_info = None
        if last_cal:
            cal_age = timezone.now() - last_cal.calibrated_at
            calibration_info = {
                "calibrated_at":     last_cal.calibrated_at.isoformat(),
                "offset":            float(last_cal.offset),
                "days_since":        cal_age.days,
                "needs_calibration": cal_age.days > 90,
            }

        # Failure risk (14-day window)
        risk = compute_device_risk(device.pk, lookback_days=14)

        return Response({
            "device_id":          device.device_id,
            "name":               device.name,
            "status":             device.status,
            "online":             online,
            "last_seen":          device.last_seen.isoformat() if device.last_seen else None,
            "minutes_since_seen": minutes_since_seen,
            "battery_percent":    device.battery_percent,
            "rssi":               device.rssi,
            "firmware_version":   device.firmware_version,
            "calibration":        calibration_info,
            "risk":               risk,
        })

    @action(detail=True, methods=['get'])
    def calibrations(self, request, pk=None):
        """Get calibration history"""
        device = self.get_object()
        calibrations = device.calibrations.all()
        serializer = DeviceCalibrationSerializer(calibrations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def maintenance(self, request, pk=None):
        """Add maintenance record"""
        device = self.get_object()
        serializer = DeviceMaintenanceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(device=device, performed_by=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def maintenance_history(self, request, pk=None):
        """Get maintenance history"""
        device = self.get_object()
        logs = device.maintenance_logs.all()
        serializer = DeviceMaintenanceSerializer(logs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def low_battery(self, request):
        """Get all devices with low battery"""
        devices = self.queryset.filter(
            battery_percent__lt=20,
            status='active'
        )
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def offline(self, request):
        """Get all offline devices"""
        from django.utils import timezone
        from datetime import timedelta

        threshold = timezone.now() - timedelta(hours=1)
        devices = self.queryset.filter(
            last_seen__lt=threshold,
            status='active'
        )
        serializer = DeviceSerializer(devices, many=True)
        return Response(serializer.data)
