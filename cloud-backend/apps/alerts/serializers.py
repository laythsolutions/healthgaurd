"""Serializers for alerts app"""

from rest_framework import serializers
from .models import Alert, AlertRule, NotificationLog


class AlertSerializer(serializers.ModelSerializer):
    """Serializer for Alert model"""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    acknowledged_by_name = serializers.CharField(source='acknowledged_by.get_full_name', read_only=True)
    resolved_by_name = serializers.CharField(source='resolved_by.get_full_name', read_only=True)

    class Meta:
        model = Alert
        fields = [
            'id', 'alert_type', 'severity', 'status', 'restaurant', 'restaurant_name',
            'device', 'device_name', 'title', 'message', 'temperature',
            'threshold_min', 'threshold_max', 'notification_sent', 'notification_sent_at',
            'notification_methods', 'acknowledged_by', 'acknowledged_by_name',
            'acknowledged_at', 'acknowledgement_notes', 'resolved_by', 'resolved_by_name',
            'resolved_at', 'resolution_notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'notification_sent_at']


class AlertCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating alerts (e.g., from MQTT)"""

    class Meta(AlertSerializer.Meta):
        fields = [
            'alert_type', 'severity', 'restaurant', 'device', 'title', 'message',
            'temperature', 'threshold_min', 'threshold_max'
        ]


class AlertRuleSerializer(serializers.ModelSerializer):
    """Serializer for AlertRule model"""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)

    class Meta:
        model = AlertRule
        fields = [
            'id', 'restaurant', 'restaurant_name', 'device', 'device_name',
            'rule_type', 'severity', 'parameters', 'enabled', 'notification_methods',
            'notification_delay_minutes', 'escalation_enabled', 'escalation_delay_minutes',
            'escalation_severity', 'active_all_day', 'active_start_time', 'active_end_time',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for NotificationLog model"""

    class Meta:
        model = NotificationLog
        fields = [
            'id', 'alert', 'notification_type', 'recipient', 'subject', 'message',
            'status', 'sent_at', 'delivered_at', 'error_message', 'external_id', 'created_at'
        ]
        read_only_fields = ['created_at']
