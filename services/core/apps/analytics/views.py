"""Views for analytics app"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Avg, Min, Max, Count, Sum

from .models import ComplianceReport, InspectionPrediction, MetricSnapshot
from .serializers import (
    ComplianceReportSerializer,
    InspectionPredictionSerializer,
    MetricSnapshotSerializer,
    DashboardDataSerializer,
)
from apps.alerts.models import Alert
from apps.devices.models import Device
from apps.sensors.models import SensorReading


class ComplianceReportViewSet(viewsets.ModelViewSet):
    """ViewSet for ComplianceReport model"""

    queryset = ComplianceReport.objects.select_related('restaurant', 'generated_by').all()
    serializer_class = ComplianceReportSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        return queryset

    @action(detail=False, methods=['post'])
    def generate(self, request):
        """Generate a new compliance report"""
        restaurant_id = request.data.get('restaurant_id')
        report_type = request.data.get('report_type', 'WEEKLY')

        if not restaurant_id:
            return Response(
                {'error': 'restaurant_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate period
        today = timezone.now().date()
        if report_type == 'DAILY':
            period_start = today - timedelta(days=1)
            period_end = today
        elif report_type == 'WEEKLY':
            period_start = today - timedelta(days=7)
            period_end = today
        elif report_type == 'MONTHLY':
            period_start = today - timedelta(days=30)
            period_end = today
        else:
            period_start = today - timedelta(days=30)
            period_end = today

        # Create report
        report = ComplianceReport.objects.create(
            restaurant_id=restaurant_id,
            report_type=report_type,
            period_start=period_start,
            period_end=period_end,
            generated_by=request.user
        )

        # Trigger async report generation
        from .tasks import generate_compliance_report
        generate_compliance_report.delay(report.id)

        serializer = self.get_serializer(report)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class InspectionPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for InspectionPrediction model"""

    queryset = InspectionPrediction.objects.select_related('restaurant').all()
    serializer_class = InspectionPredictionSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        return queryset


class MetricSnapshotViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for MetricSnapshot model"""

    queryset = MetricSnapshot.objects.select_related('restaurant').all()
    serializer_class = MetricSnapshotSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')
        start_date = self.request.query_params.get('start')
        end_date = self.request.query_params.get('end')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)

        return queryset


class AnalyticsViewSet(viewsets.GenericViewSet):
    """Analytics endpoint for custom queries"""

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Get aggregated dashboard data for all user's restaurants"""
        user = request.user
        restaurants = user.restaurants.filter(status='ACTIVE')

        dashboard_data = []

        for restaurant in restaurants:
            # Get active devices
            active_devices = Device.objects.filter(
                restaurant=restaurant,
                status='ACTIVE'
            ).count()

            # Get offline devices
            threshold = timezone.now() - timedelta(hours=1)
            offline_devices = Device.objects.filter(
                restaurant=restaurant,
                last_seen__lt=threshold
            ).count()

            # Get alert counts
            active_alerts = Alert.objects.filter(
                restaurant=restaurant,
                status='ACTIVE'
            ).count()

            critical_alerts = Alert.objects.filter(
                restaurant=restaurant,
                status='ACTIVE',
                severity='CRITICAL'
            ).count()

            # Get latest temperature reading
            latest_reading = SensorReading.objects.filter(
                device__restaurant=restaurant
            ).order_by('-timestamp').first()

            dashboard_data.append({
                'restaurant_id': restaurant.id,
                'restaurant_name': restaurant.name,
                'compliance_score': float(restaurant.compliance_score) if restaurant.compliance_score else 0,
                'active_alerts': active_alerts,
                'critical_alerts': critical_alerts,
                'active_devices': active_devices,
                'offline_devices': offline_devices,
                'avg_temperature': float(latest_reading.temperature) if latest_reading and latest_reading.temperature else None,
                'last_reading_time': latest_reading.timestamp if latest_reading else None,
            })

        serializer = DashboardDataSerializer(dashboard_data, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def trends(self, request):
        """Get trends data for a restaurant"""
        restaurant_id = request.query_params.get('restaurant')
        days = int(request.query_params.get('days', 30))

        if not restaurant_id:
            return Response(
                {'error': 'restaurant parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        start_date = timezone.now().date() - timedelta(days=days)
        snapshots = MetricSnapshot.objects.filter(
            restaurant_id=restaurant_id,
            date__gte=start_date
        ).order_by('date')

        serializer = MetricSnapshotSerializer(snapsshots, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def comparison(self, request):
        """Compare restaurants within an organization"""
        org_id = request.query_params.get('organization')

        if not org_id:
            return Response(
                {'error': 'organization parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        from apps.restaurants.models import Restaurant

        restaurants = Restaurant.objects.filter(organization_id=org_id)

        comparison = []
        for restaurant in restaurants:
            comparison.append({
                'restaurant_id': restaurant.id,
                'restaurant_name': restaurant.name,
                'compliance_score': float(restaurant.compliance_score) if restaurant.compliance_score else 0,
                'active_devices': Device.objects.filter(restaurant=restaurant, status='ACTIVE').count(),
                'alerts_last_30d': Alert.objects.filter(
                    restaurant=restaurant,
                    created_at__gte=timezone.now() - timedelta(days=30)
                ).count(),
            })

        # Sort by compliance score
        comparison.sort(key=lambda x: x['compliance_score'], reverse=True)

        return Response(comparison)
