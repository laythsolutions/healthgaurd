"""Serializers for restaurants app"""

from rest_framework import serializers
from .models import Organization, Restaurant, Location, ComplianceCheck


class LocationSerializer(serializers.ModelSerializer):
    """Serializer for Location model"""

    class Meta:
        model = Location
        fields = [
            'id', 'name', 'location_type', 'temp_min_f', 'temp_max_f',
            'description', 'position', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class RestaurantSerializer(serializers.ModelSerializer):
    """Serializer for Restaurant model"""
    locations = LocationSerializer(many=True, read_only=True)
    compliance_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Restaurant
        fields = [
            'id', 'organization', 'name', 'code', 'address', 'city', 'state',
            'zip_code', 'country', 'latitude', 'longitude', 'cuisine_type',
            'seating_capacity', 'square_footage', 'health_department_id',
            'last_inspection_date', 'last_inspection_score', 'compliance_score',
            'compliance_percentage', 'gateway_id', 'gateway_last_seen',
            'gateway_version', 'status', 'locations', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'compliance_score']

    def get_compliance_percentage(self, obj):
        return float(obj.compliance_score) if obj.compliance_score else 0


class RestaurantDetailSerializer(RestaurantSerializer):
    """Detailed serializer with more info"""
    recent_alerts_count = serializers.SerializerMethodField()
    active_devices_count = serializers.SerializerMethodField()

    class Meta(RestaurantSerializer.Meta):
        fields = RestaurantSerializer.Meta.fields + [
            'recent_alerts_count', 'active_devices_count'
        ]

    def get_recent_alerts_count(self, obj):
        from apps.alerts.models import Alert
        last_24h = timezone.now() - timedelta(hours=24)
        return Alert.objects.filter(
            restaurant=obj,
            created_at__gte=last_24h
        ).count()

    def get_active_devices_count(self, obj):
        return obj.devices.filter(status='active').count()


class OrganizationSerializer(serializers.ModelSerializer):
    """Serializer for Organization model"""
    restaurants_count = serializers.SerializerMethodField()
    total_monthly_cost = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'tier', 'address', 'phone', 'email', 'logo_url',
            'subscription_status', 'monthly_fee', 'last_inspection_date',
            'last_inspection_score', 'compliance_score', 'restaurants_count',
            'total_monthly_cost', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'compliance_score']

    def get_restaurants_count(self, obj):
        return obj.restaurants.count()

    def get_total_monthly_cost(self, obj):
        return obj.restaurants.count() * float(obj.monthly_fee)


class ComplianceCheckSerializer(serializers.ModelSerializer):
    """Serializer for ComplianceCheck model"""
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)

    class Meta:
        model = ComplianceCheck
        fields = [
            'id', 'restaurant', 'location', 'location_name', 'check_type',
            'performed_by', 'performed_by_name', 'value', 'notes', 'passed',
            'corrective_action', 'photo_url', 'checked_at', 'created_at'
        ]
        read_only_fields = ['created_at']
