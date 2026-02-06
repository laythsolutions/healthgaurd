"""API views for reports"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.utils import timezone
from datetime import datetime, timedelta

from .models import ComplianceReport, ReportSchedule, ReportTemplate
from .serializers import (
    ComplianceReportSerializer,
    ReportScheduleSerializer,
    ReportTemplateSerializer,
    GenerateReportSerializer,
)
from .tasks import generate_compliance_report, send_report_email, generate_inspection_prep_report, generate_scorecard


class ComplianceReportViewSet(viewsets.ModelViewSet):
    """ViewSet for compliance reports"""

    queryset = ComplianceReport.objects.select_related('restaurant', 'organization', 'generated_by').all()
    serializer_class = ComplianceReportSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')
        report_type = self.request.query_params.get('report_type')
        status_filter = self.request.query_params.get('status')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if report_type:
            queryset = queryset.filter(report_type=report_type)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new compliance report"""
        serializer = GenerateReportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create report record
        report = ComplianceReport.objects.create(
            restaurant_id=serializer.validated_data['restaurant_id'],
            report_type=serializer.validated_data['report_type'],
            period_start=serializer.validated_data['period_start'],
            period_end=serializer.validated_data['period_end'],
            email_recipients=serializer.validated_data.get('email_recipients', []),
        )

        # Generate report asynchronously
        generate_compliance_report.delay(report.id)

        return Response({
            'report_id': report.id,
            'status': 'generating',
            'message': 'Report generation started'
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def regenerate(self, request, pk=None):
        """Regenerate an existing report"""
        report = self.get_object()

        # Reset status
        report.status = 'PENDING'
        report.save()

        # Regenerate
        generate_compliance_report.delay(report.id)

        return Response({
            'report_id': report.id,
            'status': 'regenerating'
        })

    @action(detail=True, methods=['post'])
    def send_email(self, request, pk=None):
        """Send report via email"""
        report = self.get_object()

        send_report_email.delay(report.id)

        return Response({
            'status': 'sending',
            'recipients': report.email_recipients
        })


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """ViewSet for report schedules"""

    queryset = ReportSchedule.objects.select_related('restaurant').all()
    serializer_class = ReportScheduleSerializer

    @action(detail=True, methods=['post'])
    def trigger_now(self, request, pk=None):
        """Trigger scheduled report immediately"""
        schedule = self.get_object()

        # Create report
        report = ComplianceReport.objects.create(
            restaurant=schedule.restaurant,
            report_type=schedule.report_type,
            period_start=timezone.now().date(),
            period_end=timezone.now().date(),
            email_recipients=schedule.email_recipients,
        )

        # Generate
        generate_compliance_report.delay(report.id)

        return Response({
            'status': 'generating',
            'report_id': report.id
        })


class ReportTemplateViewSet(viewsets.ModelViewSet):
    """ViewSet for report templates"""

    queryset = ReportTemplate.objects.select_related('organization', 'approved_by').all()
    serializer_class = ReportTemplateSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        organization_id = self.request.query_params.get('organization')

        if organization_id:
            queryset = queryset.filter(organization_id=organization_id)

        return queryset.order_by('-created_at')

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a report template"""
        template = self.get_object()

        if template.is_approved:
            return Response({
                'message': 'Template already approved'
            }, status=status.HTTP_400_BAD_REQUEST)

        template.is_approved = True
        template.approved_by = request.user
        template.approved_at = timezone.now()
        template.save()

        return Response({
            'status': 'approved',
            'template_id': template.id
        })

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get report summary statistics"""
        from django.db.models import Count, Q

        total_reports = ComplianceReport.objects.count()
        completed_reports = ComplianceReport.objects.filter(status='COMPLETED').count()
        pending_reports = ComplianceReport.objects.filter(status__in=['PENDING', 'GENERATING']).count()
        failed_reports = ComplianceReport.objects.filter(status='FAILED').count()

        # Report type breakdown
        report_types = ComplianceReport.objects.values('report_type').annotate(
            count=Count('id')
        )

        # Recent reports
        recent = ComplianceReport.objects.select_related('restaurant').order_by('-created_at')[:10]

        return Response({
            'total_reports': total_reports,
            'completed_reports': completed_reports,
            'pending_reports': pending_reports,
            'failed_reports': failed_reports,
            'success_rate': round(completed_reports / total_reports * 100, 1) if total_reports > 0 else 0,
            'report_types': list(report_types),
            'recent_reports': ComplianceReportSerializer(recent, many=True).data
        })
