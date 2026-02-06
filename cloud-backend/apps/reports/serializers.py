"""Serializers for reports"""

from rest_framework import serializers
from .models import ComplianceReport, ReportSchedule, ReportTemplate


class ComplianceReportSerializer(serializers.ModelSerializer):
    """Serializer for ComplianceReport model"""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)
    generated_by_name = serializers.CharField(source='generated_by.get_full_name', read_only=True)

    class Meta:
        model = ComplianceReport
        fields = [
            'id', 'restaurant', 'restaurant_name', 'report_type', 'status',
            'period_start', 'period_end', 'compliance_score', 'total_readings',
            'violation_count', 'critical_alert_count', 'avg_temperature',
            'report_url', 'file_size_bytes', 'file_pages',
            'email_recipients', 'email_sent', 'email_sent_at',
            'generated_by', 'generated_by_name', 'generated_at',
            'error_message', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'report_url', 'file_size_bytes', 'file_pages',
            'email_sent', 'email_sent_at', 'generated_at', 'updated_at'
        ]


class GenerateReportSerializer(serializers.Serializer):
    """Serializer for generating reports"""
    restaurant_id = serializers.IntegerField()
    report_type = serializers.ChoiceField(choices=ComplianceReport.ReportType.choices)
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    email_recipients = serializers.ListField(child=serializers.EmailField(), required=False)


class ReportScheduleSerializer(serializers.ModelSerializer):
    """Serializer for ReportSchedule model"""
    restaurant_name = serializers.CharField(source='restaurant.name', read_only=True)

    class Meta:
        model = ReportSchedule
        fields = [
            'id', 'restaurant', 'restaurant_name', 'report_type', 'frequency',
            'is_active', 'next_run_at', 'last_run_at', 'email_recipients',
            'include_readings', 'include_alerts', 'include_predictions',
            'include_recommendations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'next_run_at', 'last_run_at', 'created_at', 'updated_at']


class ReportTemplateSerializer(serializers.ModelSerializer):
    """Serializer for ReportTemplate model"""
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    approved_by_name = serializers.CharField(source='approved_by.get_full_name', read_only=True)

    class Meta:
        model = ReportTemplate
        fields = [
            'id', 'organization', 'organization_name', 'name', 'template_type',
            'description', 'template_structure', 'include_sections',
            'custom_logo_url', 'custom_colors', 'is_approved',
            'approved_by', 'approved_by_name', 'approved_at',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'approved_at', 'created_at', 'updated_at']
