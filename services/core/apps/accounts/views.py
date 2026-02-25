"""Views for accounts app"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings

from .models import RestaurantAccess, APIKey, MFASettings, BackupCode, TrustedDevice
from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    RestaurantAccessSerializer,
    CustomTokenObtainPairSerializer,
)
from .oauth import google_oauth, microsoft_oauth
from .mfa import mfa_manager, MFAVerification
from .password_reset import password_reset_manager
from .api_auth import get_api_key_from_request, SCOPES

User = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    """Custom JWT token view"""
    serializer_class = CustomTokenObtainPairSerializer


class UserViewSet(viewsets.ModelViewSet):
    """ViewSet for User model"""

    queryset = User.objects.select_related('organization').all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        org_id = self.request.query_params.get('organization')
        if org_id:
            queryset = queryset.filter(organization_id=org_id)
        return queryset

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def restaurants(self, request):
        """Get user's accessible restaurants"""
        accesses = RestaurantAccess.objects.filter(user=request.user).select_related('restaurant')
        serializer = RestaurantAccessSerializer(accesses, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Register new user"""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response(
                UserSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # OAuth2 Authentication

    @action(detail=False, methods=['get'], permission_classes=[AllowAny])
    def oauth_url(self, request):
        """Get OAuth2 authorization URL"""
        provider = request.query_params.get('provider', 'google').lower()
        redirect_uri = request.query_params.get('redirect_uri')

        if not redirect_uri:
            return Response(
                {'error': 'redirect_uri parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if provider == 'google':
            backend = google_oauth
        elif provider == 'microsoft':
            backend = microsoft_oauth
        else:
            return Response(
                {'error': 'Invalid provider'},
                status=status.HTTP_400_BAD_REQUEST
            )

        auth_url = backend.get_authorization_url(redirect_uri)

        return Response({
            'authorization_url': auth_url,
            'provider': provider
        })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def oauth_callback(self, request):
        """OAuth2 callback endpoint"""
        provider = request.data.get('provider', 'google').lower()
        code = request.data.get('code')
        redirect_uri = request.data.get('redirect_uri')

        if not code or not redirect_uri:
            return Response(
                {'error': 'code and redirect_uri required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        if provider == 'google':
            backend = google_oauth
        elif provider == 'microsoft':
            backend = microsoft_oauth
        else:
            return Response(
                {'error': 'Invalid provider'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            result = backend.authenticate(code, redirect_uri)

            # Generate JWT tokens for the user
            from rest_framework_simplejwt.tokens import RefreshToken

            refresh = RefreshToken.for_user(result['user'])

            return Response({
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': UserSerializer(result['user']).data,
                'created': result['created']
            })

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    # Password Reset

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def forgot_password(self, request):
        """Request password reset"""
        email = request.data.get('email')

        if not email:
            return Response(
                {'error': 'email parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Get IP and user agent for security
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')

        result = password_reset_manager.create_reset_token(email, ip_address, user_agent)

        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def verify_reset_token(self, request):
        """Verify password reset token"""
        token = request.data.get('token')

        if not token:
            return Response(
                {'error': 'token parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user, error = password_reset_manager.verify_reset_token(token)

        if error:
            return Response({'error': error}, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'valid': True,
            'email': user.email
        })

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def reset_password(self, request):
        """Reset password with token"""
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not token or not new_password:
            return Response(
                {'error': 'token and new_password required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        result = password_reset_manager.reset_password(token, new_password)

        if result['success']:
            return Response(result)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Change password (authenticated)"""
        current_password = request.data.get('current_password')
        new_password = request.data.get('new_password')

        if not current_password or not new_password:
            return Response(
                {'error': 'current_password and new_password required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify current password
        if not request.user.check_password(current_password):
            return Response(
                {'error': 'Current password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Set new password
        request.user.set_password(new_password)
        request.user.save()

        return Response({'message': 'Password changed successfully'})

    # Multi-Factor Authentication

    @action(detail=False, methods=['get'])
    def mfa_status(self, request):
        """Get MFA status"""
        mfa_enabled = mfa_manager.is_mfa_enabled(request.user)

        return Response({
            'enabled': mfa_enabled,
            'requires_setup': mfa_manager.require_mfa_setup(request.user)
        })

    @action(detail=False, methods=['post'])
    def mfa_setup(self, request):
        """Set up MFA - generate secret and QR code"""
        # Generate secret
        secret = mfa_manager.generate_secret()

        # Create or update MFA settings
        mfa_settings, created = MFASettings.objects.get_or_create(
            user=request.user,
            defaults={'totp_secret': secret}
        )

        if not created:
            mfa_settings.totp_secret = secret
            mfa_settings.save()

        # Generate QR code
        qr_code = mfa_manager.create_qr_code(request.user, secret)

        # Generate backup codes
        from .mfa import MFAManager
        backup_codes = MFAManager().generate_backup_codes()

        # Store backup codes
        from .models import BackupCode
        BackupCode.objects.filter(user=request.user).delete()

        for code in backup_codes:
            BackupCode.objects.create(
                user=request.user,
                code_hash=MFAManager().hash_backup_code(code)
            )

        return Response({
            'secret': secret,
            'qr_code': f'data:image/png;base64,{qr_code}',
            'backup_codes': backup_codes
        })

    @action(detail=False, methods=['post'])
    def mfa_verify_setup(self, request):
        """Verify MFA setup during enrollment"""
        token = request.data.get('token')

        if not token:
            return Response(
                {'error': 'token parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            mfa_settings = request.user.mfa_settings
        except MFASettings.DoesNotExist:
            return Response(
                {'error': 'MFA not set up'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verify token
        if mfa_manager.verify_totp(mfa_settings.totp_secret, token):
            mfa_settings.is_enabled = True
            mfa_settings.verified_at = timezone.now()
            mfa_settings.save()

            return Response({
                'success': True,
                'message': 'MFA enabled successfully'
            })

        return Response(
            {'error': 'Invalid verification code'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=['post'])
    def mfa_disable(self, request):
        """Disable MFA"""
        try:
            mfa_settings = request.user.mfa_settings
            mfa_settings.is_enabled = False
            mfa_settings.save()

            return Response({'message': 'MFA disabled'})
        except MFASettings.DoesNotExist:
            return Response(
                {'error': 'MFA not enabled'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['post'])
    def mfa_verify(self, request):
        """Verify MFA token during login"""
        token = request.data.get('token')
        trust_device = request.data.get('trust_device', False)

        if not token:
            return Response(
                {'error': 'token parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        verification = MFAVerification(request.user)
        success, error = verification.verify_code(token)

        if success:
            response_data = {'success': True}

            # Create trusted device if requested
            if trust_device:
                device_token = verification.create_trusted_device()
                response_data['trusted_device_token'] = device_token

            return Response(response_data)

        return Response(
            {'error': error},
            status=status.HTTP_400_BAD_REQUEST
        )

    # API Keys

    @action(detail=False, methods=['get'])
    def api_keys(self, request):
        """List user's API keys"""
        api_keys = APIKey.objects.filter(
            user=request.user,
            is_active=True
        ).order_by('-created_at')

        data = [{
            'id': key.id,
            'name': key.name,
            'key_prefix': key.key_prefix,
            'key_type': key.key_type,
            'scopes': key.scopes,
            'last_used_at': key.last_used_at,
            'expires_at': key.expires_at,
            'created_at': key.created_at,
        } for key in api_keys]

        return Response(data)

    @action(detail=False, methods=['post'])
    def create_api_key(self, request):
        """Create new API key"""
        name = request.data.get('name')
        key_type = request.data.get('key_type', 'PERSONAL')
        scopes = request.data.get('scopes', [])
        expires_days = request.data.get('expires_days')

        if not name:
            return Response(
                {'error': 'name parameter required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calculate expiration
        from datetime import timedelta
        expires_at = None
        if expires_days:
            expires_at = timezone.now() + timedelta(days=expires_days)

        # Generate key
        full_key, key_hash = APIKey.generate_key()

        # Create API key
        api_key = APIKey.objects.create(
            user=request.user,
            name=name,
            key_type=key_type,
            key_prefix=full_key[:10],
            key_hash=key_hash,
            scopes=scopes,
            expires_at=expires_at,
            created_by=request.user
        )

        return Response({
            'id': api_key.id,
            'name': api_key.name,
            'key': full_key,  # Only shown once!
            'key_prefix': api_key.key_prefix,
            'scopes': api_key.scopes,
            'expires_at': api_key.expires_at,
            'message': 'Save this key now. You will not be able to see it again.'
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'])
    def delete_api_key(self, request, pk=None):
        """Delete an API key"""
        try:
            api_key = APIKey.objects.get(id=pk, user=request.user)
            api_key.is_active = False
            api_key.save()

            return Response({'message': 'API key deleted'})
        except APIKey.DoesNotExist:
            return Response(
                {'error': 'API key not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    # Sessions

    @action(detail=False, methods=['get'])
    def sessions(self, request):
        """List user's active sessions"""
        from .models import Session

        sessions = Session.objects.filter(
            user=request.user,
            is_active=True,
            expires_at__gt=timezone.now()
        ).order_by('-last_activity_at')

        data = [{
            'id': session.id,
            'device_info': session.device_info,
            'ip_address': session.ip_address,
            'last_activity_at': session.last_activity_at,
            'created_at': session.created_at,
            'is_current': session.session_key == request.session.session_key if hasattr(request, 'session') else False,
        } for session in sessions]

        return Response(data)

    @action(detail=True, methods=['delete'])
    def revoke_session(self, request, pk=None):
        """Revoke a session"""
        from .models import Session

        try:
            session = Session.objects.get(id=pk, user=request.user)
            session.is_active = False
            session.save()

            return Response({'message': 'Session revoked'})
        except Session.DoesNotExist:
            return Response(
                {'error': 'Session not found'},
                status=status.HTTP_404_NOT_FOUND
            )

    def _get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
