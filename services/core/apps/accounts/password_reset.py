"""Password reset functionality"""

import logging
from datetime import timedelta
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.template.loader import render_to_string
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content

from .models import PasswordResetToken

logger = logging.getLogger(__name__)
User = get_user_model()


class PasswordResetManager:
    """Manager for password reset operations"""

    def __init__(self):
        self.token_expiry_hours = getattr(settings, 'PASSWORD_RESET_TOKEN_EXPIRY_HOURS', 24)
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')

    def create_reset_token(self, email: str, ip_address: str = None, user_agent: str = None) -> dict:
        """Create a password reset token for the user

        Args:
            email: User's email address
            ip_address: Request IP address
            user_agent: Request user agent

        Returns:
            dict with success status and message
        """
        try:
            user = User.objects.get(email=email, is_active=True)
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return {
                'success': True,
                'message': 'If an account exists with this email, a password reset link has been sent.'
            }

        # Check if there's a recent unused token
        recent_token = PasswordResetToken.objects.filter(
            user=user,
            used_at__isnull=True,
            created_at__gte=timezone.now() - timedelta(minutes=5)
        ).first()

        if recent_token:
            # Reuse recent token
            token = recent_token
        else:
            # Create new token
            token = PasswordResetToken.objects.create(
                user=user,
                token=PasswordResetToken.generate_token(),
                expires_at=timezone.now() + timedelta(hours=self.token_expiry_hours),
                ip_address=ip_address,
                user_agent=user_agent,
            )

        # Send email
        try:
            self._send_reset_email(user, token)
            logger.info(f"Password reset email sent to {email}")

            # Deactivate any other active tokens for this user
            PasswordResetToken.objects.filter(
                user=user,
                used_at__isnull=True,
            ).exclude(id=token.id).delete()

            return {
                'success': True,
                'message': 'If an account exists with this email, a password reset link has been sent.'
            }

        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
            return {
                'success': False,
                'message': 'Failed to send password reset email. Please try again later.'
            }

    def verify_reset_token(self, token: str) -> tuple:
        """Verify a password reset token

        Returns:
            (user, error_message) - user is None if invalid
        """
        try:
            reset_token = PasswordResetToken.objects.select_related('user').get(
                token=token,
                used_at__isnull=True
            )
        except PasswordResetToken.DoesNotExist:
            return None, 'Invalid or expired reset token'

        if not reset_token.is_valid():
            return None, 'Reset token has expired'

        return reset_token.user, None

    def reset_password(self, token: str, new_password: str) -> dict:
        """Reset user's password using token

        Args:
            token: Password reset token
            new_password: New password

        Returns:
            dict with success status and message
        """
        user, error = self.verify_reset_token(token)

        if error:
            return {
                'success': False,
                'message': error
            }

        # Set new password
        user.set_password(new_password)
        user.save()

        # Mark token as used
        reset_token = PasswordResetToken.objects.get(token=token)
        reset_token.used_at = timezone.now()
        reset_token.save()

        logger.info(f"Password reset completed for {user.email}")

        return {
            'success': True,
            'message': 'Password has been reset successfully. Please log in with your new password.'
        }

    def _send_reset_email(self, user: User, token: PasswordResetToken):
        """Send password reset email via SendGrid"""
        reset_url = f"{self.frontend_url}/auth/reset-password/{token.token}"

        context = {
            'user': user,
            'reset_url': reset_url,
            'expiry_hours': self.token_expiry_hours,
            'support_email': getattr(settings, 'SUPPORT_EMAIL', 'support@healthguard.com'),
        }

        html_content = render_to_string('accounts/password_reset_email.html', context)

        message = Mail(
            from_email=Email(
                getattr(settings, 'SENDGRID_FROM_EMAIL', 'noreply@healthguard.com'),
                'HealthGuard'
            ),
            to_emails=To(user.email),
            subject='Reset Your HealthGuard Password',
            html_content=Content("text/html", html_content)
        )

        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        response = sg.send(message)

        return response


# Singleton instance
password_reset_manager = PasswordResetManager()
