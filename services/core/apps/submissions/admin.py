from django.contrib import admin

from .models import JurisdictionAccount, SubmissionBatch


@admin.register(JurisdictionAccount)
class JurisdictionAccountAdmin(admin.ModelAdmin):
    list_display  = ("name", "fips_code", "state", "jurisdiction_type", "status", "created_at")
    list_filter   = ("status", "jurisdiction_type", "state")
    search_fields = ("name", "fips_code", "contact_email")
    readonly_fields = ("api_key", "approved_by", "approved_at", "created_at")
    fieldsets = (
        ("Jurisdiction", {
            "fields": ("name", "fips_code", "state", "jurisdiction_type", "website"),
        }),
        ("Contact", {
            "fields": ("contact_email",),
        }),
        ("Data Format", {
            "fields": ("score_system", "schema_map"),
        }),
        ("Integration", {
            "fields": ("webhook_url",),
        }),
        ("Workflow", {
            "fields": ("status", "api_key", "approved_by", "approved_at", "created_at"),
        }),
    )


@admin.register(SubmissionBatch)
class SubmissionBatchAdmin(admin.ModelAdmin):
    list_display  = (
        "pk", "jurisdiction", "status", "total_rows",
        "created_count", "skipped_count", "error_count",
        "submitted_at",
    )
    list_filter   = ("status", "source_format")
    search_fields = ("jurisdiction__name", "jurisdiction__fips_code")
    readonly_fields = (
        "jurisdiction", "status", "source_format",
        "total_rows", "created_count", "skipped_count", "error_count",
        "row_errors", "raw_payload",
        "webhook_delivered", "webhook_delivered_at",
        "submitted_at", "completed_at",
    )

    def has_add_permission(self, request):
        return False
