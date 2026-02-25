from rest_framework import serializers
from .models import Inspection, InspectionSchedule, InspectionViolation


class InspectionViolationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InspectionViolation
        fields = [
            "id", "code", "description", "severity", "violation_status",
            "category", "location_description", "notes", "corrective_action",
            "points_deducted",
        ]


class InspectionListSerializer(serializers.ModelSerializer):
    critical_violations = serializers.SerializerMethodField()
    total_violations = serializers.SerializerMethodField()
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = Inspection
        fields = [
            "id", "restaurant", "restaurant_name", "inspection_type",
            "inspected_at", "score", "grade", "passed", "closed",
            "source_jurisdiction", "critical_violations", "total_violations",
        ]

    def get_critical_violations(self, obj):
        return obj.violations.filter(severity="critical").count()

    def get_total_violations(self, obj):
        return obj.violations.count()


class InspectionDetailSerializer(serializers.ModelSerializer):
    violations = InspectionViolationSerializer(many=True, read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    restaurant_address = serializers.CharField(source="restaurant.address", read_only=True)

    class Meta:
        model = Inspection
        fields = [
            "id", "restaurant", "restaurant_name", "restaurant_address",
            "external_id", "source_jurisdiction", "inspection_type",
            "inspected_at", "score", "grade", "passed",
            "closed", "closure_reason", "reopened_at",
            "report_url", "violations", "created_at", "updated_at",
        ]


class InspectionWriteSerializer(serializers.ModelSerializer):
    """Used by health dept portal to submit inspection records."""
    violations = InspectionViolationSerializer(many=True, required=False)

    class Meta:
        model = Inspection
        fields = [
            "restaurant", "external_id", "source_jurisdiction",
            "inspection_type", "inspected_at", "inspector_id",
            "score", "grade", "passed", "closed", "closure_reason",
            "reopened_at", "report_url", "raw_data", "violations",
        ]

    def create(self, validated_data):
        violations_data = validated_data.pop("violations", [])
        inspection = Inspection.objects.create(**validated_data)
        for v in violations_data:
            InspectionViolation.objects.create(inspection=inspection, **v)
        return inspection

    def update(self, instance, validated_data):
        violations_data = validated_data.pop("violations", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if violations_data is not None:
            instance.violations.all().delete()
            for v in violations_data:
                InspectionViolation.objects.create(inspection=instance, **v)

        return instance


class InspectionScheduleSerializer(serializers.ModelSerializer):
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)
    restaurant_address = serializers.CharField(source="restaurant.address", read_only=True)
    restaurant_city = serializers.CharField(source="restaurant.city", read_only=True)
    restaurant_state = serializers.CharField(source="restaurant.state", read_only=True)

    class Meta:
        model = InspectionSchedule
        fields = [
            "id", "restaurant", "restaurant_name", "restaurant_address",
            "restaurant_city", "restaurant_state",
            "scheduled_date", "scheduled_time", "inspection_type",
            "assigned_inspector_id", "jurisdiction", "notes", "status",
            "completed_inspection", "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "created_by"]
