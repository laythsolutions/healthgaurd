"""URL configuration for alerts app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AlertViewSet, AlertRuleViewSet, NotificationLogViewSet

router = DefaultRouter()
router.register(r'alerts', AlertViewSet, basename='alert')
router.register(r'rules', AlertRuleViewSet, basename='alert-rule')
router.register(r'notifications', NotificationLogViewSet, basename='notification-log')

urlpatterns = [
    path('', include(router.urls)),
]
