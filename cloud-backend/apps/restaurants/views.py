"""Views for restaurants app"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta

from .models import Organization, Restaurant, Location, ComplianceCheck
from .serializers import (
    OrganizationSerializer,
    RestaurantSerializer,
    RestaurantDetailSerializer,
    LocationSerializer,
    ComplianceCheckSerializer,
)


class OrganizationViewSet(viewsets.ModelViewSet):
    """ViewSet for Organization model"""

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        tier = self.request.query_params.get('tier')
        if tier:
            queryset = queryset.filter(tier=tier)
        return queryset

    @action(detail=True, methods=['get'])
    def restaurants(self, request, pk=None):
        """Get all restaurants for an organization"""
        organization = self.get_object()
        restaurants = organization.restaurants.all()
        serializer = RestaurantSerializer(restaurants, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def compliance_report(self, request, pk=None):
        """Get compliance report for organization"""
        organization = self.get_object()
        restaurants = organization.restaurants.all()

        report = {
            'organization': organization.name,
            'total_restaurants': restaurants.count(),
            'avg_compliance_score': sum(r.compliance_score or 0 for r in restaurants) / max(restaurants.count(), 1),
            'restaurants': [
                {
                    'name': r.name,
                    'compliance_score': r.compliance_score,
                    'last_inspection': r.last_inspection_date,
                    'last_inspection_score': r.last_inspection_score,
                }
                for r in restaurants
            ]
        }
        return Response(report)


class RestaurantViewSet(viewsets.ModelViewSet):
    """ViewSet for Restaurant model"""

    queryset = Restaurant.objects.select_related('organization').prefetch_related('locations').all()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return RestaurantDetailSerializer
        return RestaurantSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        org_id = self.request.query_params.get('organization')
        status_filter = self.request.query_params.get('status')

        if org_id:
            queryset = queryset.filter(organization_id=org_id)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=True, methods=['get'])
    def locations(self, request, pk=None):
        """Get all locations for a restaurant"""
        restaurant = self.get_object()
        locations = restaurant.locations.all()
        serializer = LocationSerializer(locations, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_location(self, request, pk=None):
        """Add a new location to a restaurant"""
        restaurant = self.get_object()
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(restaurant=restaurant)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def compliance_history(self, request, pk=None):
        """Get compliance history for a restaurant"""
        restaurant = self.get_object()
        days = int(request.query_params.get('days', 30))

        start_date = timezone.now() - timedelta(days=days)
        checks = ComplianceCheck.objects.filter(
            restaurant=restaurant,
            checked_at__gte=start_date
        ).order_by('-checked_at')

        serializer = ComplianceCheckSerializer(checks, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def dashboard(self, request, pk=None):
        """Get dashboard data for a restaurant"""
        restaurant = self.get_object()

        from apps.devices.models import Device
        from apps.alerts.models import Alert
        from apps.sensors.models import SensorReading

        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)

        # Get active devices
        active_devices = Device.objects.filter(
            restaurant=restaurant,
            status='active'
        ).count()

        # Get recent alerts
        critical_alerts = Alert.objects.filter(
            restaurant=restaurant,
            severity='critical',
            created_at__gte=last_24h,
            acknowledged=False
        ).count()

        # Get latest readings
        latest_readings = []
        for device in Device.objects.filter(restaurant=restaurant, status='active'):
            latest = SensorReading.objects.filter(
                device=device
            ).order_by('-timestamp').first()

            if latest:
                latest_readings.append({
                    'device_id': device.device_id,
                    'device_name': device.name,
                    'location': device.location.name if device.location else None,
                    'temperature': latest.temperature,
                    'timestamp': latest.timestamp,
                })

        dashboard_data = {
            'restaurant': RestaurantSerializer(restaurant).data,
            'summary': {
                'active_devices': active_devices,
                'critical_alerts': critical_alerts,
                'compliance_score': restaurant.compliance_score,
            },
            'latest_readings': latest_readings[:10],  # Last 10 readings
        }

        return Response(dashboard_data)


class LocationViewSet(viewsets.ModelViewSet):
    """ViewSet for Location model"""

    queryset = Location.objects.select_related('restaurant').all()
    serializer_class = LocationSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')
        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        return queryset


class ComplianceCheckViewSet(viewsets.ModelViewSet):
    """ViewSet for ComplianceCheck model"""

    queryset = ComplianceCheck.objects.select_related('restaurant', 'location', 'performed_by').all()
    serializer_class = ComplianceCheckSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        restaurant_id = self.request.query_params.get('restaurant')
        check_type = self.request.query_params.get('check_type')

        if restaurant_id:
            queryset = queryset.filter(restaurant_id=restaurant_id)
        if check_type:
            queryset = queryset.filter(check_type=check_type)

        return queryset

    def perform_create(self, serializer):
        serializer.save(performed_by=self.request.user)
