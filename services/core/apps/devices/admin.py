"""Admin configuration for devices app"""

from django.contrib import admin
from .models import Device, DeviceCalibration, DeviceMaintenance


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Admin for Device model"""

    list_display = ['name', 'device_id', 'device_type', 'restaurant', 'location', 'status', 'battery_percent', 'last_seen']
    list_filter = ['device_type', 'status', 'restaurant__organization']
    search_fields = ['name', 'device_id']
    readonly_fields = ['created_at', 'updated_at', 'last_seen']


@admin.register(DeviceCalibration)
class DeviceCalibrationAdmin(admin.ModelAdmin):
    """Admin for DeviceCalibration model"""

    list_display = ['device', 'actual_temp', 'sensor_temp', 'offset', 'calibrated_at']
    list_filter = ['calibrated_at']
    search_fields = ['device__name']
    readonly_fields = ['calibrated_at']


@admin.register(DeviceMaintenance)
class DeviceMaintenanceAdmin(admin.ModelAdmin):
    """Admin for DeviceMaintenance model"""

    list_display = ['device', 'maintenance_type', 'performed_by', 'completed_at']
    list_filter = ['maintenance_type', 'completed_at']
    search_fields = ['device__name', 'description']
    readonly_fields = ['created_at']
