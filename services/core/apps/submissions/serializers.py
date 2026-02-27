"""
Serializers for the submissions app.

JurisdictionRegistrationSerializer — public write: new registration form
JurisdictionAccountSerializer      — read: own account status
SubmitInspectionsSerializer        — write: validate a batch of records (max 500)
BatchStatusSerializer              — read: batch status + counts + errors
"""

import re

from rest_framework import serializers

from .models import JurisdictionAccount, SubmissionBatch

_FIPS_RE = re.compile(r"^\d{2,5}$")


class JurisdictionRegistrationSerializer(serializers.ModelSerializer):
    """Validate and create a new JurisdictionAccount (status=PENDING)."""

    class Meta:
        model = JurisdictionAccount
        fields = [
            "id", "name", "fips_code", "state", "contact_email",
            "jurisdiction_type", "website", "score_system", "schema_map",
            "webhook_url", "status",
        ]
        read_only_fields = ["id", "status"]

    def validate_fips_code(self, value):
        if not _FIPS_RE.match(value):
            raise serializers.ValidationError(
                "fips_code must be 2–5 digits (e.g. '04013' for Maricopa County, AZ)."
            )
        if JurisdictionAccount.objects.filter(fips_code=value).exists():
            raise serializers.ValidationError(
                "A jurisdiction account with this FIPS code already exists."
            )
        return value

    def validate_state(self, value):
        if len(value) != 2 or not value.isalpha():
            raise serializers.ValidationError("state must be a 2-letter US state code.")
        return value.upper()

    def create(self, validated_data):
        validated_data["status"] = JurisdictionAccount.Status.PENDING
        return super().create(validated_data)


class JurisdictionAccountSerializer(serializers.ModelSerializer):
    """Read-only view of a jurisdiction account (omits api_key raw value)."""

    class Meta:
        model = JurisdictionAccount
        fields = [
            "id", "name", "fips_code", "state", "contact_email",
            "jurisdiction_type", "website", "status", "score_system",
            "schema_map", "webhook_url", "approved_at", "created_at",
        ]
        read_only_fields = fields


class _InspectionRecordSerializer(serializers.Serializer):
    """Validate a single inspection record within a batch."""

    restaurant_name = serializers.CharField(max_length=500)
    address         = serializers.CharField(max_length=500)
    inspected_at    = serializers.CharField(
        help_text="ISO 8601 datetime or date string (e.g. '2024-03-15' or '2024-03-15T14:00:00Z')"
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # All other fields are optional — pass through unchanged
        self.fields["extra"] = serializers.DictField(required=False, allow_empty=True)


class SubmitInspectionsSerializer(serializers.Serializer):
    """Validate a batch of inspection records (max 500 rows)."""

    records = serializers.ListField(
        child=serializers.DictField(),
        min_length=1,
        max_length=500,
    )

    def validate_records(self, records):
        errors = []
        for idx, record in enumerate(records):
            missing = []
            for required in ("restaurant_name", "address", "inspected_at"):
                if not record.get(required):
                    missing.append(required)
            if missing:
                errors.append({
                    "row":    idx,
                    "reason": f"Missing required field(s): {', '.join(missing)}",
                })
        if errors:
            raise serializers.ValidationError(errors)
        return records


class BatchStatusSerializer(serializers.ModelSerializer):
    """Read batch status, counts, and row-level errors."""

    jurisdiction_name = serializers.CharField(source="jurisdiction.name", read_only=True)
    fips_code         = serializers.CharField(source="jurisdiction.fips_code", read_only=True)

    class Meta:
        model = SubmissionBatch
        fields = [
            "id", "jurisdiction_name", "fips_code",
            "status", "source_format",
            "total_rows", "created_count", "skipped_count", "error_count",
            "row_errors",
            "webhook_delivered", "webhook_delivered_at",
            "submitted_at", "completed_at",
        ]
        read_only_fields = fields
