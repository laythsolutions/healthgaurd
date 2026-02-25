"""URL routing for OTA app"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OTAManifestViewSet,
    GatewayUpdateStatusViewSet,
    UpdateCheckView,
    UpdateSuccessView,
    UpdateFailureView
)

router = DefaultRouter()
router.register(r'manifests', OTAManifestViewSet, basename='ota-manifest')
router.register(r'status', GatewayUpdateStatusViewSet, basename='gateway-update-status')

urlpatterns = [
    path('', include(router.urls)),
    path('check/', UpdateCheckView.as_view(), name='ota-check'),
    path('updates/success/', UpdateSuccessView.as_view(), name='ota-success'),
    path('updates/failure/', UpdateFailureView.as_view(), name='ota-failure'),
]
