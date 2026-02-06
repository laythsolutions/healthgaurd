"""Alert generation from sensor readings and rule evaluation"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List
from django.utils import timezone
from django.db.models import Q, Avg

from .models import Alert, AlertRule
from apps.sensors.models import SensorReading
from apps.devices.models import Device

logger = logging.getLogger(__name__)


class AlertGenerator:
    """Generate alerts from sensor data based on rules"""

    def __init__(self):
        self.alert_cache = {}  # Cache to avoid duplicate alerts

    def process_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Process a single alert rule and generate alert if conditions are met"""
        try:
            if rule.rule_type == AlertRule.RuleType.TEMPERATURE_THRESHOLD:
                return self._check_temperature_rule(rule)
            elif rule.rule_type == AlertRule.RuleType.HUMIDITY_THRESHOLD:
                return self._check_humidity_rule(rule)
            elif rule.rule_type == AlertRule.RuleType.DOOR_OPEN_DURATION:
                return self._check_door_rule(rule)
            elif rule.rule_type == AlertRule.RuleType.DEVICE_OFFLINE:
                return self._check_device_offline_rule(rule)
            elif rule.rule_type == AlertRule.RuleType.BATTERY_LOW:
                return self._check_battery_rule(rule)
            else:
                logger.warning(f"Unknown rule type: {rule.rule_type}")
                return None

        except Exception as e:
            logger.error(f"Error processing rule {rule.id}: {e}")
            return None

    def _check_temperature_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Check temperature threshold rule"""
        params = rule.parameters
        temp_min = params.get('temp_min')
        temp_max = params.get('temp_max')
        consecutive_violations = params.get('consecutive_violations', 3)

        # Get device(s) to check
        if rule.device:
            devices = [rule.device]
        else:
            # Check all temperature sensors for this restaurant
            devices = Device.objects.filter(
                restaurant=rule.restaurant,
                device_type=Device.DeviceType.TEMPERATURE_SENSOR,
                status='ACTIVE'
            )

        for device in devices:
            # Get recent readings
            recent_readings = SensorReading.objects.filter(
                device=device,
                timestamp__gte=timezone.now() - timedelta(minutes=15)
            ).order_by('-timestamp')[:consecutive_violations]

            if len(recent_readings) < consecutive_violations:
                continue

            # Check if all recent readings violate the threshold
            violation_count = 0
            for reading in recent_readings:
                if reading.temperature is None:
                    continue

                temp = float(reading.temperature)

                if temp_min is not None and temp < temp_min:
                    violation_count += 1
                elif temp_max is not None and temp > temp_max:
                    violation_count += 1

            # Create alert if threshold violated
            if violation_count >= consecutive_violations:
                # Check if alert already exists for this device+violation
                recent_alert = Alert.objects.filter(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.TEMP_VIOLATION,
                    status__in=['ACTIVE', 'ACKNOWLEDGED'],
                    created_at__gte=timezone.now() - timedelta(hours=1)
                ).first()

                if recent_alert:
                    continue

                # Create alert
                latest_temp = recent_readings[0].temperature

                alert = Alert.objects.create(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.TEMP_VIOLATION,
                    severity=rule.severity,
                    title=f"Temperature Violation - {device.name or device.device_id}",
                    message=self._build_temp_message(device, latest_temp, temp_min, temp_max),
                    temperature=latest_temp,
                    threshold_min=temp_min,
                    threshold_max=temp_max,
                    notification_methods=rule.notification_methods,
                )

                logger.info(f"Temperature alert created for device {device.device_id}")
                return alert

        return None

    def _check_humidity_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Check humidity threshold rule"""
        params = rule.parameters
        humidity_min = params.get('humidity_min')
        humidity_max = params.get('humidity_max')

        if rule.device:
            devices = [rule.device]
        else:
            devices = Device.objects.filter(
                restaurant=rule.restaurant,
                device_type=Device.DeviceType.HUMIDITY_SENSOR,
                status='ACTIVE'
            )

        for device in devices:
            # Get latest reading
            latest = SensorReading.objects.filter(
                device=device
            ).order_by('-timestamp').first()

            if not latest or latest.humidity is None:
                continue

            humidity = float(latest.humidity)

            # Check if outside threshold
            if (humidity_min and humidity < humidity_min) or (humidity_max and humidity > humidity_max):
                # Check for recent duplicate alert
                recent_alert = Alert.objects.filter(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.HUMIDITY_VIOLATION,
                    status__in=['ACTIVE', 'ACKNOWLEDGED'],
                    created_at__gte=timezone.now() - timedelta(hours=1)
                ).first()

                if recent_alert:
                    continue

                alert = Alert.objects.create(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.HUMIDITY_VIOLATION,
                    severity=rule.severity,
                    title=f"Humidity Violation - {device.name or device.device_id}",
                    message=f"Humidity level {humidity}% is outside acceptable range ({humidity_min}%-{humidity_max}%).",
                    notification_methods=rule.notification_methods,
                )

                logger.info(f"Humidity alert created for device {device.device_id}")
                return alert

        return None

    def _check_door_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Check door open duration rule"""
        params = rule.parameters
        max_duration_minutes = params.get('max_duration_minutes', 5)

        if rule.device:
            devices = [rule.device]
        else:
            devices = Device.objects.filter(
                restaurant=rule.restaurant,
                device_type=Device.DeviceType.DOOR_SENSOR,
                status='ACTIVE'
            )

        for device in devices:
            # Get readings showing door is open
            threshold_time = timezone.now() - timedelta(minutes=max_duration_minutes)

            open_readings = SensorReading.objects.filter(
                device=device,
                door_open=True,
                timestamp__lte=threshold_time
            ).exists()

            if open_readings:
                # Check for recent duplicate alert
                recent_alert = Alert.objects.filter(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.DOOR_OPEN,
                    status__in=['ACTIVE', 'ACKNOWLEDGED'],
                    created_at__gte=timezone.now() - timedelta(hours=1)
                ).first()

                if recent_alert:
                    continue

                alert = Alert.objects.create(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.DOOR_OPEN,
                    severity=rule.severity,
                    title=f"Door Open Too Long - {device.name or device.device_id}",
                    message=f"Door has been open for more than {max_duration_minutes} minutes. Please close to maintain temperature control.",
                    notification_methods=rule.notification_methods,
                )

                logger.info(f"Door alert created for device {device.device_id}")
                return alert

        return None

    def _check_device_offline_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Check if device has gone offline"""
        params = rule.parameters
        offline_minutes = params.get('offline_minutes', 30)

        threshold_time = timezone.now() - timedelta(minutes=offline_minutes)

        if rule.device:
            devices = [rule.device]
        else:
            devices = Device.objects.filter(
                restaurant=rule.restaurant,
                status='ACTIVE'
            )

        for device in devices:
            # Check if device has no recent readings
            last_reading = SensorReading.objects.filter(
                device=device
            ).order_by('-timestamp').first()

            if not last_reading or last_reading.timestamp < threshold_time:
                # Check for recent duplicate alert
                recent_alert = Alert.objects.filter(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.DEVICE_OFFLINE,
                    status__in=['ACTIVE', 'ACKNOWLEDGED'],
                    created_at__gte=timezone.now() - timedelta(hours=1)
                ).first()

                if recent_alert:
                    continue

                alert = Alert.objects.create(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.DEVICE_OFFLINE,
                    severity=rule.severity,
                    title=f"Device Offline - {device.name or device.device_id}",
                    message=f"Device has not reported data for over {offline_minutes} minutes. Check battery and connectivity.",
                    notification_methods=rule.notification_methods,
                )

                logger.info(f"Offline alert created for device {device.device_id}")
                return alert

        return None

    def _check_battery_rule(self, rule: AlertRule) -> Optional[Alert]:
        """Check low battery rule"""
        params = rule.parameters
        battery_threshold = params.get('battery_threshold', 20)  # 20%

        if rule.device:
            devices = [rule.device]
        else:
            devices = Device.objects.filter(
                restaurant=rule.restaurant,
                status='ACTIVE'
            )

        for device in devices:
            # Check battery level
            if device.battery_level and device.battery_level < battery_threshold:
                # Check for recent duplicate alert
                recent_alert = Alert.objects.filter(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.LOW_BATTERY,
                    status__in=['ACTIVE', 'ACKNOWLEDGED'],
                    created_at__gte=timezone.now() - timedelta(days=1)  # Once per day
                ).first()

                if recent_alert:
                    continue

                alert = Alert.objects.create(
                    restaurant=rule.restaurant,
                    device=device,
                    alert_type=Alert.AlertType.LOW_BATTERY,
                    severity=rule.severity,
                    title=f"Low Battery - {device.name or device.device_id}",
                    message=f"Device battery level is at {device.battery_level}%. Replace battery soon to avoid interruption.",
                    notification_methods=rule.notification_methods,
                )

                logger.info(f"Battery alert created for device {device.device_id}")
                return alert

        return None

    def _build_temp_message(self, device: Device, temp: float,
                           temp_min: float = None, temp_max: float = None) -> str:
        """Build temperature violation message"""
        msg_parts = []

        if temp_min and temp < temp_min:
            msg_parts.append(f"Temperature {temp}°F is below minimum safe threshold of {temp_min}°F.")
            msg_parts.append("Food may be in the danger zone. Take immediate action to increase temperature.")

        if temp_max and temp > temp_max:
            msg_parts.append(f"Temperature {temp}°F exceeds maximum safe threshold of {temp_max}°F.")
            msg_parts.append("Food may be unsafe. Check cooling systems immediately.")

        return ' '.join(msg_parts)


class ManualLogReminderGenerator:
    """Generate reminders for manual temperature logging"""

    def __init__(self):
        pass

    def check_overdue_logs(self) -> List[Alert]:
        """Check for restaurants with overdue manual logs"""
        from apps.restaurants.models import Restaurant
        from apps.analytics.models import MetricSnapshot

        alerts_created = []

        # Get restaurants requiring manual logging
        restaurants = Restaurant.objects.filter(status='ACTIVE')

        for restaurant in restaurants:
            # Check latest manual log entry
            latest_snapshot = MetricSnapshot.objects.filter(
                restaurant=restaurant
            ).order_by('-date').first()

            if not latest_snapshot:
                continue

            # Calculate days since last log
            days_since = (timezone.now().date() - latest_snapshot.date).days

            # If more than 24 hours since last log
            if days_since >= 1:
                # Check for recent reminder
                recent_alert = Alert.objects.filter(
                    restaurant=restaurant,
                    alert_type=Alert.AlertType.MANUAL_LOG_REQUIRED,
                    status__in=['ACTIVE', 'ACKNOWLEDGED'],
                    created_at__gte=timezone.now() - timedelta(hours=12)
                ).exists()

                if not recent_alert:
                    alert = Alert.objects.create(
                        restaurant=restaurant,
                        alert_type=Alert.AlertType.MANUAL_LOG_REQUIRED,
                        severity=Alert.Severity.WARNING,
                        title=f"Manual Temperature Log Required - {restaurant.name}",
                        message=f"Manual temperature logs are overdue. Last log was {days_since} days ago. Please complete logs for all refrigeration, hot holding, and cold holding units.",
                        notification_methods=['email'],
                    )

                    alerts_created.append(alert)
                    logger.info(f"Manual log reminder created for {restaurant.name}")

        return alerts_created
