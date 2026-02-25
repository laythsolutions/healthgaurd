"""Sensor reading models for time-series data"""

from django.db import models
from apps.devices.models import Device


class SensorReading(models.Model):
    """Individual sensor reading (time-series data - stored in TimescaleDB)"""

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='readings')
    timestamp = models.DateTimeField(db_index=True)

    # Sensor data
    temperature = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    humidity = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    pressure = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    # Door sensor
    door_open = models.BooleanField(null=True, blank=True)
    # Cumulative seconds the door has been open in the current open event.
    # Reset to 0 each time the door closes.  Populated by the MQTT bridge.
    door_open_seconds = models.IntegerField(null=True, blank=True)

    # Smart plug
    power_usage = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    energy_consumed = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Fryer oil quality sensor
    # TPM = Total Polar Materials %; proxy for fry oil degradation.
    # US guidance: discard at ≥25 % (varies by jurisdiction, 24–27 %).
    oil_tpm_percent = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Total Polar Materials percentage (0–100)",
    )
    oil_temperature = models.DecimalField(
        max_digits=6, decimal_places=2, null=True, blank=True,
        help_text="Fryer oil temperature (°F)",
    )

    # Water leak sensor
    water_detected = models.BooleanField(
        null=True, blank=True,
        help_text="True = water detected by the sensor probe",
    )

    # Battery and signal
    battery_percent = models.IntegerField(null=True, blank=True)
    rssi = models.IntegerField(null=True, blank=True)  # Signal strength

    # Metadata
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'sensor_readings'
        indexes = [
            models.Index(fields=['device', '-timestamp']),
            models.Index(fields=['timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.name} at {self.timestamp}"


class SensorAggregate(models.Model):
    """Aggregated sensor data (hourly/daily averages - stored in TimescaleDB)"""

    class AggregateType(models.TextChoices):
        HOURLY = 'HOURLY', 'Hourly'
        DAILY = 'DAILY', 'Daily'
        WEEKLY = 'WEEKLY', 'Weekly'
        MONTHLY = 'MONTHLY', 'Monthly'

    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='aggregates')
    aggregate_type = models.CharField(max_length=20, choices=AggregateType.choices)
    timestamp = models.DateTimeField()

    # Temperature aggregates
    temp_avg = models.DecimalField(max_digits=6, decimal_places=2)
    temp_min = models.DecimalField(max_digits=6, decimal_places=2)
    temp_max = models.DecimalField(max_digits=6, decimal_places=2)

    # Humidity aggregates
    humidity_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity_min = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    humidity_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    # Counts
    reading_count = models.IntegerField()

    # Violations
    violation_count = models.IntegerField(default=0)

    # Fryer oil aggregates (null when device is not a fryer oil sensor)
    oil_tpm_avg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    oil_tpm_max = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    oil_tpm_readings = models.IntegerField(default=0)

    # Door aggregates
    door_open_events = models.IntegerField(
        default=0,
        help_text="Number of distinct open events in this period",
    )
    max_door_open_seconds = models.IntegerField(
        null=True, blank=True,
        help_text="Longest single door-open event duration (seconds)",
    )

    # Water leak aggregates
    water_events = models.IntegerField(
        default=0,
        help_text="Number of wet detections in this period",
    )

    class Meta:
        db_table = 'sensor_aggregates'
        unique_together = ['device', 'aggregate_type', 'timestamp']
        indexes = [
            models.Index(fields=['device', '-timestamp']),
        ]
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.device.name} - {self.aggregate_type} at {self.timestamp}"


class TemperatureLog(models.Model):
    """Manual temperature log entries"""

    device = models.ForeignKey(Device, on_delete=models.SET_NULL, null=True, blank=True)
    logged_by = models.ForeignKey('accounts.User', on_delete=models.SET_NULL, null=True)
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE)

    # Log details
    location = models.CharField(max_length=255)  # e.g., "Walk-in Cooler #1"
    temperature = models.DecimalField(max_digits=6, decimal_places=2)
    logged_at = models.DateTimeField()

    # Food safety info
    food_item = models.CharField(max_length=255, blank=True)
    corrective_action = models.TextField(blank=True)

    # Compliance
    in_safe_range = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'temperature_logs'
        indexes = [
            models.Index(fields=['restaurant', '-logged_at']),
        ]
        ordering = ['-logged_at']

    def __str__(self):
        return f"{self.restaurant.name} - {self.location}: {self.temperature}°F"
