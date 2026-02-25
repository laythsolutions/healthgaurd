"""Serializers for analytics app"""

from rest_framework import serializers
from .models import ComplianceReport, InspectionPrediction, MetricSnapshot


class ComplianceReportSerializer(serializers.ModelSerializer):
    """Serializer for ComplianceReport model"""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)

    class Meta:
        model = ComplianceReport
        fields = [
            'id', 'restaurant', 'restaurant_name', 'report_type', 'status',
            'period_start', 'period_end', 'compliance_score', 'total_readings',
            'violation_count', 'critical_alert_count', 'report_url', 'generated_by',
            'generated_by_name', 'created_at', 'completed_at'
        ]
        read_only_fields = ['created_at', 'completed_at']


class InspectionPredictionSerializer(serializers.ModelSerializer):
    """Serializer for InspectionPrediction model"""

    class Meta:
        model = InspectionPrediction
        fields = [
            'id', 'restaurant', 'predicted_inspection_date', 'predicted_score',
            'confidence', 'risk_factors', 'recommendations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class MetricSnapshotSerializer(serializers.ModelSerializer):
    """Serializer for MetricSnapshot model"""

    class Meta:
        model = MetricSnapshot
        fields = [
            'id', 'restaurant', 'date', 'active_devices', 'offline_devices',
            'low_battery_devices', 'total_readings', 'avg_temperature',
            'min_temperature', 'max_temperature', 'total_alerts',
            'critical_alerts', 'warning_alerts', 'compliance_score',
            'violations_resolved', 'violations_active', 'manual_logs', 'created_at'
        ]
        read_only_fields = ['created_at']


class DashboardDataSerializer(serializers.Serializer):
    """Aggregated dashboard data serializer"""

    restaurant_id = serializers.IntegerField()
    restaurant_name = serializers.CharField()
    compliance_score = serializers.FloatField()
    active_alerts = serializers.IntegerField()
    critical_alerts = serializers.IntegerField()
    active_devices = serializers.IntegerField()
    offline_devices = serializers.IntegerField()
    avg_temperature = serializers.FloatField(allow_null=True)
    last_reading_time = serializers.DateTimeField(allow_null=True)
