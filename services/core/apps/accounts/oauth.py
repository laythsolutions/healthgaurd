"""OAuth2 authentication backends for Google and Microsoft"""

import logging
import requests
from django.contrib.auth import get_user_model
from django.conf import settings
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)
User = get_user_model()


class OAuth2Backend:
    """Base class for OAuth2 authentication"""

    def __init__(self):
        self.provider_name = None
        self.authorization_url = None
        self.token_url = None
        self.user_info_url = None
        self.scope = None

    def get_authorization_url(self, redirect_uri, state=None):
        """Get the authorization URL for OAuth2 flow"""
        params = {
            'client_id': self.get_client_id(),
            'redirect_uri': redirect_uri,
            'scope': self.scope,
            'response_type': 'code',
            'access_type': 'offline',
        }

        if state:
            params['state'] = state

        param_string = '&'.join(f'{k}={v}' for k, v in params.items())
        return f'{self.authorization_url}?{param_string}'

    def exchange_code_for_token(self, code, redirect_uri):
        """Exchange authorization code for access token"""
        data = {
            'code': code,
            'client_id': self.get_client_id(),
            'client_secret': self.get_client_secret(),
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }

        response = requests.post(self.token_url, data=data)
        response.raise_for_status()
        return response.json()

    def get_user_info(self, access_token):
        """Get user information from OAuth2 provider"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.user_info_url, headers=headers)
        response.raise_for_status()
        return response.json()

    def get_or_create_user(self, user_info):
        """Get or create user from OAuth2 user info"""
        email = user_info.get('email')
        if not email:
            raise ValueError("Email not provided by OAuth2 provider")

        try:
            user = User.objects.get(email=email)
            return user, False
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                email=email,
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                username=email,  # Required by Django
                is_active=True,
            )
            logger.info(f"Created new user via {self.provider_name}: {email}")
            return user, True

    def authenticate(self, code, redirect_uri):
        """Complete OAuth2 authentication flow"""
        try:
            # Exchange code for token
            token_data = self.exchange_code_for_token(code, redirect_uri)
            access_token = token_data.get('access_token')

            # Get user info
            user_info = self.get_user_info(access_token)

            # Get or create user
            user, created = self.get_or_create_user(user_info)

            return {
                'user': user,
                'access_token': access_token,
                'refresh_token': token_data.get('refresh_token'),
                'created': created,
            }

        except requests.RequestException as e:
            logger.error(f"OAuth2 authentication failed: {e}")
            raise ValueError(f"OAuth2 authentication failed: {str(e)}")

    def get_client_id(self):
        """Get client ID from settings"""
        raise NotImplementedError

    def get_client_secret(self):
        """Get client secret from settings"""
        raise NotImplementedError


class GoogleOAuth2Backend(OAuth2Backend):
    """Google OAuth2 authentication backend"""

    def __init__(self):
        super().__init__()
        self.provider_name = 'Google'
        self.authorization_url = 'https://accounts.google.com/o/oauth2/v2/auth'
        self.token_url = 'https://oauth2.googleapis.com/token'
        self.user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
        self.scope = 'openid email profile'

    def get_client_id(self):
        return getattr(settings, 'GOOGLE_OAUTH2_CLIENT_ID', '')

    def get_client_secret(self):
        return getattr(settings, 'GOOGLE_OAUTH2_CLIENT_SECRET', '')

    def get_or_create_user(self, user_info):
        """Get or create user from Google user info"""
        email = user_info.get('email')
        if not email:
            raise ValueError("Email not provided by Google")

        try:
            user = User.objects.get(email=email)
            return user, False
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                email=email,
                first_name=user_info.get('given_name', ''),
                last_name=user_info.get('family_name', ''),
                username=email,
                is_active=True,
                profile_image=user_info.get('picture', ''),
            )
            logger.info(f"Created new user via Google OAuth2: {email}")
            return user, True


class MicrosoftOAuth2Backend(OAuth2Backend):
    """Microsoft Azure AD OAuth2 authentication backend"""

    def __init__(self):
        super().__init__()
        self.provider_name = 'Microsoft'
        self.authorization_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/authorize'
        self.token_url = 'https://login.microsoftonline.com/common/oauth2/v2.0/token'
        self.user_info_url = 'https://graph.microsoft.com/v1.0/me'
        self.scope = 'openid email profile User.Read'

    def get_client_id(self):
        return getattr(settings, 'MICROSOFT_OAUTH2_CLIENT_ID', '')

    def get_client_secret(self):
        return getattr(settings, 'MICROSOFT_OAUTH2_CLIENT_SECRET', '')

    def get_user_info(self, access_token):
        """Get user information from Microsoft Graph API"""
        headers = {'Authorization': f'Bearer {access_token}'}
        response = requests.get(self.user_info_url, headers=headers)
        response.raise_for_status()

        data = response.json()

        # Transform to consistent format
        return {
            'email': data.get('mail') or data.get('userPrincipalName'),
            'given_name': data.get('givenName', ''),
            'family_name': data.get('surname', ''),
        }


# Singleton instances
google_oauth = GoogleOAuth2Backend()
microsoft_oauth = MicrosoftOAuth2Backend()
