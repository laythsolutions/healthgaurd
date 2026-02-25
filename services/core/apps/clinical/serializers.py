from rest_framework import serializers
from .models import ClinicalCase, ClinicalExposure, OutbreakInvestigation, ReportingInstitution
from apps.privacy.services import AnonymizationService


class ClinicalExposureSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClinicalExposure
        fields = [
            "id", "exposure_type", "exposure_date", "geohash",
            "establishment_type", "food_items", "linked_recall",
            "confidence", "notes",
        ]


class ClinicalCaseSubmissionSerializer(serializers.Serializer):
    """
    Accepts raw case data from healthcare institutions.
    AnonymizationService is applied before any data is persisted.

    Deliberately accepts raw fields like 'patient_id', 'age', 'date_of_birth',
    'latitude', 'longitude' — these are stripped and never stored.
    """

    # Raw identity fields — used only to derive subject_hash and anonymized bands
    patient_id = serializers.CharField(write_only=True, required=True)
    age = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    date_of_birth = serializers.DateField(write_only=True, required=False, allow_null=True)
    sex = serializers.ChoiceField(
        choices=[("M", "Male"), ("F", "Female"), ("O", "Other/Unknown")],
        required=False,
        allow_blank=True,
        default="",
    )

    # Location — raw, will be geohashed
    latitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    longitude = serializers.FloatField(write_only=True, required=False, allow_null=True)
    zip_code = serializers.CharField(write_only=True, required=False, allow_blank=True, default="")

    # Illness details — stored as-is (no PII)
    illness_status = serializers.ChoiceField(
        choices=ClinicalCase.IllnessStatus.choices,
        default=ClinicalCase.IllnessStatus.SUSPECTED,
    )
    onset_date = serializers.DateField(required=False, allow_null=True)
    illness_duration_days = serializers.IntegerField(required=False, allow_null=True)
    symptoms = serializers.ListField(
        child=serializers.CharField(), required=False, default=list
    )
    stool_culture_collected = serializers.BooleanField(required=False, allow_null=True)
    pathogen = serializers.CharField(required=False, allow_blank=True, default="")
    serotype = serializers.CharField(required=False, allow_blank=True, default="")
    hospitalized = serializers.BooleanField(required=False, allow_null=True)
    icu_admission = serializers.BooleanField(required=False, allow_null=True)
    outcome = serializers.ChoiceField(
        choices=ClinicalCase.OutcomeStatus.choices,
        default=ClinicalCase.OutcomeStatus.UNKNOWN,
    )

    # Exposures (optional)
    exposures = ClinicalExposureSerializer(many=True, required=False, default=list)

    def create(self, validated_data):
        svc = AnonymizationService()
        exposures_data = validated_data.pop("exposures", [])

        # Anonymize
        anon = svc.anonymize_clinical_case(validated_data)

        case = ClinicalCase.objects.create(
            subject_hash=anon.get("subject_hash", ""),
            age_range=anon.get("age_range", ""),
            sex=validated_data.get("sex", ""),
            geohash=anon.get("geohash", ""),
            zip3=anon.get("zip3", ""),
            illness_status=validated_data.get("illness_status", ClinicalCase.IllnessStatus.SUSPECTED),
            onset_date=validated_data.get("onset_date"),
            illness_duration_days=validated_data.get("illness_duration_days"),
            symptoms=validated_data.get("symptoms", []),
            stool_culture_collected=validated_data.get("stool_culture_collected"),
            pathogen=validated_data.get("pathogen", ""),
            serotype=validated_data.get("serotype", ""),
            hospitalized=validated_data.get("hospitalized"),
            icu_admission=validated_data.get("icu_admission"),
            outcome=validated_data.get("outcome", ClinicalCase.OutcomeStatus.UNKNOWN),
            reporting_institution=self.context.get("institution"),
            submitted_by=self.context.get("user"),
        )

        for exp in exposures_data:
            ClinicalExposure.objects.create(case=case, **exp)

        return case


class ClinicalCaseSerializer(serializers.ModelSerializer):
    exposures = ClinicalExposureSerializer(many=True, read_only=True)

    class Meta:
        model = ClinicalCase
        fields = [
            "id", "subject_hash", "age_range", "sex", "geohash", "zip3",
            "illness_status", "onset_date", "illness_duration_days", "symptoms",
            "stool_culture_collected", "pathogen", "serotype",
            "hospitalized", "icu_admission", "outcome",
            "investigation", "exposures", "created_at",
        ]
        read_only_fields = ["subject_hash", "created_at"]


class OutbreakInvestigationSerializer(serializers.ModelSerializer):
    case_count = serializers.IntegerField(source="cases.count", read_only=True)

    class Meta:
        model = OutbreakInvestigation
        fields = [
            "id", "title", "status", "pathogen", "suspected_vehicle",
            "geographic_scope", "cluster_start_date", "cluster_end_date",
            "opened_at", "closed_at", "case_count", "case_count_at_open",
            "auto_generated", "cluster_score", "notes",
        ]
        read_only_fields = ["opened_at", "case_count"]
