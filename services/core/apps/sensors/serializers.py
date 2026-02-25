"""Serializers for sensors app"""

from rest_framework import serializers
from .models import SensorReading, SensorAggregate, TemperatureLog


class SensorReadingSerializer(serializers.ModelSerializer):
    """Serializer for SensorReading model"""

    class Meta:
        model = SensorReading
        fields = [
            'id', 'device', 'timestamp', 'temperature', 'humidity', 'pressure',
            'door_open', 'power_usage', 'energy_consumed', 'battery_percent',
            'rssi', 'received_at'
        ]
        read_only_fields = ['received_at']


class SensorAggregateSerializer(serializers.ModelSerializer):
    """Serializer for SensorAggregate model"""

    class Meta:
        model = SensorAggregate
        fields = [
            'id', 'device', 'aggregate_type', 'timestamp',
            'temp_avg', 'temp_min', 'temp_max',
            'humidity_avg', 'humidity_min', 'humidity_max',
            'reading_count', 'violations'
        ]


class TemperatureLogSerializer(serializers.ModelSerializer):
    """Serializer for TemperatureLog model"""
    logged_by_name = serializers.CharField(source='logged_by.get_full_name', read_only=True)

    class Meta:
        model = TemperatureLog
        fields = [
            'id', 'device', 'logged_by', 'logged_by_name', 'restaurant',
            'location', 'temperature', 'logged_at', 'food_item',
            'corrective_action', 'in_safe_range', 'created_at'
        ]
        read_only_fields = ['created_at']

    def create(self, validated_data):
        # Check if temperature is in safe range
        device = validated_data.get('device')
        temp = validated_data.get('temperature')

        if device:
            min_temp = device.temp_threshold_min
            max_temp = device.temp_threshold_max

            if min_temp is not None and max_temp is not None:
                validated_data['in_safe_range'] = min_temp <= temp <= max_temp

        return super().create(validated_data)
