from rest_framework import serializers
from .models import ConsentRecord, DataSubject, DataProcessingAuditLog, ConsentScope


class ConsentStatusSerializer(serializers.Serializer):
    subject_hash = serializers.CharField(read_only=True)
    scope = serializers.CharField(read_only=True)
    status = serializers.CharField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)


class ConsentUpdateSerializer(serializers.Serializer):
    scope = serializers.ChoiceField(choices=ConsentScope.choices)
    status = serializers.ChoiceField(choices=ConsentRecord.Status.choices)
    legal_basis = serializers.CharField(
        required=False, default="consent", max_length=60
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class ConsentRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConsentRecord
        fields = ["id", "scope", "status", "legal_basis", "notes", "created_at"]
        read_only_fields = fields


class DataSubjectConsentSummarySerializer(serializers.ModelSerializer):
    active_consents = serializers.SerializerMethodField()

    class Meta:
        model = DataSubject
        fields = ["subject_hash", "source_system", "age_range", "zip3", "geohash", "active_consents", "created_at"]

    def get_active_consents(self, obj):
        # Return only the most recent record per scope
        seen = {}
        for record in obj.consent_records.order_by("-created_at"):
            if record.scope not in seen:
                seen[record.scope] = {
                    "scope": record.scope,
                    "status": record.status,
                    "updated_at": record.created_at.isoformat(),
                }
        return list(seen.values())


class AuditLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataProcessingAuditLog
        fields = [
            "id", "action", "data_categories", "purpose",
            "performed_by_system", "endpoint", "record_type",
            "record_id", "created_at",
        ]
        read_only_fields = fields
