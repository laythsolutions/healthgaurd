"""Celery tasks for alert processing and notification delivery"""

import logging
from datetime import datetime, timedelta
from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from .models import Alert, AlertRule, NotificationLog
from .delivery import dispatcher
from apps.sensors.models import SensorReading
from apps.devices.models import Device

logger = get_task_logger(__name__)


@shared_task
def process_alert_rules():
    """Process all active alert rules and generate alerts if thresholds are violated"""
    from .generators import AlertGenerator

    generator = AlertGenerator()
    rules_processed = 0
    alerts_created = 0

    # Get all enabled rules
    active_rules = AlertRule.objects.filter(enabled=True).select_related('restaurant', 'device')

    for rule in active_rules:
        # Check if rule is currently active (time-based)
        if not _is_rule_active(rule):
            continue

        rules_processed += 1

        # Process rule and potentially create alert
        alert = generator.process_rule(rule)
        if alert:
            alerts_created += 1
            logger.info(f"Alert created: {alert.title} for {alert.restaurant.name}")

    logger.info(f"Processed {rules_processed} rules, created {alerts_created} alerts")
    return {
        'rules_processed': rules_processed,
        'alerts_created': alerts_created
    }


@shared_task
def send_alert_notification(alert_id: int):
    """Send notifications for an alert"""
    try:
        alert = Alert.objects.get(id=alert_id)

        # Don't send if already sent
        if alert.notification_sent:
            logger.info(f"Alert {alert_id} already sent")
            return {'status': 'already_sent'}

        # Determine delivery methods from alert rule
        methods = alert.notification_methods or ['email']

        # Send notifications
        results = dispatcher.send_alert(alert, methods=methods)

        logger.info(f"Alert {alert_id} notifications sent: {results}")
        return {'status': 'sent', 'results': results}

    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return {'status': 'error', 'error': 'Alert not found'}


@shared_task
def send_bulk_notifications(alert_id: int, methods: list, recipients: dict):
    """Send alert notifications to specific recipients"""
    try:
        alert = Alert.objects.get(id=alert_id)
        results = dispatcher.send_alert(alert, methods=methods, recipients=recipients)

        logger.info(f"Bulk notifications sent for alert {alert_id}")
        return {'status': 'sent', 'results': results}

    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return {'status': 'error', 'error': 'Alert not found'}


@shared_task
def escalate_alert(alert_id: int):
    """Escalate alert to higher severity or different recipients"""
    try:
        alert = Alert.objects.get(id=alert_id)

        # Only escalate active alerts
        if alert.status != 'ACTIVE':
            return {'status': 'skipped', 'reason': 'Alert not active'}

        # Check if already escalated
        if alert.severity == 'CRITICAL':
            return {'status': 'skipped', 'reason': 'Already critical'}

        # Escalate severity
        old_severity = alert.severity
        if alert.severity == 'INFO':
            alert.severity = 'WARNING'
        elif alert.severity == 'WARNING':
            alert.severity = 'CRITICAL'

        alert.save(update_fields=['severity'])

        # Send escalation notifications
        escalated_recipients = {
            'email': [],  # Would get from escalation contacts
            'sms': [],
        }

        # Get escalation contacts (e.g., area managers, owners)
        from apps.accounts.models import User, RestaurantAccess

        escalation_access = RestaurantAccess.objects.filter(
            restaurant=alert.restaurant,
            role__in=['OWNER', 'AREA_MANAGER']
        ).select_related('user')

        for access in escalation_access:
            escalated_recipients['email'].append(access.user.email)
            if access.user.phone:
                escalated_recipients['sms'].append(access.user.phone)

        # Send escalation notifications
        results = dispatcher.send_alert(alert, methods=['email', 'sms'], recipients=escalated_recipients)

        logger.info(f"Alert {alert_id} escalated from {old_severity} to {alert.severity}")
        return {
            'status': 'escalated',
            'old_severity': old_severity,
            'new_severity': alert.severity,
            'results': results
        }

    except Alert.DoesNotExist:
        logger.error(f"Alert {alert_id} not found")
        return {'status': 'error', 'error': 'Alert not found'}


@shared_task
def check_escalation_queue():
    """Check for alerts that need to be escalated"""
    # Find alerts that have been active for too long
    from django.db.models import F

    # Get rules with escalation enabled
    escalation_rules = AlertRule.objects.filter(
        enabled=True,
        escalation_enabled=True
    ).select_related('restaurant')

    for rule in escalation_rules:
        # Find active alerts for this rule that are past escalation time
        escalation_threshold = timezone.now() - timedelta(minutes=rule.escalation_delay_minutes)

        active_alerts = Alert.objects.filter(
            restaurant=rule.restaurant,
            status='ACTIVE',
            severity__in=['INFO', 'WARNING'],
            created_at__lte=escalation_threshold
        )

        for alert in active_alerts:
            # Check if this alert matches the rule
            if alert.alert_type == _rule_type_to_alert_type(rule.rule_type):
                escalate_alert.delay(alert.id)


@shared_task
def resolve_auto_resolvable_alerts():
    """Automatically resolve alerts that are no longer valid"""
    resolved_count = 0

    # Find temperature violation alerts
    temp_alerts = Alert.objects.filter(
        alert_type='TEMP_VIOLATION',
        status='ACTIVE'
    ).select_related('device')

    for alert in temp_alerts:
        if not alert.device:
            continue

        # Get latest reading for this device
        latest_reading = SensorReading.objects.filter(
            device=alert.device
        ).order_by('-timestamp').first()

        if not latest_reading:
            continue

        # Check if temperature is now within acceptable range
        temp = float(latest_reading.temperature)

        in_range = True
        if alert.threshold_min and temp < float(alert.threshold_min):
            in_range = False
        if alert.threshold_max and temp > float(alert.threshold_max):
            in_range = False

        if in_range:
            # Auto-resolve the alert
            alert.status = 'RESOLVED'
            alert.resolved_at = timezone.now()
            alert.resolution_notes = 'Automatically resolved - temperature back in range'
            alert.save(update_fields=['status', 'resolved_at', 'resolution_notes'])
            resolved_count += 1

            logger.info(f"Auto-resolved alert {alert.id} - temperature back in range")

    logger.info(f"Auto-resolved {resolved_count} alerts")
    return {'resolved_count': resolved_count}


@shared_task
def cleanup_old_notifications(days_to_keep: int = 90):
    """Clean up old notification logs"""
    cutoff_date = timezone.now() - timedelta(days=days_to_keep)

    deleted_count = NotificationLog.objects.filter(
        created_at__lt=cutoff_date
    ).delete()[0]

    logger.info(f"Cleaned up {deleted_count} old notification logs")
    return {'deleted_count': deleted_count}


@shared_task
def send_alert_summary(restaurant_id: int, recipient_email: str):
    """Send daily/weekly alert summary to restaurant managers"""
    from apps.restaurants.models import Restaurant

    try:
        restaurant = Restaurant.objects.get(id=restaurant_id)

        # Get alerts from last 24 hours
        yesterday = timezone.now() - timedelta(days=1)

        alerts = Alert.objects.filter(
            restaurant=restaurant,
            created_at__gte=yesterday
        ).order_by('-created_at')

        # Build summary
        critical_count = alerts.filter(severity='CRITICAL').count()
        warning_count = alerts.filter(severity='WARNING').count()
        info_count = alerts.filter(severity='INFO').count()
        active_count = alerts.filter(status='ACTIVE').count()

        # Send summary email
        from django.template.loader import render_to_string
        from django.core.mail import EmailMessage
        import sendgrid
        from sendgrid.helpers.mail import Mail, Email, To, Content

        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)

        context = {
            'restaurant': restaurant,
            'alerts': alerts[:20],  # Top 20 alerts
            'critical_count': critical_count,
            'warning_count': warning_count,
            'info_count': info_count,
            'active_count': active_count,
            'summary_date': timezone.now().strftime('%B %d, %Y'),
        }

        html_content = render_to_string('alerts/alert_summary.html', context)

        message = Mail(
            from_email=Email(settings.SENDGRID_FROM_EMAIL, 'HealthGuard Alerts'),
            to_emails=To(recipient_email),
            subject=f"Daily Alert Summary - {restaurant.name}",
            html_content=Content("text/html", html_content)
        )

        response = sg.send(message)

        logger.info(f"Alert summary sent to {recipient_email}")
        return {'status': 'sent', 'recipient': recipient_email}

    except Restaurant.DoesNotExist:
        logger.error(f"Restaurant {restaurant_id} not found")
        return {'status': 'error', 'error': 'Restaurant not found'}


@shared_task
def test_notification_delivery(recipient_email: str, recipient_sms: str = None):
    """Test notification delivery by sending a test alert"""
    from apps.restaurants.models import Restaurant

    # Get first restaurant for testing
    restaurant = Restaurant.objects.first()

    if not restaurant:
        logger.error("No restaurants found for test notification")
        return {'status': 'error', 'error': 'No restaurants found'}

    # Create test alert
    alert = Alert.objects.create(
        restaurant=restaurant,
        alert_type='INFO',
        severity='INFO',
        status='ACTIVE',
        title='TEST ALERT - Notification Delivery Test',
        message='This is a test alert to verify notification delivery is working correctly.',
    )

    # Send notifications
    recipients = {
        'email': [recipient_email],
    }

    if recipient_sms:
        recipients['sms'] = [recipient_sms]

    results = dispatcher.send_alert(alert, methods=['email', 'sms'], recipients=recipients)

    logger.info(f"Test notification sent: {results}")
    return {'status': 'sent', 'alert_id': alert.id, 'results': results}


def _is_rule_active(rule: AlertRule) -> bool:
    """Check if a rule is currently active based on time schedule"""
    if rule.active_all_day:
        return True

    if not rule.active_start_time or not rule.active_end_time:
        return True

    now = timezone.now().time()
    return rule.active_start_time <= now <= rule.active_end_time


def _rule_type_to_alert_type(rule_type: str) -> str:
    """Map rule type to alert type"""
    mapping = {
        'TEMP_THRESHOLD': 'TEMP_VIOLATION',
        'HUMIDITY_THRESHOLD': 'HUMIDITY_VIOLATION',
        'DOOR_DURATION': 'DOOR_OPEN',
        'DEVICE_OFFLINE': 'DEVICE_OFFLINE',
        'BATTERY_LOW': 'LOW_BATTERY',
    }
    return mapping.get(rule_type, 'INFO')
