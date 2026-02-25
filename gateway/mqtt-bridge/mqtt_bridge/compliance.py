"""Compliance engine for local rule checking (works offline on the gateway)."""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Default thresholds (can be overridden per-device via cloud config)
# ---------------------------------------------------------------------------

_DEFAULT_OIL_TPM_MAX   = 25.0   # % — FDA/USDA guidance; discard fryer oil above this
_DEFAULT_DOOR_MAX_SECS = 240    # 4 minutes — typical refrigeration standard


class ComplianceEngine:
    """Check compliance rules locally (works fully offline)."""

    def __init__(self, storage):
        self.storage = storage
        # door_open_since[device_id] = epoch timestamp when door opened
        self._door_open_since: dict[str, float] = {}

    # -----------------------------------------------------------------------
    # Temperature
    # -----------------------------------------------------------------------

    def generate_alert(self, device_id, temperature, min_temp, max_temp, location):
        """Generate a temperature compliance alert."""
        delta = max(abs(temperature - min_temp), abs(temperature - max_temp))
        severity = 'CRITICAL' if delta > 10 else 'WARNING'

        alert = {
            'alert_type': 'TEMP_VIOLATION',
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'device_id': device_id,
            'location': location,
            'temperature': temperature,
            'threshold_min': min_temp,
            'threshold_max': max_temp,
            'message': (
                f'Temperature violation at {location}: {temperature}°F '
                f'(safe range: {min_temp}–{max_temp}°F)'
            ),
        }
        logger.warning("Generated temp alert: %s", alert)
        return alert

    # -----------------------------------------------------------------------
    # Fryer oil quality
    # -----------------------------------------------------------------------

    def check_fryer_oil(self, device_id: str, tpm_percent: float,
                        oil_temp_f: float | None, config: dict) -> dict | None:
        """
        Check fryer oil Total Polar Materials (TPM) against threshold.

        TPM measures the concentration of degradation compounds in fry oil.
        US guidance (FDA/USDA): discard at ≥25 % TPM.
        Some jurisdictions use 24 % (EU) or 27 %.

        Returns an alert dict if threshold exceeded, else None.
        """
        tpm_max = float(config.get('oil_tpm_max_percent') or _DEFAULT_OIL_TPM_MAX)
        if tpm_percent < tpm_max:
            return None

        location = config.get('location', 'Fryer')
        temp_note = f', oil temp {oil_temp_f}°F' if oil_temp_f else ''
        alert = {
            'alert_type': 'FRYER_OIL',
            'severity': 'CRITICAL',
            'timestamp': datetime.utcnow().isoformat(),
            'device_id': device_id,
            'location': location,
            'oil_tpm_percent': tpm_percent,
            'oil_tpm_threshold': tpm_max,
            'message': (
                f'Fryer oil at {location} requires changing: {tpm_percent:.1f}% TPM '
                f'(discard threshold: {tpm_max}%{temp_note})'
            ),
        }
        logger.warning("Generated fryer oil alert: %s", alert)
        return alert

    # -----------------------------------------------------------------------
    # Door open duration
    # -----------------------------------------------------------------------

    def check_door(self, device_id: str, door_open: bool,
                   config: dict) -> dict | None:
        """
        Track door open duration and alert if it exceeds the threshold.

        The engine maintains a per-device open-since timestamp.  When the door
        closes the timer is cleared.  When it has been open longer than
        door_max_open_minutes, a WARNING (then escalating CRITICAL) alert fires.

        Returns an alert dict if duration exceeded, else None.
        """
        import time
        max_secs = int(
            (config.get('door_max_open_minutes') or _DEFAULT_DOOR_MAX_SECS / 60) * 60
        )
        location = config.get('location', 'Door')

        if not door_open:
            # Door just closed — clear timer
            self._door_open_since.pop(device_id, None)
            return None

        now = time.time()
        if device_id not in self._door_open_since:
            self._door_open_since[device_id] = now
            return None

        open_secs = int(now - self._door_open_since[device_id])
        if open_secs < max_secs:
            return None

        open_mins = open_secs // 60
        severity = 'CRITICAL' if open_secs > max_secs * 2 else 'WARNING'

        alert = {
            'alert_type': 'DOOR_OPEN',
            'severity': severity,
            'timestamp': datetime.utcnow().isoformat(),
            'device_id': device_id,
            'location': location,
            'door_open_seconds': open_secs,
            'threshold_seconds': max_secs,
            'message': (
                f'{location} has been open for {open_mins} minute'
                f'{"s" if open_mins != 1 else ""} '
                f'(threshold: {max_secs // 60} min)'
            ),
        }
        logger.warning("Generated door alert: %s", alert)
        return alert

    # -----------------------------------------------------------------------
    # Water leak
    # -----------------------------------------------------------------------

    def check_water_leak(self, device_id: str, water_detected: bool,
                         config: dict) -> dict | None:
        """
        Any wetness detected → immediate CRITICAL alert.
        Water leaks near electrical equipment or food prep surfaces are
        treated as critical food safety and safety hazards.
        """
        if not water_detected:
            return None

        location = config.get('location', 'Unknown location')
        alert = {
            'alert_type': 'WATER_LEAK',
            'severity': 'CRITICAL',
            'timestamp': datetime.utcnow().isoformat(),
            'device_id': device_id,
            'location': location,
            'message': (
                f'Water leak detected at {location}. '
                f'Inspect immediately — do not use electrical equipment in the area.'
            ),
        }
        logger.warning("Generated water leak alert: %s", alert)
        return alert

    # -----------------------------------------------------------------------
    # Generic compliance check (router)
    # -----------------------------------------------------------------------

    def check_compliance(self, message: dict) -> list[dict]:
        """
        Route a sensor message to the appropriate compliance checks.
        Returns a (possibly empty) list of alert dicts.
        """
        device_id = message['device_id']
        data = message.get('data', {})
        config = self.storage.get_device_config(device_id) or {}

        alerts = []

        # Temperature
        if 'temperature' in data:
            min_temp = config.get('temp_min_f')
            max_temp = config.get('temp_max_f')
            if min_temp is not None and max_temp is not None:
                temp = data['temperature']
                if temp < min_temp or temp > max_temp:
                    alerts.append(self.generate_alert(
                        device_id=device_id,
                        temperature=temp,
                        min_temp=min_temp,
                        max_temp=max_temp,
                        location=config.get('location', 'Unknown'),
                    ))

        # Fryer oil quality
        if 'tpm_percent' in data:
            alert = self.check_fryer_oil(
                device_id=device_id,
                tpm_percent=float(data['tpm_percent']),
                oil_temp_f=data.get('oil_temperature'),
                config=config,
            )
            if alert:
                alerts.append(alert)

        # Door open duration
        if 'contact' in data or 'door_open' in data:
            # Zigbee2MQTT uses `contact` (false = open); normalise to door_open bool
            raw = data.get('contact', data.get('door_open'))
            door_open = not raw if 'contact' in data else bool(raw)
            alert = self.check_door(device_id=device_id, door_open=door_open, config=config)
            if alert:
                alerts.append(alert)

        # Water leak
        if 'water_detected' in data:
            alert = self.check_water_leak(
                device_id=device_id,
                water_detected=bool(data['water_detected']),
                config=config,
            )
            if alert:
                alerts.append(alert)

        return alerts

    # -----------------------------------------------------------------------
    # Legacy single-path entry (kept for backward-compat with main.py)
    # -----------------------------------------------------------------------

    def calculate_compliance_score(self, device_id: str, hours: int = 24) -> float:
        """Calculate compliance score for a device (temperature-based, 0–100)."""
        readings = self.storage.get_recent_readings(device_id, hours=hours)
        if not readings:
            return 100.0

        violations = 0
        config = self.storage.get_device_config(device_id) or {}
        min_temp = config.get('temp_min_f')
        max_temp = config.get('temp_max_f')

        for reading in readings:
            temp = reading.get('data', {}).get('temperature')
            if temp is not None and min_temp is not None and max_temp is not None:
                if temp < min_temp or temp > max_temp:
                    violations += 1

        return (1.0 - violations / len(readings)) * 100
