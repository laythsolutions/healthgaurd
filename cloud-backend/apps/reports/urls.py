"""URL routing for reports app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ComplianceReportViewSet, ReportScheduleViewSet, ReportTemplateViewSet

router = DefaultRouter()
router.register(r'reports', ComplianceReportViewSet, basename='compliance-report')
router.register(r'schedules', ReportScheduleViewSet, basename='report-schedule')
router.register(r'templates', ReportTemplateViewSet, basename='report-template')

urlpatterns = [
    path('', include(router.urls)),
]
