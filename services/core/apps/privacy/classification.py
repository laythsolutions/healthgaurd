"""
Data Classification Framework
===============================

Every API endpoint and model is assigned a classification level.
The `DataClassificationPermission` DRF permission class checks whether
the requesting user's role satisfies the declared classification before
the view processes any data.

Classification levels (ascending sensitivity)
----------------------------------------------
  public      Any request, authenticated or not
  internal    Any authenticated user
  restricted  Staff / health-dept inspector / admin
  phi         Protected Health Information — health dept or superuser only
  pii         Never exposed via API — server-side / admin console only

Usage
-----
In a ViewSet or APIView, declare the classification:

    from apps.privacy.classification import DataClassification, DataClassificationPermission

    class ClinicalCaseViewSet(viewsets.ModelViewSet):
        data_classification = DataClassification.PHI
        permission_classes   = [IsAuthenticated, DataClassificationPermission]

The permission class reads `data_classification` from the view instance.
If not set, it defaults to `INTERNAL`.

Serializer field filtering
--------------------------
Use `ClassifiedSerializerMixin` on a serializer to strip fields that
exceed the requesting user's access level:

    class PatientSerializer(ClassifiedSerializerMixin, serializers.ModelSerializer):
        field_classifications = {
            'subject_hash': DataClassification.PHI,
            'geohash':      DataClassification.RESTRICTED,
        }
"""

from __future__ import annotations

import logging
from enum import IntEnum
from typing import Optional

from rest_framework.permissions import BasePermission

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Classification levels
# ---------------------------------------------------------------------------

class DataClassification(IntEnum):
    """
    Ordered sensitivity tiers.  Higher value = more sensitive.
    Comparison operators work naturally: PHI > INTERNAL is True.
    """
    PUBLIC     = 0   # No restriction — anyone may access
    INTERNAL   = 1   # Authenticated users only
    RESTRICTED = 2   # Staff / health-dept inspectors / admin
    PHI        = 3   # Protected Health Information — health dept or superuser
    PII        = 4   # Never exposed via API (server-side / admin only)

    @classmethod
    def from_label(cls, label: str) -> "DataClassification":
        return cls[label.upper()]


# ---------------------------------------------------------------------------
# Role groups (must exist in Django Groups)
# ---------------------------------------------------------------------------

_HEALTH_DEPT_GROUPS = frozenset(["health_dept", "health_department", "inspector"])
_ADMIN_GROUPS       = frozenset(["admin", "platform_admin"])


def _user_max_classification(user) -> DataClassification:
    """
    Derive the highest classification level a user may access.
    Query is cached on the user instance to avoid N+1 across permission checks.
    """
    if not user or not user.is_authenticated:
        return DataClassification.PUBLIC

    if user.is_superuser:
        return DataClassification.PHI   # PII never exposed; PHI is the ceiling

    # Cache the resolved level to avoid repeated group queries per request
    if not hasattr(user, '_classification_level'):
        group_names = set(user.groups.values_list("name", flat=True))
        if group_names & _ADMIN_GROUPS or user.is_staff:
            level = DataClassification.RESTRICTED
        elif group_names & _HEALTH_DEPT_GROUPS:
            level = DataClassification.PHI
        else:
            level = DataClassification.INTERNAL
        user._classification_level = level

    return user._classification_level


def user_may_access(user, classification: DataClassification) -> bool:
    """Return True if `user` is allowed to access data at `classification` level."""
    return _user_max_classification(user) >= classification


# ---------------------------------------------------------------------------
# DRF permission class
# ---------------------------------------------------------------------------

class DataClassificationPermission(BasePermission):
    """
    DRF permission that enforces the data_classification declared on the view.

    Apply alongside an authentication permission:
        permission_classes = [IsAuthenticated, DataClassificationPermission]

    The view may override the default by setting:
        data_classification = DataClassification.RESTRICTED
    """

    message = "You do not have permission to access data at this classification level."

    def has_permission(self, request, view) -> bool:
        cls = getattr(view, "data_classification", DataClassification.INTERNAL)
        allowed = user_may_access(request.user, cls)
        if not allowed:
            logger.warning(
                "Classification denied: user=%s classification=%s path=%s",
                getattr(request.user, "username", "anon"),
                cls.name,
                request.path,
            )
        return allowed

    def has_object_permission(self, request, view, obj) -> bool:
        # Row-level classification — check the object's own classification if present
        obj_cls = getattr(obj, "data_classification", None)
        if obj_cls is None:
            return True
        return user_may_access(request.user, DataClassification(obj_cls))


# ---------------------------------------------------------------------------
# Serializer mixin — field-level stripping
# ---------------------------------------------------------------------------

class ClassifiedSerializerMixin:
    """
    Mixin for DRF serializers that strips fields exceeding the requesting
    user's classification level.

    Declare which fields are elevated:
        class MySerializer(ClassifiedSerializerMixin, serializers.ModelSerializer):
            field_classifications = {
                'subject_hash': DataClassification.PHI,
                'geohash':      DataClassification.RESTRICTED,
            }

    The mixin reads `request` from the serializer context; if absent (e.g. tests
    without request context), no fields are stripped.
    """

    field_classifications: dict[str, DataClassification] = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if not request:
            return

        user_level = _user_max_classification(request.user)
        to_remove = [
            field
            for field, required_level in self.field_classifications.items()
            if required_level > user_level and field in self.fields
        ]
        for field in to_remove:
            self.fields.pop(field)


# ---------------------------------------------------------------------------
# Model registry — maps model class → classification (without touching models)
# ---------------------------------------------------------------------------

#: Registry populated at app startup.
#: Keys are "<app_label>.<ModelName>" strings.
_MODEL_REGISTRY: dict[str, DataClassification] = {}


def register_model_classification(app_label: str, model_name: str,
                                   classification: DataClassification) -> None:
    """Register a model's classification level at startup."""
    key = f"{app_label}.{model_name}"
    _MODEL_REGISTRY[key] = classification


def get_model_classification(app_label: str, model_name: str) -> DataClassification:
    """Look up the classification for a model (default: INTERNAL)."""
    return _MODEL_REGISTRY.get(f"{app_label}.{model_name}", DataClassification.INTERNAL)


def register_defaults() -> None:
    """
    Register all known model classifications.
    Called from `apps.privacy.apps.PrivacyConfig.ready()`.
    """
    entries = [
        # Public-access data
        ("restaurants", "Restaurant",             DataClassification.PUBLIC),
        ("restaurants", "Location",               DataClassification.INTERNAL),
        ("inspections", "InspectionRecord",       DataClassification.PUBLIC),
        ("inspections", "InspectionSchedule",     DataClassification.RESTRICTED),

        # Recall data — public (aggregated), restricted for acknowledgment workflow
        ("recalls", "Recall",                     DataClassification.PUBLIC),
        ("recalls", "RecallProduct",              DataClassification.PUBLIC),
        ("recalls", "RecallAcknowledgment",       DataClassification.RESTRICTED),

        # IoT — internal for readings, restricted for risk scores
        ("devices", "Device",                     DataClassification.INTERNAL),
        ("devices", "DeviceCalibration",          DataClassification.RESTRICTED),
        ("sensors", "SensorReading",              DataClassification.INTERNAL),

        # Alerts — restricted (restaurant staff + health dept)
        ("alerts", "Alert",                       DataClassification.RESTRICTED),
        ("alerts", "AlertRule",                   DataClassification.RESTRICTED),

        # Clinical / outbreak — PHI
        ("clinical", "ClinicalCase",              DataClassification.PHI),
        ("clinical", "CaseExposure",              DataClassification.PHI),
        ("clinical", "OutbreakInvestigation",     DataClassification.RESTRICTED),

        # Privacy infrastructure — admin only
        ("privacy", "DataSubject",                DataClassification.PHI),
        ("privacy", "ConsentRecord",              DataClassification.PHI),
        ("privacy", "DataProcessingAuditLog",     DataClassification.RESTRICTED),
    ]
    for app_label, model_name, cls in entries:
        register_model_classification(app_label, model_name, cls)
