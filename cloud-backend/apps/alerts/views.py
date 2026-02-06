"""Views for alerts app"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import Alert, AlertRule, NotificationLog
from .serializers import (
    AlertSerializer,
    AlertCreateSerializer,
    AlertRuleSerializer,
    NotificationLogSerializer,
)
from .delivery import dispatcher
from .tasks import send_alert_notification, test_notification_delivery


class AlertViewSet(viewsets.ModelViewSet):
    """ViewSet for Alert model"""

    queryset = Alert.objects.select_related('restaurant', 'device', 'acknowledged_by', 'resolved_by').all()
    serializer_class = AlertSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')
        severity = self.request.query_params.get('severity')
        status_filter = self.request.query_params.get('status')
        alert_type = self.request.query_params.get('alert_type')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if severity:
            queryset = queryset.filter(severity=severity)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        if alert_type:
            queryset = queryset.filter(alert_type=alert_type)

        return queryset

    @action(detail=True, methods=['post'])
    def acknowledge(self, request, pk=None):
        """Acknowledge an alert"""
        alert = self.get_object()

        if alert.status != 'ACTIVE':
            return Response(
                {'error': 'Only active alerts can be acknowledged'},
                status=status.HTTP_400_BAD_REQUEST
            )

        alert.status = 'ACKNOWLEDGED'
        alert.acknowledged_by = request.user
        alert.acknowledged_at = timezone.now()
        alert.acknowledgement_notes = request.data.get('notes', '')
        alert.save()

        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve an alert"""
        alert = self.get_object()

        alert.status = 'RESOLVED'
        alert.resolved_by = request.user
        alert.resolved_at = timezone.now()
        alert.resolution_notes = request.data.get('notes', '')
        alert.save()

        serializer = self.get_serializer(alert)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def active(self, request):
        """Get all active alerts"""
        alerts = self.queryset.filter(status='ACTIVE')
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def critical(self, request):
        """Get all critical alerts"""
        alerts = self.queryset.filter(
            severity='CRITICAL',
            status__in=['ACTIVE', 'ACKNOWLEDGED']
        )
        serializer = self.get_serializer(alerts, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get alert summary for a restaurant"""
        restaurant_id = request.query_params.get('restaurant')
        if not restaurant_id:
            return Response(
                {'error': 'restaurant parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        alerts = self.queryset.filter(restaurant_id=restaurant_id)

        summary = {
            'active_critical': alerts.filter(status='ACTIVE', severity='CRITICAL').count(),
            'active_warning': alerts.filter(status='ACTIVE', severity='WARNING').count(),
            'unacknowledged': alerts.filter(status='ACTIVE').count(),
            'last_24_hours': alerts.filter(created_at__gte=last_24h).count(),
            'last_7_days': alerts.filter(created_at__gte=last_7d).count(),
            'resolved_today': alerts.filter(
                resolved_at__date=now.date()
            ).count(),
        }

        return Response(summary)

    @action(detail=True, methods=['post'])
    def send_notification(self, request, pk=None):
        """Send notifications for an alert"""
        alert = self.get_object()

        methods = request.data.get('methods', alert.notification_methods or ['email'])
        recipients = request.data.get('recipients', None)

        if recipients:
            # Custom recipients
            from .tasks import send_bulk_notifications
            task = send_bulk_notifications.delay(alert.id, methods, recipients)
            return Response({
                'status': 'queued',
                'task_id': task.id
            })
        else:
            # Default recipients based on preferences
            task = send_alert_notification.delay(alert.id)
            return Response({
                'status': 'queued',
                'task_id': task.id
            })

    @action(detail=False, methods=['post'])
    def test_delivery(self, request):
        """Test notification delivery"""
        recipient_email = request.data.get('email')
        recipient_sms = request.data.get('phone')

        if not recipient_email:
            return Response(
                {'error': 'email parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        task = test_notification_delivery.delay(recipient_email, recipient_sms)
        return Response({
            'status': 'queued',
            'task_id': task.id,
            'message': 'Test notification will be sent shortly'
        })


class AlertRuleViewSet(viewsets.ModelViewSet):
    """ViewSet for AlertRule model"""

    queryset = AlertRule.objects.select_related('restaurant', 'device').all()
    serializer_class = AlertRuleSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)

        return queryset.filter(enabled=True)

    @action(detail=True, methods=['post'])
    def test(self, request, pk=None):
        """Test an alert rule"""
        rule = self.get_object()

        # Create a test alert based on the rule
        test_alert = Alert.objects.create(
            restaurant=rule.restaurant,
            device=rule.device,
            alert_type='TEMP_VIOLATION',  # Default
            severity=rule.severity,
            title=f"TEST: {rule.rule_type}",
            message=f"This is a test alert for rule: {rule.rule_type}",
            status='ACTIVE'
        )

        return Response({
            'message': 'Test alert created',
            'alert_id': test_alert.id
        })


class NotificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for NotificationLog model"""

    queryset = NotificationLog.objects.select_related('alert').all()
    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        alert_id = self.request.query_params.get('alert')
        status_filter = self.request.query_params.get('status')

        if alert_id:
            queryset = queryset.filter(alert_id=alert_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset
