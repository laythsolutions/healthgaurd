"""URL configuration for HealthGuard Cloud Backend"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

# API Documentation
schema_view = get_schema_view(
    openapi.Info(
        title="HealthGuard API",
        default_version='v1',
        description="Restaurant Compliance Monitoring Platform API",
        terms_of_service="https://healthguard.com/terms/",
        contact=openapi.Contact(email="api@healthguard.com"),
        license=openapi.License(name="Proprietary"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # API v1
    path('api/v1/accounts/', include('apps.accounts.urls')),
    path('api/v1/restaurants/', include('apps.restaurants.urls')),
    path('api/v1/devices/', include('apps.devices.urls')),
    path('api/v1/sensors/', include('apps.sensors.urls')),
    path('api/v1/alerts/', include('apps.alerts.urls')),
    path('api/v1/analytics/', include('apps.analytics.urls')),
    path('api/v1/reports/', include('apps.reports.urls')),
    path('api/v1/ota/', include('apps.ota.urls')),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # Health check
    path('health/', include('health_check.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
