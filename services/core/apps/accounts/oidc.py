"""
OIDC Authentication Backend for health department SSO.

Uses mozilla-django-oidc as the base. Each participating health department
provides an OIDC-compliant IdP (Okta, Azure AD, Keycloak, etc.).

Install:
    pip install mozilla-django-oidc

Add to INSTALLED_APPS:
    'mozilla_django_oidc',

Add to AUTHENTICATION_BACKENDS in settings:
    'apps.accounts.oidc.HealthDeptOIDCBackend',

Add to MIDDLEWARE (after SessionMiddleware):
    'mozilla_django_oidc.middleware.SessionRefresh',

Wire URLs in config/urls.py:
    path('oidc/', include('mozilla_django_oidc.urls')),

Required environment variables (per health department IdP):
    OIDC_RP_CLIENT_ID       — client ID from the IdP app registration
    OIDC_RP_CLIENT_SECRET   — client secret
    OIDC_OP_JWKS_ENDPOINT   — e.g. https://login.microsoftonline.com/{tid}/discovery/v2.0/keys
    OIDC_OP_AUTHORIZATION_ENDPOINT
    OIDC_OP_TOKEN_ENDPOINT
    OIDC_OP_USER_ENDPOINT   — userinfo endpoint
    OIDC_HEALTH_DEPT_DOMAIN — email domain to require, e.g. "health.ca.gov"
                              (optional; leave blank to allow any verified domain)

Claims mapping
--------------
The OIDC backend maps IdP claims to [PROJECT_NAME] groups and roles:
  - If the IdP groups claim includes "HealthDeptInspector" → Django group "health_dept"
  - If the IdP groups claim includes "HealthDeptAdmin"    → Django group "admin"
  - If the user's email domain matches OIDC_HEALTH_DEPT_DOMAIN, they receive
    the "health_dept" group even without an explicit groups claim.

Session behaviour
-----------------
Access tokens are validated on every request by SessionRefresh middleware.
If the OIDC session expires, users are redirected to the IdP for re-authentication.
"""

import logging

from django.conf import settings
from django.contrib.auth.models import Group

logger = logging.getLogger(__name__)

try:
    from mozilla_django_oidc.auth import OIDCAuthenticationBackend
    _OIDC_AVAILABLE = True
except ImportError:
    # Graceful degradation if package not yet installed.
    OIDCAuthenticationBackend = object
    _OIDC_AVAILABLE = False


# Groups created in the DB by data migrations / management command
_HEALTH_DEPT_GROUP = "health_dept"
_ADMIN_GROUP       = "admin"

# IdP groups claim key (Azure AD / Okta both typically use "groups")
_GROUPS_CLAIM = getattr(settings, "OIDC_GROUPS_CLAIM", "groups")

# IdP group names that map to [PROJECT_NAME] roles
_INSPECTOR_CLAIM_VALUE = getattr(settings, "OIDC_INSPECTOR_GROUP", "HealthDeptInspector")
_ADMIN_CLAIM_VALUE     = getattr(settings, "OIDC_ADMIN_GROUP",     "HealthDeptAdmin")

# Optional: restrict login to users from a specific email domain
_REQUIRED_DOMAIN = getattr(settings, "OIDC_HEALTH_DEPT_DOMAIN", "")


class HealthDeptOIDCBackend(OIDCAuthenticationBackend):
    """
    Custom OIDC backend that maps IdP claims to health department roles
    and creates/updates the corresponding Django user on every SSO login.
    """

    def verify_claims(self, claims: dict) -> bool:
        """
        Optional email-domain restriction.
        If OIDC_HEALTH_DEPT_DOMAIN is set, only users from that domain can log in.
        """
        if not super().verify_claims(claims):
            return False

        if _REQUIRED_DOMAIN:
            email = claims.get("email", "")
            if not email.lower().endswith(f"@{_REQUIRED_DOMAIN.lower()}"):
                logger.warning(
                    "OIDC login rejected: email %s does not match domain %s",
                    email, _REQUIRED_DOMAIN,
                )
                return False

        return True

    def create_user(self, claims: dict):
        user = super().create_user(claims)
        self._sync_groups(user, claims)
        logger.info("OIDC: created user %s via SSO", user.username)
        return user

    def update_user(self, user, claims: dict):
        user = super().update_user(user, claims)
        self._sync_groups(user, claims)
        return user

    def _sync_groups(self, user, claims: dict) -> None:
        """
        Derive group memberships from OIDC claims and sync them to the
        Django user.  Existing [PROJECT_NAME] role groups are reset on
        every login so that IdP revocations take effect immediately.
        """
        idp_groups = set(claims.get(_GROUPS_CLAIM, []))
        email = claims.get("email", "")

        # Determine target groups
        target_groups: set[str] = set()

        if _ADMIN_CLAIM_VALUE in idp_groups:
            target_groups.add(_ADMIN_GROUP)
            target_groups.add(_HEALTH_DEPT_GROUP)

        elif (
            _INSPECTOR_CLAIM_VALUE in idp_groups
            or (
                _REQUIRED_DOMAIN
                and email.lower().endswith(f"@{_REQUIRED_DOMAIN.lower()}")
            )
        ):
            target_groups.add(_HEALTH_DEPT_GROUP)

        # Ensure the groups exist (idempotent)
        group_objects = []
        for name in target_groups:
            group, _ = Group.objects.get_or_create(name=name)
            group_objects.append(group)

        # Remove only the role groups we manage; leave other groups untouched
        managed = {_HEALTH_DEPT_GROUP, _ADMIN_GROUP}
        user.groups.remove(
            *user.groups.filter(name__in=managed)
        )
        if group_objects:
            user.groups.add(*group_objects)

        # Mirror admin status to is_staff so Django admin is accessible for admins
        user.is_staff = _ADMIN_GROUP in target_groups
        user.save(update_fields=["is_staff"])

        logger.info(
            "OIDC: synced user %s → groups %s",
            user.username, sorted(target_groups),
        )

    # -----------------------------------------------------------------------
    # Attribute mapping
    # -----------------------------------------------------------------------

    def get_username(self, claims: dict) -> str:
        """Use email as username (unique, stable across SSO sessions)."""
        return claims.get("email", "").lower()

    def get_userinfo(self, access_token, id_token, payload):
        """Standard userinfo fetch; override here to add caching if needed."""
        return super().get_userinfo(access_token, id_token, payload)
