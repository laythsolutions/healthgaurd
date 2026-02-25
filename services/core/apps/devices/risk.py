"""
IoT equipment failure risk scoring engine.

Computes a failure_risk_score (0–100) per device using the last N days of
sensor aggregate data. Higher scores indicate higher likelihood of impending
equipment failure or compliance risk.

Risk signals
------------
1. temperature_variance     — High daily std-dev on temp_avg → struggling to
                              hold set-point (compressor wear, seal failure).
2. warming_trend            — Positive linear slope on temp_avg for cold-storage
                              devices → losing cooling capacity over time.
3. breach_rate              — Fraction of daily aggregates with violation_count > 0
                              → recurring exceedances stress equipment further.
4. gap_penalty              — Missing expected daily aggregates → device going
                              offline intermittently (connectivity or power issues).
5. battery_decline          — If the latest battery_percent is low or the device
                              status is LOW_BATTERY.
6. signal_degradation       — RSSI getting consistently worse over the window.

Score formula
-------------
    raw = Σ(signal_score × weight)  for each signal
    failure_risk_score = clamp(raw, 0, 100)

Risk levels
-----------
    critical : score ≥ 75
    high     : 50 ≤ score < 75
    medium   : 25 ≤ score < 50
    low      : score < 25
"""

import logging
import math
from datetime import date, timedelta
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Signal weights (must sum to 100)
# ---------------------------------------------------------------------------
_WEIGHTS = {
    "temperature_variance": 30,
    "warming_trend":        25,
    "breach_rate":          20,
    "gap_penalty":          15,
    "battery":              6,
    "signal_degradation":   4,
}

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _linear_slope(values: list[float]) -> float:
    """Return the slope of a linear fit through the values (index as x)."""
    n = len(values)
    if n < 2:
        return 0.0
    x_mean = (n - 1) / 2
    y_mean = sum(values) / n
    numerator   = sum((i - x_mean) * (v - y_mean) for i, v in enumerate(values))
    denominator = sum((i - x_mean) ** 2 for i in range(n))
    return numerator / denominator if denominator else 0.0


def _std_dev(values: list[float]) -> float:
    if len(values) < 2:
        return 0.0
    mean = sum(values) / len(values)
    variance = sum((v - mean) ** 2 for v in values) / len(values)
    return math.sqrt(variance)


def _clamp(val: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, val))


# ---------------------------------------------------------------------------
# Individual signal scorers (each returns 0–100)
# ---------------------------------------------------------------------------

def _score_temperature_variance(temp_avgs: list[float], device_type: str) -> tuple[float, str]:
    """
    Standard deviation of daily average temps over the window.
    Thresholds differ by device type: refrigerators should be ±1 °F; freezers ±0.5 °F.
    """
    if not temp_avgs:
        return 0.0, "no_data"
    std = _std_dev(temp_avgs)
    # Acceptable std: ≤ 1.5°F for cold-storage; ≤ 3°F for hot-holding
    cold_storage = device_type in ("TEMP", "HUMIDITY")
    threshold = 1.5 if cold_storage else 3.0
    if std <= threshold:
        score = 0.0
    elif std <= threshold * 2:
        score = 40.0
    elif std <= threshold * 3:
        score = 70.0
    else:
        score = 100.0
    return _clamp(score), f"std={std:.2f}°F"


def _score_warming_trend(temp_avgs: list[float], is_cold_storage: bool) -> tuple[float, str]:
    """
    For cold-storage devices, a positive slope (warming) is a risk signal.
    For hot-holding, a negative slope (cooling) is a risk signal.
    """
    if len(temp_avgs) < 3:
        return 0.0, "insufficient_data"
    slope = _linear_slope(temp_avgs)
    # For cold-storage: positive slope = warming = risk
    risk_slope = slope if is_cold_storage else -slope
    if risk_slope <= 0:
        return 0.0, f"slope={slope:.3f}°F/day (stable)"
    elif risk_slope < 0.1:
        return 20.0, f"slope={slope:.3f}°F/day (slight warming)"
    elif risk_slope < 0.25:
        return 60.0, f"slope={slope:.3f}°F/day (warming)"
    else:
        return 100.0, f"slope={slope:.3f}°F/day (rapid warming)"


def _score_breach_rate(violation_counts: list[int], reading_counts: list[int]) -> tuple[float, str]:
    total_readings = sum(reading_counts)
    total_breaches = sum(violation_counts)
    if total_readings == 0:
        return 0.0, "no_readings"
    rate = total_breaches / total_readings
    if rate == 0:
        return 0.0, "0% breach rate"
    elif rate < 0.05:
        return 25.0, f"{rate*100:.1f}% breach rate"
    elif rate < 0.15:
        return 60.0, f"{rate*100:.1f}% breach rate"
    else:
        return 100.0, f"{rate*100:.1f}% breach rate"


def _score_gap_penalty(
    actual_days: int, expected_days: int
) -> tuple[float, str]:
    """Penalise missing daily aggregates within the window."""
    if expected_days == 0:
        return 0.0, "no_expectation"
    coverage = actual_days / expected_days
    if coverage >= 0.95:
        return 0.0, f"{coverage*100:.0f}% coverage"
    elif coverage >= 0.80:
        return 30.0, f"{coverage*100:.0f}% coverage"
    elif coverage >= 0.60:
        return 70.0, f"{coverage*100:.0f}% coverage"
    else:
        return 100.0, f"{coverage*100:.0f}% coverage"


def _score_battery(battery_pct: Optional[int], device_status: str) -> tuple[float, str]:
    if device_status == "LOW_BATTERY":
        return 100.0, "status=LOW_BATTERY"
    if battery_pct is None:
        return 0.0, "no_battery_data"
    if battery_pct >= 50:
        return 0.0, f"{battery_pct}%"
    elif battery_pct >= 30:
        return 40.0, f"{battery_pct}%"
    elif battery_pct >= 15:
        return 75.0, f"{battery_pct}%"
    else:
        return 100.0, f"{battery_pct}% (critical)"


def _score_fryer_oil_tpm(
    tpm_values: list[float],
    tpm_max: float = 25.0,
) -> tuple[float, str]:
    """
    Score fryer oil quality from a recent sequence of TPM readings.

    Two sub-signals combined:
      - Proximity: how close the latest reading is to the discard threshold
      - Trend: is TPM rising rapidly (oil degrading faster than expected)?
    """
    if not tpm_values:
        return 0.0, "no_oil_data"

    latest_tpm = tpm_values[-1]

    # Proximity score: proportion of threshold consumed
    proximity_fraction = latest_tpm / tpm_max if tpm_max > 0 else 0.0
    if proximity_fraction >= 1.0:
        proximity_score = 100.0
    elif proximity_fraction >= 0.85:
        proximity_score = 80.0
    elif proximity_fraction >= 0.70:
        proximity_score = 50.0
    elif proximity_fraction >= 0.50:
        proximity_score = 20.0
    else:
        proximity_score = 0.0

    # Trend score: rising TPM slope
    trend_score = 0.0
    if len(tpm_values) >= 3:
        slope = _linear_slope(tpm_values)
        if slope >= 2.0:
            trend_score = 100.0    # Very rapid degradation
        elif slope >= 1.0:
            trend_score = 70.0
        elif slope >= 0.3:
            trend_score = 30.0

    combined = (proximity_score * 0.65) + (trend_score * 0.35)
    return _clamp(combined), (
        f"TPM={latest_tpm:.1f}% (max={tpm_max}%), slope={_linear_slope(tpm_values):.2f}%/day"
        if len(tpm_values) >= 2 else f"TPM={latest_tpm:.1f}%"
    )


def _score_signal(rssi_values: list[int]) -> tuple[float, str]:
    """Average RSSI — lower (more negative) = weaker signal."""
    if not rssi_values:
        return 0.0, "no_data"
    avg_rssi = sum(rssi_values) / len(rssi_values)
    # RSSI: -50 = excellent, -70 = good, -80 = fair, -90 = poor
    if avg_rssi >= -70:
        return 0.0, f"RSSI={avg_rssi:.0f}dBm"
    elif avg_rssi >= -80:
        return 30.0, f"RSSI={avg_rssi:.0f}dBm"
    elif avg_rssi >= -90:
        return 70.0, f"RSSI={avg_rssi:.0f}dBm"
    else:
        return 100.0, f"RSSI={avg_rssi:.0f}dBm (poor)"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def compute_device_risk(device_id: int, lookback_days: int = 14) -> dict:
    """
    Compute failure risk score for a single device.

    Returns:
        {
          "device_id":         int,
          "failure_risk_score": float,   # 0–100
          "risk_level":        str,      # critical/high/medium/low
          "signals": {
            "temperature_variance": {"score": float, "detail": str},
            "warming_trend":        {"score": float, "detail": str},
            "breach_rate":          {"score": float, "detail": str},
            "gap_penalty":          {"score": float, "detail": str},
            "battery":              {"score": float, "detail": str},
            "signal_degradation":   {"score": float, "detail": str},
          },
          "recommendations": [...],
          "computed_at": str,
        }
    """
    from django.utils import timezone
    from apps.devices.models import Device
    from apps.sensors.models import SensorAggregate

    try:
        device = Device.objects.select_related("restaurant", "location").get(pk=device_id)
    except Device.DoesNotExist:
        return {"error": f"Device {device_id} not found"}

    since = date.today() - timedelta(days=lookback_days)
    aggregates = list(
        SensorAggregate.objects
        .filter(device=device, aggregate_type="DAILY", timestamp__date__gte=since)
        .order_by("timestamp")
        .values("timestamp", "temp_avg", "temp_min", "temp_max",
                "reading_count", "violation_count", "humidity_avg")
    )

    violation_counts = [a["violation_count"] or 0 for a in aggregates]
    reading_counts   = [a["reading_count"] or 0 for a in aggregates]

    from apps.sensors.models import SensorReading
    recent_readings = list(
        SensorReading.objects
        .filter(device=device, rssi__isnull=False)
        .order_by("-timestamp")
        .values_list("rssi", flat=True)[:50]
    )
    s_battery, d_battery = _score_battery(device.battery_percent, device.status)
    s_signal,  d_signal  = _score_signal(recent_readings)
    s_gap,     d_gap     = _score_gap_penalty(len(aggregates), lookback_days)

    # ---- Branch by device type -------------------------------------------

    if device.device_type == "FRYER_OIL":
        # Fryer oil: TPM quality + connectivity signals
        tpm_values = list(
            SensorReading.objects
            .filter(device=device, oil_tpm_percent__isnull=False)
            .order_by("timestamp")
            .values_list("oil_tpm_percent", flat=True)
            .filter(timestamp__date__gte=date.today() - timedelta(days=lookback_days))
        )
        tpm_values = [float(v) for v in tpm_values]
        tpm_max = float(device.oil_tpm_max_percent or 25.0)
        s_oil, d_oil = _score_fryer_oil_tpm(tpm_values, tpm_max=tpm_max)

        # Fryer oil weights: oil quality 60%, gap 20%, battery 12%, signal 8%
        raw_score = (
            s_oil     * 60 / 100
            + s_gap     * 20 / 100
            + s_battery * 12 / 100
            + s_signal  * 8  / 100
        )
        failure_risk_score = _clamp(round(raw_score, 1))
        signals = {
            "oil_tpm_quality":  {"score": s_oil,     "detail": d_oil},
            "gap_penalty":      {"score": s_gap,     "detail": d_gap},
            "battery":          {"score": s_battery, "detail": d_battery},
            "signal_degradation": {"score": s_signal, "detail": d_signal},
        }
        recommendations = []
        if s_oil >= 80:
            recommendations.append("Change fryer oil immediately — TPM at or above discard threshold.")
        elif s_oil >= 50:
            recommendations.append("Schedule fryer oil change soon — TPM approaching discard threshold.")
        if s_gap >= 70:
            recommendations.append("Check device connectivity — significant gaps in oil sensor reporting.")
        if s_battery >= 75:
            recommendations.append("Replace battery or check power supply.")

    elif device.device_type == "WATER_LEAK":
        # Water leak: recent events + connectivity
        recent_events = list(
            SensorReading.objects
            .filter(
                device=device,
                water_detected=True,
                timestamp__date__gte=date.today() - timedelta(days=lookback_days),
            )
            .order_by("-timestamp")
            .values_list("timestamp", flat=True)[:10]
        )
        event_count = len(recent_events)
        s_events = _clamp(event_count * 25.0)   # Each event = +25 risk points, max 100

        raw_score = (
            s_events  * 60 / 100
            + s_gap     * 20 / 100
            + s_battery * 12 / 100
            + s_signal  * 8  / 100
        )
        failure_risk_score = _clamp(round(raw_score, 1))
        signals = {
            "leak_events":      {"score": s_events,  "detail": f"{event_count} events in {lookback_days}d"},
            "gap_penalty":      {"score": s_gap,     "detail": d_gap},
            "battery":          {"score": s_battery, "detail": d_battery},
            "signal_degradation": {"score": s_signal, "detail": d_signal},
        }
        recommendations = []
        if event_count > 0:
            recommendations.append(
                f"{event_count} water detection event(s) in the last {lookback_days} days — inspect for persistent leaks."
            )
        if s_battery >= 75:
            recommendations.append("Replace battery or check power supply.")

    else:
        # Default: temperature/humidity/door/plug/motion — original 6-signal model
        temp_avgs = [float(a["temp_avg"]) for a in aggregates if a["temp_avg"] is not None]
        is_cold   = device.device_type in ("TEMP", "HUMIDITY")

        s_variance, d_variance = _score_temperature_variance(temp_avgs, device.device_type)
        s_trend,    d_trend    = _score_warming_trend(temp_avgs, is_cold)
        s_breach,   d_breach   = _score_breach_rate(violation_counts, reading_counts)

        raw_score = (
            s_variance * _WEIGHTS["temperature_variance"] / 100
            + s_trend   * _WEIGHTS["warming_trend"]        / 100
            + s_breach  * _WEIGHTS["breach_rate"]           / 100
            + s_gap     * _WEIGHTS["gap_penalty"]           / 100
            + s_battery * _WEIGHTS["battery"]               / 100
            + s_signal  * _WEIGHTS["signal_degradation"]    / 100
        )
        failure_risk_score = _clamp(round(raw_score, 1))
        signals = {
            "temperature_variance": {"score": s_variance, "detail": d_variance},
            "warming_trend":        {"score": s_trend,    "detail": d_trend},
            "breach_rate":          {"score": s_breach,   "detail": d_breach},
            "gap_penalty":          {"score": s_gap,      "detail": d_gap},
            "battery":              {"score": s_battery,  "detail": d_battery},
            "signal_degradation":   {"score": s_signal,   "detail": d_signal},
        }
        recommendations = []
        if s_variance >= 70:
            recommendations.append("Schedule immediate equipment inspection — temperature instability detected.")
        if s_trend >= 60 and is_cold:
            recommendations.append("Check refrigerant levels and door seals — warming trend in cold storage.")
        if s_breach >= 60:
            recommendations.append("Investigate recurring threshold breaches — equipment may be undersized or failing.")
        if s_gap >= 70:
            recommendations.append("Check device connectivity — significant gaps in sensor reporting.")
        if s_battery >= 75:
            recommendations.append("Replace battery or check power supply.")
        if s_signal >= 70:
            recommendations.append("Improve network connectivity — signal strength is poor.")

    if not recommendations:
        recommendations.append("No immediate action required. Continue routine monitoring.")

    if failure_risk_score >= 75:
        risk_level = "critical"
    elif failure_risk_score >= 50:
        risk_level = "high"
    elif failure_risk_score >= 25:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "device_id":          device.pk,
        "device_name":        device.name,
        "device_type":        device.device_type,
        "restaurant_id":      device.restaurant_id,
        "failure_risk_score": failure_risk_score,
        "risk_level":         risk_level,
        "lookback_days":      lookback_days,
        "signals":            signals,
        "recommendations":    recommendations,
        "computed_at":        timezone.now().isoformat(),
    }


def compute_restaurant_risk_summary(restaurant_id: int, lookback_days: int = 14) -> dict:
    """
    Compute risk scores for all active devices in a restaurant and return
    an aggregate summary.
    """
    from apps.devices.models import Device

    devices = Device.objects.filter(
        restaurant_id=restaurant_id,
        status__in=["ACTIVE", "LOW_BATTERY"],
    )
    results = []
    for device in devices:
        result = compute_device_risk(device.pk, lookback_days)
        if "error" not in result:
            results.append(result)

    if not results:
        return {"restaurant_id": restaurant_id, "devices": [], "overall_risk": "low"}

    max_score  = max(r["failure_risk_score"] for r in results)
    avg_score  = sum(r["failure_risk_score"] for r in results) / len(results)

    if max_score >= 75:
        overall = "critical"
    elif max_score >= 50:
        overall = "high"
    elif avg_score >= 25:
        overall = "medium"
    else:
        overall = "low"

    critical_devices = [r for r in results if r["risk_level"] in ("critical", "high")]

    return {
        "restaurant_id":   restaurant_id,
        "device_count":    len(results),
        "overall_risk":    overall,
        "max_risk_score":  round(max_score, 1),
        "avg_risk_score":  round(avg_score, 1),
        "critical_devices": critical_devices,
        "all_devices":     results,
    }
