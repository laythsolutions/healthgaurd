"""URL configuration for restaurants app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet,
    RestaurantViewSet,
    LocationViewSet,
    ComplianceCheckViewSet,
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'restaurants', RestaurantViewSet, basename='restaurant')
router.register(r'locations', LocationViewSet, basename='location')
router.register(r'compliance-checks', ComplianceCheckViewSet, basename='compliance-check')

urlpatterns = [
    path('', include(router.urls)),
]
