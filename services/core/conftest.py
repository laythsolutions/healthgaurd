import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ANONYMIZATION_SALT", "test-salt-not-for-production")


def pytest_configure(config):  # noqa: ARG001
    """
    Point the timeseries database alias at the same DB as 'default' during
    tests.  This prevents the multi-DB setup from creating a second test
    database and avoids cross-database FK migration failures (sensors.0001
    depends on devices.0001 which lives on the default DB).

    Sensor/timeseries routing still works at the application level; the
    split only matters for raw performance, not correctness in tests.
    """
    from django.conf import settings

    # Only apply when settings are already configured (pytest-django calls
    # pytest_configure before Django setup in some modes, so guard here).
    try:
        ts_db = settings.DATABASES.get("timeseries", {})
        default_db = settings.DATABASES.get("default", {})
        if ts_db and default_db:
            settings.DATABASES["timeseries"] = dict(default_db)
    except Exception:
        pass

    # Disable all DRF throttling during tests so rate-limit assertions
    # don't bleed across test cases sharing the same cache/IP.
    try:
        rf = settings.REST_FRAMEWORK
        rf.setdefault("DEFAULT_THROTTLE_CLASSES", [])
        rf["DEFAULT_THROTTLE_CLASSES"] = []
        rf["DEFAULT_THROTTLE_RATES"] = {
            k: "10000/hour" for k in rf.get("DEFAULT_THROTTLE_RATES", {})
        }
    except Exception:
        pass
