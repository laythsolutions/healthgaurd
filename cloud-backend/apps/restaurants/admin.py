"""Admin configuration for restaurants app"""

from django.contrib import admin
from .models import Organization, Restaurant, Location, ComplianceCheck


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin for Organization model"""

    list_display = ['name', 'tier', 'subscription_status', 'monthly_fee', 'compliance_score', 'created_at']
    list_filter = ['tier', 'subscription_status', 'created_at']
    search_fields = ['name', 'email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    """Admin for Restaurant model"""

    list_display = ['name', 'code', 'organization', 'city', 'state', 'status', 'compliance_score', 'gateway_id']
    list_filter = ['status', 'state', 'created_at']
    search_fields = ['name', 'code', 'address']
    readonly_fields = ['created_at', 'updated_at', 'compliance_score']


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    """Admin for Location model"""

    list_display = ['name', 'restaurant', 'location_type', 'temp_min_f', 'temp_max_f']
    list_filter = ['location_type', 'restaurant__organization']
    search_fields = ['name', 'restaurant__name']


@admin.register(ComplianceCheck)
class ComplianceCheckAdmin(admin.ModelAdmin):
    """Admin for ComplianceCheck model"""

    list_display = ['restaurant', 'check_type', 'passed', 'checked_at', 'performed_by']
    list_filter = ['check_type', 'passed', 'checked_at']
    search_fields = ['restaurant__name', 'notes']
    readonly_fields = ['created_at']
    date_hierarchy = 'checked_at'
