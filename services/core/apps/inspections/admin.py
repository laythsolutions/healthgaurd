from django.contrib import admin
from .models import Inspection, InspectionViolation


class InspectionViolationInline(admin.TabularInline):
    model = InspectionViolation
    extra = 0
    fields = ["severity", "code", "description", "violation_status", "points_deducted"]


@admin.register(Inspection)
class InspectionAdmin(admin.ModelAdmin):
    list_display = ["restaurant", "inspection_type", "inspected_at", "grade", "score", "closed", "source_jurisdiction"]
    list_filter = ["grade", "inspection_type", "closed", "source_jurisdiction"]
    search_fields = ["restaurant__name", "external_id"]
    readonly_fields = ["created_at", "updated_at", "raw_data"]
    inlines = [InspectionViolationInline]
