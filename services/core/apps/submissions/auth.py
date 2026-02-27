"""
Custom DRF authentication for the jurisdiction submission API.

Expects:  X-Submission-Key: hg_live_<...>

Looks up the SHA-256 hash in accounts.APIKey, verifies:
  - scopes contains 'submissions:write'
  - is_active = True
  - not expired
  - request IP is in allowed_ips (if list is non-empty)
"""

import hashlib
import logging
from ipaddress import ip_address, ip_network

from django.utils import timezone
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from apps.accounts.models import APIKey

logger = logging.getLogger(__name__)

HEADER = "HTTP_X_SUBMISSION_KEY"
REQUIRED_SCOPE = "submissions:write"


def _get_client_ip(request) -> str:
    xff = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def _ip_allowed(client_ip: str, allowed_ips: list) -> bool:
    if not allowed_ips:
        return True
    try:
        addr = ip_address(client_ip)
        for entry in allowed_ips:
            try:
                if addr in ip_network(entry, strict=False):
                    return True
            except ValueError:
                continue
    except ValueError:
        pass
    return False


class SubmissionAPIKeyAuthentication(BaseAuthentication):
    def authenticate(self, request):
        raw_key = request.META.get(HEADER)
        if not raw_key:
            return None  # let other authenticators try

        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()

        try:
            api_key = (
                APIKey.objects.select_related("user")
                .get(key_hash=key_hash, is_active=True)
            )
        except APIKey.DoesNotExist:
            raise AuthenticationFailed("Invalid or inactive submission key.")

        if REQUIRED_SCOPE not in (api_key.scopes or []):
            raise AuthenticationFailed("Submission key missing 'submissions:write' scope.")

        if api_key.expires_at and api_key.expires_at < timezone.now():
            raise AuthenticationFailed("Submission key has expired.")

        client_ip = _get_client_ip(request)
        if not _ip_allowed(client_ip, api_key.allowed_ips or []):
            raise AuthenticationFailed("Request IP not in submission key allowlist.")

        # Stamp last_used_at without triggering full model signals
        APIKey.objects.filter(pk=api_key.pk).update(last_used_at=timezone.now())

        if api_key.user is None:
            raise AuthenticationFailed("Submission key not linked to a user account.")

        return (api_key.user, api_key)

    def authenticate_header(self, request):
        return "X-Submission-Key"
