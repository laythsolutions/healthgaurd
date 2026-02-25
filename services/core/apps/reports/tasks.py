"""Celery tasks for report generation"""

from celery import shared_task
from celery.utils.log import get_task_logger
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.files.storage import default_storage
from django.conf import settings
from django.template.loader import render_to_string

from .models import ComplianceReport, ReportSchedule
from .generators import ComplianceReportGenerator, InspectionPrepReportGenerator, ScorecardReportGenerator
from apps.sensors.models import SensorReading
from apps.alerts.models import Alert
from apps.analytics.models import MetricSnapshot

logger = get_task_logger(__name__)


@shared_task
def generate_compliance_report(report_id: int):
    """Generate a compliance report"""
    try:
        report = ComplianceReport.objects.get(id=report_id)
        report.status = 'GENERATING'
        report.save()

        # Gather data
        restaurant_data = _gather_restaurant_data(report.restaurant)
        inspection_history = _gather_inspection_history(report.restaurant, report.period_start, report.period_end)
        readings_data = _gather_sensor_data(report.restaurant, report.period_start, report.period_end)
        alerts_data = _gather_alerts(report.restaurant, report.period_start, report.period_end)

        # Generate PDF
        generator = ComplianceReportGenerator()
        pdf_bytes = generator.generate_inspection_report(
            restaurant_data=restaurant_data,
            inspection_history=inspection_history,
            readings_data=readings_data,
            alerts_data=alerts_data
        )

        # Save to storage
        filename = f"reports/{report.restaurant.id}/compliance_report_{report.id}.pdf"
        file_path = default_storage.save(filename, pdf_bytes)
        report.report_url = default_storage.url(file_path)
        report.file_size_bytes = len(pdf_bytes)
        report.file_pages = _count_pdf_pages(pdf_bytes)
        report.status = 'COMPLETED'
        report.generated_at = timezone.now()
        report.save()

        logger.info(f"Report {report_id} generated successfully")

        # Send email if recipients specified
        if report.email_recipients:
            send_report_email.delay(report_id)

        return {'status': 'success', 'report_id': report_id}

    except Exception as e:
        logger.error(f"Failed to generate report {report_id}: {e}")

        report.status = 'FAILED'
        report.error_message = str(e)
        report.save()

        return {'status': 'error', 'report_id': report_id, 'error': str(e)}


@shared_task
def generate_inspection_prep_report(restaurant_id: int, prediction_data: dict):
    """Generate inspection preparation report"""
    try:
        from apps.restaurants.models import Restaurant

        restaurant = Restaurant.objects.get(id=restaurant_id)

        # Gather data
        restaurant_data = {
            'name': restaurant.name,
            'address': restaurant.address,
            'city': restaurant.city,
            'state': restaurant.state,
        }

        risk_factors = prediction_data.get('risk_factors', [])
        checklist_items = _generate_inspection_checklist(restaurant)

        # Generate report
        generator = InspectionPrepReportGenerator()
        pdf_bytes = generator.generate_prep_report(
            restaurant_data=restaurant_data,
            inspection_prediction=prediction_data,
            risk_factors=risk_factors,
            checklist_items=checklist_items
        )

        # Save report
        filename = f"reports/{restaurant_id}/inspection_prep_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        file_path = default_storage.save(filename, pdf_bytes)

        logger.info(f"Inspection prep report generated for {restaurant.name}")

        return {
            'status': 'success',
            'url': default_storage.url(file_path),
            'filename': filename
        }

    except Exception as e:
        logger.error(f"Failed to generate inspection prep report: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def generate_scorecard(restaurant_id: int):
    """Generate simple one-page scorecard"""
    try:
        from apps.restaurants.models import Restaurant

        restaurant = Restaurant.objects.get(id=restaurant_id)

        # Get latest metrics
        latest_snapshot = MetricSnapshot.objects.filter(
            restaurant=restaurant
        ).order_by('-date').first()

        restaurant_data = {
            'name': restaurant.name,
            'compliance_score': restaurant.compliance_score or 0,
        }

        metrics = {
            'temp_monitoring': 100,  # Calculate from actual data
            'manual_logs': latest_snapshot.manual_logs if latest_snapshot else 0,
            'alert_response_time': 3.2,  # Calculate from actual data
            'sensor_uptime': 98.5,  # Calculate from actual data
            'training_complete': 100,  # Calculate from actual data
        }

        # Generate scorecard
        generator = ScorecardReportGenerator()
        pdf_bytes = generator.generate_scorecard(restaurant_data, metrics)

        # Save
        filename = f"reports/{restaurant_id}/scorecard_{datetime.now().strftime('%Y%m%d')}.pdf"
        file_path = default_storage.save(filename, pdf_bytes)

        return {
            'status': 'success',
            'url': default_storage.url(file_path)
        }

    except Exception as e:
        logger.error(f"Failed to generate scorecard: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def send_report_email(report_id: int):
    """Send report via email"""
    try:
        report = ComplianceReport.objects.get(id=report_id)

        if not report.email_recipients:
            logger.info(f"No email recipients for report {report_id}")
            return

        # Build email content
        subject = f"Compliance Report: {report.restaurant.name} ({report.report_type})"
        message = render_to_string('reports_email.html', {
            'report': report,
            'restaurant': report.restaurant,
        })

        # Attach PDF
        from django.core.mail import EmailMessage
        from django.core.files.base import ContentFile

        email = EmailMessage(
            subject=subject,
            body=message,
            to=report.email_recipients,
        )

        # Attach PDF file
        if report.report_url:
            # Download PDF from storage
            import requests
            response = requests.get(report.report_url)
            pdf_content = ContentFile(response.content)

            email.attach(f"compliance_report_{report.id}.pdf", pdf_content.read(), 'application/pdf')

        email.send()

        # Update log
        report.email_sent = True
        report.email_sent_at = timezone.now()
        report.save()

        logger.info(f"Report {report_id} email sent successfully")

        return {'status': 'success'}

    except Exception as e:
        logger.error(f"Failed to send report email: {e}")
        return {'status': 'error', 'error': str(e)}


@shared_task
def process_scheduled_reports():
    """Process all due scheduled reports"""
    from apps.restaurants.models import Restaurant

    # Find due schedules
    now = timezone.now()
    due_schedules = ReportSchedule.objects.filter(
        is_active=True,
        next_run_at__lte=now
    ).select_related('restaurant')

    logger.info(f"Processing {due_schedules.count()} scheduled reports")

    for schedule in due_schedules:
        # Determine period
        period_end = timezone.now().date()
        period_start = _calculate_period_start(schedule.frequency, period_end)

        # Create report record
        report = ComplianceReport.objects.create(
            restaurant=schedule.restaurant,
            report_type=schedule.report_type,
            period_start=period_start,
            period_end=period_end,
            email_recipients=schedule.email_recipients,
        )

        # Generate report
        generate_compliance_report.delay(report.id)

        # Schedule next run
        schedule.last_run_at = now
        schedule.next_run_at = _calculate_next_run(schedule.frequency)
        schedule.save()

        logger.info(f"Scheduled report generated for {schedule.restaurant.name}")


@shared_task
def generate_all_daily_reports():
    """Generate daily reports for all active restaurants"""
    from apps.restaurants.models import Restaurant

    yesterday = timezone.now().date() - timedelta(days=1)

    for restaurant in Restaurant.objects.filter(status='ACTIVE'):
        # Check if schedule exists
        schedule = restaurant.report_schedules.filter(frequency='DAILY', is_active=True).first()

        if schedule:
            # Create and generate report
            report = ComplianceReport.objects.create(
                restaurant=restaurant,
                report_type=ComplianceReport.ReportType.DAILY,
                period_start=yesterday,
                period_end=yesterday,
                email_recipients=schedule.email_recipients,
            )

            generate_compliance_report.delay(report.id)


def _gather_restaurant_data(restaurant) -> dict:
    """Gather restaurant data for report"""
    from django.db.models import Avg, Count, Q

    # Active devices
    from apps.devices.models import Device
    active_devices = Device.objects.filter(restaurant=restaurant, status='ACTIVE').count()

    # Alerts in last 90 days
    ninety_days_ago = timezone.now() - timedelta(days=90)
    critical_alerts = Alert.objects.filter(
        restaurant=restaurant,
        severity='CRITICAL',
        created_at__gte=ninety_days_ago
    ).count()

    # Latest inspection
    latest_inspection = restaurant.public_inspections.order_by('-inspection_date').first()

    return {
        'name': restaurant.name,
        'address': restaurant.address,
        'city': restaurant.city,
        'state': restaurant.state,
        'compliance_score': restaurant.compliance_score or 0,
        'active_devices': active_devices,
        'critical_alerts': critical_alerts,
        'latest_inspection': latest_inspection.inspection_date if latest_inspection else None,
        'alerts': [],  # Would fetch actual alerts
    }


def _gather_inspection_history(restaurant, start_date, end_date):
    """Gather inspection history for period"""
    # Get from public inspection data
    inspections = restaurant.public_inspections.filter(
        inspection_date__date__range=(start_date, end_date)
    ).order_by('-inspection_date')

    return [
        {
            'inspection_date': insp.inspection_date,
            'score': insp.inspection_score,
            'grade': insp.inspection_grade,
            'violations': insp.violations_data,
        }
        for insp in inspections
    ]


def _gather_sensor_data(restaurant, start_date, end_date):
    """Gather sensor readings for period"""
    readings = SensorReading.objects.filter(
        device__restaurant=restaurant,
        timestamp__date__range=(start_date, end_date)
    ).select_related('device').order_by('-timestamp')[:10000]  # Limit to 10k

    return [
        {
            'device_id': reading.device.device_id,
            'temperature': reading.temperature,
            'humidity': reading.humidity,
            'timestamp': reading.timestamp,
        }
        for reading in readings
    ]


def _gather_alerts(restaurant, start_date, end_date):
    """Gather alerts for period"""
    alerts = Alert.objects.filter(
        restaurant=restaurant,
        created_at__date__range=(start_date, end_date)
    ).order_by('-created_at')

    return [
        {
            'severity': alert.severity,
            'title': alert.title,
            'message': alert.message,
            'created_at': alert.created_at,
        }
        for alert in alerts
    ]


def _generate_inspection_checklist(restaurant) -> list:
    """Generate inspection checklist items"""
    return [
        {
            'category': 'Temperature Control',
            'task': 'All refrigeration units maintaining proper temperatures (≤41°F)',
        },
        {
            'category': 'Temperature Control',
            'task': 'Hot holding units maintaining proper temperatures (≥135°F)',
        },
        {
            'category': 'Temperature Control',
            'task': 'Cold holding units maintaining proper temperatures (≤41°F)',
        },
        {
            'category': 'Temperature Control',
            'task': 'Freezer units maintaining proper temperatures (≤0°F)',
        },
        {
            'category': 'Documentation',
            'task': 'Temperature logs completed for all units (last 30 days)',
        },
        {
            'category': 'Documentation',
            'task': 'Manager food safety certification valid and current',
        },
        {
            'category': 'Documentation',
            'task': 'Employee health records maintained and accessible',
        },
        {
            'category': 'Facility',
            'task': 'All lighting fixtures functioning properly',
        },
        {
            'category': 'Facility',
            'task': 'Ventilation system working correctly',
        },
        {
            'category': 'Facility',
            'task': 'No signs of pest activity (traps, droppings)',
        },
        {
            'category': 'Sanitation',
            'task': 'All surfaces clean and sanitized',
        },
        {
            'category': 'Sanitation',
            'task': 'Sanitizer buckets properly labeled and at correct concentration',
        },
        {
            'category': 'Food Storage',
            'task': 'All food properly stored (off floor, covered, labeled)',
        },
        {
            'category': 'Food Storage',
            'task': 'No cross-contamination risks (raw meat separate)',
        },
        {
            'category': 'Food Storage',
            'task': 'First-in, first-out (FIFO) system being followed',
        },
        {
            'category': 'Staff Practices',
            'task': 'All staff wearing proper hair restraints and gloves',
        },
        {
            'category': 'Staff Practices',
            'task': 'No staff working while ill',
        },
        {
            'category': 'Equipment',
            'task': 'All thermometers calibrated and accurate',
        },
        {
            'category': 'Equipment',
            'task': 'Dishwasher reaching proper sanitization temperature (≥160°F)',
        },
    ]


def _calculate_period_start(frequency: str, end_date: datetime.date) -> datetime.date:
    """Calculate period start date based on frequency"""
    if frequency == 'DAILY':
        return end_date - timedelta(days=1)
    elif frequency == 'WEEKLY':
        return end_date - timedelta(weeks=1)
    elif frequency == 'BI_WEEKLY':
        return end_date - timedelta(weeks=2)
    elif frequency == 'MONTHLY':
        return end_date - timedelta(days=30)
    elif frequency == 'QUARTERLY':
        return end_date - timedelta(days=90)
    else:
        return end_date - timedelta(days=7)


def _calculate_next_run(frequency: str) -> datetime:
    """Calculate next run time based on frequency"""
    now = timezone.now()

    if frequency == 'DAILY':
        return now + timedelta(days=1)
    elif frequency == 'WEEKLY':
        return now + timedelta(weeks=1)
    elif frequency == 'BI_WEEKLY':
        return now + timedelta(weeks=2)
    elif frequency == 'MONTHLY':
        return now + timedelta(days=30)
    elif frequency == 'QUARTERLY':
        return now + timedelta(days=90)
    else:
        return now + timedelta(days=7)


def _count_pdf_pages(pdf_bytes: bytes) -> int:
    """Count pages in PDF"""
    from io import BytesIO
    from PyPDF2 import PdfReader

    pdf_file = BytesIO(pdf_bytes)
    reader = PdfReader(pdf_file)
    return len(reader.pages)
