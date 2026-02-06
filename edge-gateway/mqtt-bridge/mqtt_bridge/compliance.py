"""Compliance engine for local rule checking"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ComplianceEngine:
    """Check compliance rules locally (works offline)"""

    def __init__(self, storage):
        self.storage = storage

    def generate_alert(self, device_id, temperature, min_temp, max_temp, location):
        """Generate a compliance alert"""

        alert = {
            'alert_type': 'TEMP_VIOLATION',
            'severity': 'CRITICAL' if abs(temperature - min_temp) > 10 or abs(temperature - max_temp) > 10 else 'WARNING',
            'timestamp': datetime.utcnow().isoformat(),
            'device_id': device_id,
            'location': location,
            'temperature': temperature,
            'threshold_min': min_temp,
            'threshold_max': max_temp,
            'message': f'Temperature violation at {location}: {temperature}°F (safe range: {min_temp}-{max_temp}°F)'
        }

        logger.warning(f"Generated alert: {alert}")
        return alert

    def check_compliance(self, message):
        """Check if sensor reading is compliant"""
        device_id = message['device_id']
        data = message['data']

        violations = []

        # Temperature check
        if 'temperature' in data:
            config = self.storage.get_device_config(device_id)
            if config:
                min_temp = config.get('temp_min_f')
                max_temp = config.get('temp_max_f')

                if min_temp and max_temp:
                    temp = data['temperature']
                    if temp < min_temp or temp > max_temp:
                        violations.append({
                            'type': 'TEMP_VIOLATION',
                            'value': temp,
                            'min': min_temp,
                            'max': max_temp
                        })

        return violations

    def calculate_compliance_score(self, device_id, hours=24):
        """Calculate compliance score for a device"""
        readings = self.storage.get_recent_readings(device_id, hours=hours)

        if not readings:
            return 100.0  # No data = perfect score (default)

        violations = 0
        for reading in readings:
            if 'temperature' in reading['data']:
                temp = reading['data']['temperature']
                config = self.storage.get_device_config(device_id)

                if config:
                    min_temp = config.get('temp_min_f')
                    max_temp = config.get('temp_max_f')

                    if min_temp and max_temp:
                        if temp < min_temp or temp > max_temp:
                            violations += 1

        # Calculate score
        compliance_rate = (len(readings) - violations) / len(readings) if readings else 1.0
        return compliance_rate * 100
