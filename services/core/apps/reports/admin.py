"""Admin configuration for reports app"""

from django.contrib import admin
from .models import ComplianceReport, ReportSchedule, ReportTemplate, ReportDeliveryLog


@admin.register(ComplianceReport)
class ComplianceReportAdmin(admin.ModelAdmin):
    """Admin for compliance reports"""

    list_display = ['restaurant', 'report_type', 'status', 'period_start', 'period_end', 'compliance_score', 'created_at']
    list_filter = ['report_type', 'status', 'created_at']
    search_fields = ['restaurant__name']
    readonly_fields = ['report_url', 'file_size_bytes', 'file_pages', 'generated_at', 'created_at', 'updated_at']

    actions = ['regenerate_selected', 'send_selected_emails']

    def regenerate_selected(self, request, queryset):
        """Regenerate selected reports"""
        from .tasks import generate_compliance_report

        for report in queryset:
            report.status = 'PENDING'
            report.save()
            generate_compliance_report.delay(report.id)

        self.message_user(request, f"{queryset.count()} reports queued for regeneration")

    regenerate_selected.short_description = "Regenerate selected reports"

    def send_selected_emails(self, request, queryset):
        """Send selected reports via email"""
        from .tasks import send_report_email

        for report in queryset:
            send_report_email.delay(report.id)

        self.message_user(request, f"{queryset.count()} reports queued for email delivery")

    send_selected_emails.short_description = "Send selected reports via email"


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    """Admin for report schedules"""

    list_display = ['restaurant', 'report_type', 'frequency', 'is_active', 'next_run_at']
    list_filter = ['report_type', 'frequency', 'is_active']
    search_fields = ['restaurant__name']


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin for report templates"""

    list_display = ['organization', 'name', 'template_type', 'is_approved', 'created_at']
    list_filter = ['template_type', 'is_approved', 'created_at']
    search_fields = ['name', 'description']


@admin.register(ReportDeliveryLog)
class ReportDeliveryLogAdmin(admin.ModelAdmin):
    """Admin for report delivery logs"""

    list_display = ['report', 'delivery_method', 'recipient_email', 'sent', 'opened', 'sent_at']
    list_filter = ['delivery_method', 'sent', 'opened']
    search_fields = ['recipient_email']
