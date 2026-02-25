"""Device models for IoT sensors"""

from django.db import models
from apps.restaurants.models import Restaurant, Location


class Device(models.Model):
    """IoT device (sensor) registered in the system"""

    class DeviceType(models.TextChoices):
        TEMPERATURE_SENSOR = 'TEMP', 'Temperature Sensor'
        HUMIDITY_SENSOR = 'HUMIDITY', 'Humidity Sensor'
        DOOR_SENSOR = 'DOOR', 'Door Sensor'
        SMART_PLUG = 'PLUG', 'Smart Plug'
        MOTION_SENSOR = 'MOTION', 'Motion Sensor'
        FRYER_OIL_SENSOR = 'FRYER_OIL', 'Fryer Oil Quality Sensor'
        WATER_LEAK_SENSOR = 'WATER_LEAK', 'Water Leak Sensor'

    class DeviceStatus(models.TextChoices):
        ACTIVE = 'ACTIVE', 'Active'
        INACTIVE = 'INACTIVE', 'Inactive'
        LOW_BATTERY = 'LOW_BATTERY', 'Low Battery'
        OFFLINE = 'OFFLINE', 'Offline'
        MAINTENANCE = 'MAINTENANCE', 'Maintenance'

    # Basic info
    device_id = models.CharField(max_length=100, unique=True)  # Zigbee/MQTT device ID
    name = models.CharField(max_length=255)
    device_type = models.CharField(max_length=20, choices=DeviceType.choices)
    status = models.CharField(max_length=20, choices=DeviceStatus.choices, default=DeviceStatus.ACTIVE)

    # Relationships
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='devices')
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True, related_name='devices')

    # Hardware info
    manufacturer = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)
    firmware_version = models.CharField(max_length=50, blank=True)
    zigbee_ieee_address = models.CharField(max_length=50, unique=True, blank=True, null=True)

    # Configuration
    reporting_interval = models.IntegerField(default=300)  # Seconds between readings
    temp_threshold_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    temp_threshold_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Fryer oil sensor thresholds
    # US FDA/USDA guidance: discard fryer oil when TPM > 25%
    oil_tpm_max_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Fryer oil discard threshold (Total Polar Materials %). Default: 25.0",
    )

    # Door sensor thresholds
    door_max_open_minutes = models.IntegerField(
        null=True, blank=True,
        help_text="Alert if door stays open longer than this many minutes. Default: 4",
    )

    # Battery & Network
    battery_percent = models.IntegerField(null=True, blank=True)
    rssi = models.IntegerField(null=True, blank=True)  # Signal strength
    last_seen = models.DateTimeField(null=True, blank=True)

    # Metadata
    notes = models.TextField(blank=True)
    installed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'devices'
        indexes = [
            models.Index(fields=['device_id']),
            models.Index(fields=['restaurant', 'status']),
            models.Index(fields=['location']),
        ]

    def __str__(self):
        return f"{self.name} ({self.device_id})"


class DeviceCalibration(models.Model):
    """Device calibration records"""

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='calibrations')
    calibrated_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    # Calibration data
    actual_temp = models.DecimalField(max_digits=5, decimal_places=2)
    sensor_temp = models.DecimalField(max_digits=5, decimal_places=2)
    offset = models.DecimalField(max_digits=5, decimal_places=2)  # Difference

    notes = models.TextField(blank=True)
    calibrated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device_calibrations'
        ordering = ['-calibrated_at']

    def __str__(self):
        return f"{self.device.name} - {self.calibrated_at}"


class DeviceMaintenance(models.Model):
    """Device maintenance logs"""

    class MaintenanceType(models.TextChoices):
        BATTERY_REPLACE = 'BATTERY', 'Battery Replacement'
        RELOCATION = 'RELOCATE', 'Relocation'
        FIRMWARE_UPDATE = 'FIRMWARE', 'Firmware Update'
        REPAIR = 'REPAIR', 'Repair'
        REPLACEMENT = 'REPLACE', 'Replacement'
        CALIBRATION = 'CALIBRATE', 'Calibration'

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='maintenance_logs')
    maintenance_type = models.CharField(max_length=20, choices=MaintenanceType.choices)
    performed_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)

    description = models.TextField()
    cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    completed_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'device_maintenance'
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.device.name} - {self.maintenance_type}"
