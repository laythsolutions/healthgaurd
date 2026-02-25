"""URL configuration for analytics app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ComplianceReportViewSet,
    InspectionPredictionViewSet,
    MetricSnapshotViewSet,
    AnalyticsViewSet,
)

router = DefaultRouter()
router.register(r'reports', ComplianceReportViewSet, basename='compliance-report')
router.register(r'predictions', InspectionPredictionViewSet, basename='inspection-prediction')
router.register(r'metrics', MetricSnapshotViewSet, basename='metric-snapshot')
router.register(r'analytics', AnalyticsViewSet, basename='analytics')

urlpatterns = [
    path('', include(router.urls)),
]
