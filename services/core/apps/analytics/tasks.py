"""Celery tasks for analytics"""

from celery import shared_task
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Avg, Count, Q
from .models import ComplianceReport, MetricSnapshot
from apps.alerts.models import Alert
from apps.devices.models import Device
from apps.sensors.models import SensorReading


@shared_task
def generate_compliance_report(report_id):
    """Generate compliance report asynchronously"""
    report = ComplianceReport.objects.get(id=report_id)

    try:
        restaurant = report.restaurant

        # Calculate metrics
        readings = SensorReading.objects.filter(
            device__restaurant=restaurant,
            timestamp__date__range=[report.period_start, report.period_end]
        )

        report.total_readings = readings.count()

        # Calculate violations (readings outside thresholds)
        violations = 0
        for reading in readings:
            if reading.temperature:
                device = reading.device
                if device.temp_threshold_min and reading.temperature < device.temp_threshold_min:
                    violations += 1
                elif device.temp_threshold_max and reading.temperature > device.temp_threshold_max:
                    violations += 1

        report.violation_count = violations

        # Count critical alerts
        report.critical_alert_count = Alert.objects.filter(
            restaurant=restaurant,
            severity='CRITICAL',
            created_at__date__range=[report.period_start, report.period_end]
        ).count()

        # Calculate compliance score (simplified)
        if report.total_readings > 0:
            violation_rate = violations / report.total_readings
            report.compliance_score = max(0, 100 - (violation_rate * 100))
        else:
            report.compliance_score = 0

        report.status = 'COMPLETED'
        report.completed_at = timezone.now()
        report.save()

        # TODO: Generate PDF report and upload to S3

    except Exception as e:
        report.status = 'FAILED'
        report.save()
        raise e


@shared_task
def create_daily_metric_snaphots():
    """Create daily metric snapshots for all restaurants"""
    from apps.restaurants.models import Restaurant

    yesterday = timezone.now().date() - timedelta(days=1)

    for restaurant in Restaurant.objects.filter(status='ACTIVE'):
        # Calculate metrics for yesterday
        snapshot = MetricSnapshot.objects.create(
            restaurant=restaurant,
            date=yesterday
        )

        # Device metrics
        snapshot.active_devices = Device.objects.filter(
            restaurant=restaurant,
            status='ACTIVE'
        ).count()

        # Reading metrics
        readings = SensorReading.objects.filter(
            device__restaurant=restaurant,
            timestamp__date=yesterday
        )

        snapshot.total_readings = readings.count()
        temp_aggs = readings.aggregate(
            avg_temp=Avg('temperature'),
            min_temp=Min('temperature'),
            max_temp=Max('temperature')
        )
        snapshot.avg_temperature = temp_aggs['avg_temp']
        snapshot.min_temperature = temp_aggs['min_temp']
        snapshot.max_temperature = temp_aggs['max_temp']

        # Alert metrics
        alerts = Alert.objects.filter(
            restaurant=restaurant,
            created_at__date=yesterday
        )
        snapshot.total_alerts = alerts.count()
        snapshot.critical_alerts = alerts.filter(severity='CRITICAL').count()
        snapshot.warning_alerts = alerts.filter(severity='WARNING').count()

        # Compliance score
        snapshot.compliance_score = restaurant.compliance_score

        snapshot.save()


@shared_task
def check_offline_devices():
    """Check for offline devices and create alerts"""
    threshold = timezone.now() - timedelta(hours=1)

    offline_devices = Device.objects.filter(
        status='ACTIVE',
        last_seen__lt=threshold
    ).select_related('restaurant')

    for device in offline_devices:
        # Check if alert already exists
        existing_alert = Alert.objects.filter(
            device=device,
            alert_type='DEVICE_OFFLINE',
            status__in=['ACTIVE', 'ACKNOWLEDGED']
        ).first()

        if not existing_alert:
            Alert.objects.create(
                restaurant=device.restaurant,
                device=device,
                alert_type='DEVICE_OFFLINE',
                severity='WARNING',
                title=f'Device Offline: {device.name}',
                message=f'Device {device.name} has not reported data for over 1 hour.',
                status='ACTIVE'
            )


@shared_task
def check_low_battery_devices():
    """Check for low battery devices and create alerts"""
    low_battery_devices = Device.objects.filter(
        status='ACTIVE',
        battery_percent__lt=20
    ).select_related('restaurant')

    for device in low_battery_devices:
        # Check if alert already exists
        existing_alert = Alert.objects.filter(
            device=device,
            alert_type='LOW_BATTERY',
            status__in=['ACTIVE', 'ACKNOWLEDGED']
        ).first()

        if not existing_alert:
            Alert.objects.create(
                restaurant=device.restaurant,
                device=device,
                alert_type='LOW_BATTERY',
                severity='WARNING',
                title=f'Low Battery: {device.name}',
                message=f'Device {device.name} battery is at {device.battery_percent}%.',
                status='ACTIVE'
            )
