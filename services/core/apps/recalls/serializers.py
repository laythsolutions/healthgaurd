from rest_framework import serializers
from .models import Recall, RecallProduct, RecallAcknowledgment


class RecallProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecallProduct
        fields = [
            "id", "product_description", "brand_name",
            "upc_codes", "lot_numbers", "best_by_dates",
            "package_sizes", "code_info",
        ]


class RecallListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""
    product_count = serializers.IntegerField(source="products.count", read_only=True)

    class Meta:
        model = Recall
        fields = [
            "id", "source", "external_id", "title", "hazard_type",
            "classification", "status", "recalling_firm",
            "recall_initiation_date", "affected_states", "product_count",
        ]


class RecallDetailSerializer(serializers.ModelSerializer):
    products = RecallProductSerializer(many=True, read_only=True)

    class Meta:
        model = Recall
        fields = [
            "id", "source", "external_id", "title", "reason",
            "hazard_type", "classification", "status",
            "recalling_firm", "firm_city", "firm_state", "firm_country",
            "distribution_pattern", "affected_states",
            "recall_initiation_date", "center_classification_date",
            "termination_date", "voluntary_mandated",
            "initial_firm_notification", "product_quantity",
            "products", "created_at", "updated_at", "last_synced_at",
        ]


class RecallAcknowledgmentSerializer(serializers.ModelSerializer):
    recall_title = serializers.CharField(source="recall.title", read_only=True)
    restaurant_name = serializers.CharField(source="restaurant.name", read_only=True)

    class Meta:
        model = RecallAcknowledgment
        fields = [
            "id", "recall", "recall_title", "restaurant", "restaurant_name",
            "status", "notes", "remediation_date", "units_removed",
            "created_at", "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at", "recall_title", "restaurant_name"]
