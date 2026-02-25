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
        title="[PROJECT_NAME] API",
        default_version='v1',
        description=(
            "Open-source food safety intelligence platform. "
            "Connects restaurant inspections, IoT sensor monitoring, "
            "recall tracking, and clinical outbreak detection."
        ),
        contact=openapi.Contact(email="api@[project-domain]"),
        license=openapi.License(name="Apache 2.0"),
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

    # OSFI: public-interest APIs
    path('api/v1/public/', include('apps.restaurants.public_urls')),
    path('api/v1/privacy/', include('apps.privacy.urls')),
    path('api/v1/recalls/', include('apps.recalls.urls')),
    path('api/v1/inspections/', include('apps.inspections.urls')),
    path('api/v1/clinical/', include('apps.clinical.urls')),

    # API Documentation
    path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),

    # OIDC SSO for health department users (mozilla-django-oidc)
    # Only active when OIDC_RP_CLIENT_ID env var is set
    path('oidc/', include('mozilla_django_oidc.urls')),

    # Health check
    path('health/', include('health_check.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
