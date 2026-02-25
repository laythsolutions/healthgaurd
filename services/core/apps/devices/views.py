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
