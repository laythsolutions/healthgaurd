"""Admin configuration for OTA app"""

from django.contrib import admin
from .models import OTAManifest, GatewayUpdateStatus, GatewayBackup


@admin.register(OTAManifest)
class OTAManifestAdmin(admin.ModelAdmin):
    """Admin for OTA manifests"""

    list_display = ['version', 'status', 'critical', 'release_date', 'success_rate']
    list_filter = ['status', 'critical', 'release_date']
    search_fields = ['version', 'description']
    readonly_fields = ['release_date', 'total_gateways', 'updated_gateways', 'failed_gateways']

    actions = ['mark_as_staged', 'mark_as_completed']

    def mark_as_staged(self, request, queryset):
        queryset.update(status='STAGED')
    mark_as_staged.short_description = "Mark selected as staged"

    def mark_as_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
    mark_as_completed.short_description = "Mark selected as completed"


@admin.register(GatewayUpdateStatus)
class GatewayUpdateStatusAdmin(admin.ModelAdmin):
    """Admin for gateway update status"""

    list_display = ['gateway_id', 'manifest', 'state', 'progress_percentage', 'started_at', 'duration_seconds']
    list_filter = ['state', 'started_at']
    search_fields = ['gateway_id', 'error_message']
    readonly_fields = ['started_at', 'completed_at', 'duration_seconds']


@admin.register(GatewayBackup)
class GatewayBackupAdmin(admin.ModelAdmin):
    """Admin for gateway backups"""

    list_display = ['gateway_id', 'manifest', 'version', 'created_at', 'size_bytes', 'is_cleaned_up']
    list_filter = ['created_at', 'is_cleaned_up']
    search_fields = ['gateway_id']
    readonly_fields = ['created_at']
