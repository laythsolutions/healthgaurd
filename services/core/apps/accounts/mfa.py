"""Multi-Factor Authentication (TOTP) implementation"""

import pyotp
import qrcode
import io
import base64
from django.contrib.auth import get_user_model
from django.conf import settings
from typing import Tuple, Optional

User = get_user_model()


class MFAManager:
    """Manager for Multi-Factor Authentication operations"""

    def __init__(self):
        self.issuer_name = getattr(settings, 'MFA_ISSUER_NAME', 'HealthGuard')

    def generate_secret(self) -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()

    def create_qr_code(self, user: User, secret: str) -> str:
        """Generate QR code for TOTP setup

        Returns:
            Base64 encoded PNG image
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user.email,
            issuer_name=self.issuer_name
        )

        # Create QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

        return qr_code_base64

    def verify_totp(self, secret: str, token: str, valid_window: int = 1) -> bool:
        """Verify TOTP token

        Args:
            secret: The TOTP secret
            token: The 6-digit token from authenticator app
            valid_window: Number of time windows to allow (default: 1 = ±30 seconds)

        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        return totp.verify(token, valid_window=valid_window)

    def generate_backup_codes(self, count: int = 10) -> list:
        """Generate backup codes for MFA recovery

        Returns:
            List of 10-character backup codes
        """
        import secrets
        return [secrets.token_hex(5).upper() for _ in range(count)]

    def hash_backup_code(self, code: str) -> str:
        """Hash a backup code for storage"""
        import hashlib
        return hashlib.sha256(code.encode()).hexdigest()

    def verify_backup_code(self, user: User, code: str) -> bool:
        """Verify a backup code

        Note: This is a one-time use - code should be marked as used after verification
        """
        from .models import BackupCode

        hashed_code = self.hash_backup_code(code.upper())

        try:
            backup_code = BackupCode.objects.get(
                user=user,
                code_hash=hashed_code,
                is_used=False
            )
            # Mark as used
            backup_code.is_used = True
            backup_code.save()
            return True
        except BackupCode.DoesNotExist:
            return False

    def is_mfa_enabled(self, user: User) -> bool:
        """Check if user has MFA enabled"""
        return hasattr(user, 'mfa_settings') and user.mfa_settings.is_enabled

    def require_mfa_setup(self, user: User) -> bool:
        """Check if user is required to set up MFA

        Based on organization policy or user role
        """
        if not user.organization:
            return False

        # Check organization MFA policy
        org_policy = getattr(user.organization, 'mfa_policy', 'optional')

        if org_policy == 'required':
            return not self.is_mfa_enabled(user)
        elif org_policy == 'required_for_admins':
            return user.role in ['ADMIN', 'MANAGER'] and not self.is_mfa_enabled(user)

        return False


class MFAVerification:
    """MFA verification during login"""

    def __init__(self, user: User):
        self.user = user

    def verify_code(self, code: str) -> Tuple[bool, Optional[str]]:
        """Verify MFA code during login

        Returns:
            (success, error_message)
        """
        if not hasattr(self.user, 'mfa_settings') or not self.user.mfa_settings.is_enabled:
            return True, None

        # Try TOTP verification
        if MFAManager().verify_totp(self.user.mfa_settings.totp_secret, code):
            self.user.mfa_settings.last_verified_at = timezone.now()
            self.user.mfa_settings.save()
            return True, None

        # Try backup code
        if MFAManager().verify_backup_code(self.user, code):
            self.user.mfa_settings.last_verified_at = timezone.now()
            self.user.mfa_settings.save()
            return True, None

        return False, "Invalid verification code"

    def verify_trusted_device(self, device_token: str) -> bool:
        """Verify trusted device token"""
        from .models import TrustedDevice

        try:
            device = TrustedDevice.objects.get(
                user=self.user,
                token=device_token,
                is_active=True
            )
            # Check if still valid
            from django.utils import timezone
            from datetime import timedelta

            if device.expires_at and device.expires_at < timezone.now():
                device.is_active = False
                device.save()
                return False

            return True
        except TrustedDevice.DoesNotExist:
            return False

    def create_trusted_device(self, days_valid: int = 30) -> str:
        """Create a trusted device token

        Returns:
            Device token
        """
        from .models import TrustedDevice
        import secrets
        from datetime import timedelta

        token = secrets.token_urlsafe(32)

        expires_at = timezone.now() + timedelta(days=days_valid)

        TrustedDevice.objects.create(
            user=self.user,
            token=token,
            expires_at=expires_at
        )

        return token


# Singleton instance
mfa_manager = MFAManager()
