"""Serializers for devices app"""

from rest_framework import serializers
from .models import Device, DeviceCalibration, DeviceMaintenance


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model"""
    location_name = serializers.CharField(source='location.name', read_only=True)
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = Device
        fields = [
            'id', 'device_id', 'name', 'device_type', 'status',
            'restaurant', 'restaurant_name', 'location', 'location_name',
            'manufacturer', 'model', 'firmware_version', 'zigbee_ieee_address',
            'reporting_interval', 'temp_threshold_min', 'temp_threshold_max',
            'battery_percent', 'rssi', 'last_seen', 'notes',
            'installed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'last_seen']


class DeviceDetailSerializer(DeviceSerializer):
    """Detailed device serializer with recent readings"""
    latest_reading = serializers.SerializerMethodField()
    alert_count_24h = serializers.SerializerMethodField()

    class Meta(DeviceSerializer.Meta):
        fields = DeviceSerializer.Meta.fields + ['latest_reading', 'alert_count_24h']

    def get_latest_reading(self, obj):
        from apps.sensors.models import SensorReading
        latest = SensorReading.objects.filter(device=obj).order_by('-timestamp').first()
        if latest:
            return {
                'temperature': latest.temperature,
                'humidity': latest.humidity,
                'timestamp': latest.timestamp,
            }
        return None

    def get_alert_count_24h(self, obj):
        from apps.alerts.models import Alert
        from django.utils import timezone
        from datetime import timedelta

        last_24h = timezone.now() - timedelta(hours=24)
        return Alert.objects.filter(
            device=obj,
            created_at__gte=last_24h
        ).count()


class DeviceCalibrationSerializer(serializers.ModelSerializer):
    """Serializer for DeviceCalibration model"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    calibrated_by_name = serializers.CharField(source='calibrated_by.get_full_name', read_only=True)

    class Meta:
        model = DeviceCalibration
        fields = [
            'id', 'device', 'device_name', 'calibrated_by', 'calibrated_by_name',
            'actual_temp', 'sensor_temp', 'offset', 'notes', 'calibrated_at'
        ]
        read_only_fields = ['calibrated_at']


class DeviceMaintenanceSerializer(serializers.ModelSerializer):
    """Serializer for DeviceMaintenance model"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)

    class Meta:
        model = DeviceMaintenance
        fields = [
            'id', 'device', 'device_name', 'maintenance_type', 'performed_by',
            'performed_by_name', 'description', 'cost', 'completed_at', 'created_at'
        ]
        read_only_fields = ['created_at']
