"""URL configuration for HealthGuard Cloud Backend"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions

try:
    from drf_yasg.views import get_schema_view
    from drf_yasg import openapi
    schema_view = get_schema_view(
        openapi.Info(
            title="HealthGuard API",
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
    _yasg_available = True
except ImportError:
    _yasg_available = False

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

]

# API Documentation (requires drf-yasg: pip install drf-yasg)
if _yasg_available:
    urlpatterns += [
        path('api/docs/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        path('api/redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    ]

# OIDC SSO — only active when mozilla-django-oidc is installed
try:
    import mozilla_django_oidc  # noqa: F401
    urlpatterns += [path('oidc/', include('mozilla_django_oidc.urls'))]
except ImportError:
    pass

# Health check — only active when django-health-check is installed
try:
    import health_check  # noqa: F401
    urlpatterns += [path('health/', include('health_check.urls'))]
except ImportError:
    pass

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
