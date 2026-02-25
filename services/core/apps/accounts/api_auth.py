"""API Key authentication for programmatic access"""

import logging
from django.contrib.auth.backends import BaseBackend
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import APIKey, User

logger = logging.getLogger(__name__)


class APIKeyBackend(BaseBackend):
    """Authentication backend for API keys"""

    def authenticate(self, request, key=None):
        """Authenticate using API key"""
        if key is None:
            return None

        # Hash the provided key
        import hashlib
        key_hash = hashlib.sha256(key.encode()).hexdigest()

        try:
            api_key = APIKey.objects.select_related('user', 'organization').get(
                key_hash=key_hash,
                is_active=True
            )
        except APIKey.DoesNotExist:
            return None

        # Check expiration
        if api_key.expires_at and api_key.expires_at < timezone.now():
            return None

        # Check IP whitelist
        if api_key.allowed_ips:
            client_ip = self._get_client_ip(request)
            if not self._is_ip_allowed(client_ip, api_key.allowed_ips):
                logger.warning(f"API key {api_key.key_prefix} denied for IP {client_ip}")
                return None

        # Update last used
        from django.utils import timezone
        api_key.last_used_at = timezone.now()
        api_key.save(update_fields=['last_used_at'])

        # Return user (or organization user)
        if api_key.user:
            return api_key.user

        # For organization keys, return a service user or None
        return None

    def get_user(self, user_id):
        """Get user by ID"""
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def _is_ip_allowed(self, client_ip, allowed_ips):
        """Check if client IP is in allowed list"""
        import ipaddress

        try:
            client_ip_obj = ipaddress.ip_address(client_ip)

            for allowed in allowed_ips:
                # Check if it's a CIDR range
                if '/' in allowed:
                    if client_ip_obj in ipaddress.ip_network(allowed):
                        return True
                else:
                    # Exact IP match
                    if client_ip == allowed:
                        return True

            return False

        except ValueError:
            return False


class APIKeyAuthentication(BaseAuthentication):
    """DRF authentication class for API keys"""

    def authenticate(self, request):
        """Authenticate request using API key"""
        # Get key from header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        key = auth_header[7:]  # Remove 'Bearer ' prefix

        # Don't process JWT tokens
        if key.startswith('eyJ'):
            return None

        # Authenticate with API key backend
        backend = APIKeyBackend()
        user = backend.authenticate(request, key=key)

        if user:
            return (user, None)

        raise AuthenticationFailed('Invalid API key')

    def authenticate_header(self, request):
        """Return authentication header"""
        return 'Bearer'


class HasAPIKeyScope:
    """Permission class for checking API key scopes"""

    def __init__(self, required_scopes):
        self.required_scopes = required_scopes

    def __call__(self, permission):
        """Check permission class"""
        permission.required_scopes = self.required_scopes
        return permission


class APIKeyPermission:
    """Base permission class for API key scope checking"""

    def has_permission(self, request, view):
        """Check if request has required scopes"""
        # No permission checks for non-API key auth
        if not hasattr(request, 'api_key'):
            return True

        api_key = request.api_key

        # Get required scopes for this view
        required_scopes = getattr(view, 'required_scopes', [])

        if not required_scopes:
            return True

        # Check if API key has all required scopes
        return all(scope in api_key.scopes for scope in required_scapes)


def get_api_key_from_request(request):
    """Extract and validate API key from request

    Returns:
        APIKey object or None
    """
    import hashlib

    auth_header = request.META.get('HTTP_AUTHORIZATION', '')

    if not auth_header.startswith('Bearer '):
        return None

    key = auth_header[7:]

    # Don't process JWT tokens
    if key.startswith('eyJ'):
        return None

    # Hash and lookup
    key_hash = hashlib.sha256(key.encode()).hexdigest()

    try:
        api_key = APIKey.objects.get(
            key_hash=key_hash,
            is_active=True
        )

        # Check expiration
        from django.utils import timezone
        if api_key.expires_at and api_key.expires_at < timezone.now():
            return None

        return api_key

    except APIKey.DoesNotExist:
        return None


# API Key scopes
SCOPES = {
    # Restaurant management
    'read:restaurants': 'View restaurant information',
    'write:restaurants': 'Create and edit restaurants',

    # Device management
    'read:devices': 'View device information',
    'write:devices': 'Register and configure devices',

    # Sensor data
    'read:sensors': 'View sensor readings',
    'write:sensors': 'Submit sensor readings',

    # Alerts
    'read:alerts': 'View alerts',
    'write:alerts': 'Create and acknowledge alerts',

    # Reports
    'read:reports': 'View reports',
    'write:reports': 'Generate reports',

    # Analytics
    'read:analytics': 'View analytics data',

    # Organization
    'read:organization': 'View organization details',
    'write:organization': 'Edit organization settings',

    # Users
    'read:users': 'View user information',
    'write:users': 'Create and edit users',

    # Integrations
    'webhook:receive': 'Receive webhooks',
    'webhook:send': 'Send webhooks',
}
