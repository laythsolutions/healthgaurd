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
