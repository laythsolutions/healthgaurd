"""Custom middleware for HealthGuard"""

from django.db import connection
from threading import local

_thread_locals = local()


class TenantMiddleware:
    """Middleware for multi-tenancy support"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Store restaurant_id from request for DB queries
        if request.user.is_authenticated:
            restaurant_id = request.headers.get('X-Restaurant-ID')
            if restaurant_id:
                _thread_locals.restaurant_id = restaurant_id

        response = self.get_response(request)

        # Clean up
        if hasattr(_thread_locals, 'restaurant_id'):
            del _thread_locals.restaurant_id

        return response


def get_current_restaurant_id():
    """Get current restaurant ID from thread locals"""
    return getattr(_thread_locals, 'restaurant_id', None)


class APIVersionHeaderMiddleware:
    """
    Inject API versioning headers on every response.

    Clients can inspect these headers to:
      - Know the current stable API version (API-Version)
      - Detect when a version is sunset and plan migration (Deprecation, Sunset)

    Current versioning policy:
      - /api/v1/ — stable, supported indefinitely until a migration notice is issued
      - /api/v2/ — not yet available; stub returns 404 with a link to the roadmap

    When /api/v2/ is launched, v1 Deprecation/Sunset headers will be added here.
    """

    CURRENT_VERSION = "1"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Tag all API responses with the version they were served by
        if request.path.startswith("/api/"):
            response["API-Version"] = self.CURRENT_VERSION

        return response
