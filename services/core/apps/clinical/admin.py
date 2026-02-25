from django.contrib import admin
from .models import ReportingInstitution, ClinicalCase, ClinicalExposure, OutbreakInvestigation


@admin.register(ReportingInstitution)
class ReportingInstitutionAdmin(admin.ModelAdmin):
    list_display = ["name", "institution_type", "jurisdiction", "state", "is_active", "created_at"]
    list_filter = ["institution_type", "is_active"]
    search_fields = ["name", "jurisdiction"]
    readonly_fields = ["api_key_hash", "created_at"]


class ClinicalExposureInline(admin.TabularInline):
    model = ClinicalExposure
    extra = 0
    fields = ["exposure_type", "exposure_date", "geohash", "establishment_type", "confidence", "linked_recall"]


@admin.register(ClinicalCase)
class ClinicalCaseAdmin(admin.ModelAdmin):
    list_display = ["id", "age_range", "geohash", "pathogen", "illness_status", "outcome", "onset_date", "created_at"]
    list_filter = ["illness_status", "outcome", "pathogen"]
    readonly_fields = ["subject_hash", "created_at", "updated_at"]
    inlines = [ClinicalExposureInline]

    def has_change_permission(self, request, obj=None):
        # Cases should only be updated via API to preserve audit trail
        return request.user.is_superuser


@admin.register(OutbreakInvestigation)
class OutbreakInvestigationAdmin(admin.ModelAdmin):
    list_display = ["id", "title", "status", "pathogen", "case_count", "opened_at"]
    list_filter = ["status", "auto_generated"]
    search_fields = ["title", "pathogen"]

    def case_count(self, obj):
        return obj.cases.count()
    case_count.short_description = "Cases"
