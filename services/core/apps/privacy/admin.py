from django.contrib import admin
from .models import DataSubject, ConsentRecord, DataProcessingAuditLog


@admin.register(DataSubject)
class DataSubjectAdmin(admin.ModelAdmin):
    list_display = ["subject_hash_short", "source_system", "age_range", "zip3", "created_at"]
    list_filter = ["source_system"]
    search_fields = ["subject_hash"]
    readonly_fields = ["subject_hash", "created_at"]

    def subject_hash_short(self, obj):
        return obj.subject_hash[:12] + "…"
    subject_hash_short.short_description = "Subject Hash"


@admin.register(ConsentRecord)
class ConsentRecordAdmin(admin.ModelAdmin):
    list_display = ["subject", "scope", "status", "legal_basis", "created_at"]
    list_filter = ["scope", "status"]
    readonly_fields = ["subject", "scope", "status", "legal_basis", "ip_hash",
                       "user_agent_hash", "recorded_by_user", "recorded_by_system", "created_at"]

    def has_change_permission(self, request, obj=None):
        return False  # Consent records are immutable

    def has_delete_permission(self, request, obj=None):
        return False  # Consent records are immutable


@admin.register(DataProcessingAuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ["action", "record_type", "record_id", "purpose", "performed_by_system", "created_at"]
    list_filter = ["action", "record_type"]
    readonly_fields = list(
        f.name for f in DataProcessingAuditLog._meta.get_fields()
        if hasattr(f, "name")
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
