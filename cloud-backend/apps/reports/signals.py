"""Signals for reports app"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta

from .models import ComplianceReport, Restaurant


@receiver(post_save, sender=ComplianceReport)
def report_post_save(sender, instance, created, **kwargs):
    """Handle report post-save actions"""
    if created and instance.email_recipients:
        # Queue email delivery if recipients specified
        from .tasks import send_report_email
        send_report_email.delay(instance.id)


@receiver(post_save, sender=Restaurant)
def restaurant_post_save(sender, instance, created, **kwargs):
    """Auto-create default schedules for new restaurants"""
    if created:
        from .models import ReportSchedule

        # Create default weekly schedule
        ReportSchedule.objects.create(
            restaurant=instance,
            report_type=ComplianceReport.ReportType.WEEKLY,
            frequency=ReportSchedule.Frequency.WEEKLY,
            is_active=False,  # Require manual activation
            email_recipients=[]
        )
