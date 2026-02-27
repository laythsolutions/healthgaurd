"""URL configuration for HealthGuard Cloud Backend"""

import os
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, Http404
from django.views.generic import TemplateView

def _openapi_yaml_view(request):
    """Serve the hand-maintained OpenAPI spec from schemas/openapi.yaml."""
    spec_path = settings.BASE_DIR.parent.parent / 'schemas' / 'openapi.yaml'
    if not spec_path.exists():
        raise Http404("openapi.yaml not found")
    content = spec_path.read_bytes()
    return HttpResponse(content, content_type='application/yaml')


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

    # RFC-002: product & retail transaction data pipeline
    path('api/v1/products/', include('apps.products.urls')),

    # Jurisdiction submission push API
    path('api/v1/submissions/', include('apps.submissions.urls')),

    # API Documentation — Redoc UI + raw OpenAPI spec (no extra packages required)
    path('api/docs/', TemplateView.as_view(template_name='api_docs.html'), name='api-docs'),
    path('api/docs/openapi.yaml', _openapi_yaml_view, name='api-docs-spec'),
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
