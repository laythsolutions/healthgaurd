"""Alert delivery handlers for SMS, Email, Push, and Webhooks"""

import logging
from typing import Optional, Dict, List
from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone

from .models import Alert, NotificationLog, AlertRule

logger = logging.getLogger(__name__)


class BaseNotificationDelivery:
    """Base class for notification delivery"""

    def __init__(self):
        self.enabled = True

    def send(self, alert: Alert, recipient: str, **kwargs) -> NotificationLog:
        """Send notification and create log"""
        if not self.enabled:
            return self._create_log(alert, 'FAILED', recipient, error="Delivery method disabled")

        try:
            result = self._deliver(alert, recipient, **kwargs)
            return self._create_log(alert, 'SENT', recipient, external_id=result)
        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return self._create_log(alert, 'FAILED', recipient, error=str(e))

    def _deliver(self, alert: Alert, recipient: str, **kwargs) -> str:
        """Actual delivery implementation - returns external ID"""
        raise NotImplementedError

    def _create_log(self, alert: Alert, status: str, recipient: str,
                   external_id: str = '', error: str = '') -> NotificationLog:
        """Create notification log entry"""
        return NotificationLog.objects.create(
            alert=alert,
            notification_type=self.notification_type,
            recipient=recipient,
            subject=getattr(self, '_subject', ''),
            message=getattr(self, '_message', ''),
            status=status,
            sent_at=timezone.now() if status == 'SENT' else None,
            external_id=external_id,
            error_message=error
        )


class SMSDelivery(BaseNotificationDelivery):
    """SMS delivery via Twilio"""

    notification_type = NotificationLog.NotificationType.SMS

    def __init__(self):
        super().__init__()
        try:
            from twilio.rest import Client
            self.client = Client(
                settings.TWILIO_ACCOUNT_SID,
                settings.TWILIO_AUTH_TOKEN
            )
            self.from_number = settings.TWILIO_PHONE_NUMBER
            self.enabled = True
        except ImportError:
            logger.warning("Twilio not installed - SMS delivery disabled")
            self.enabled = False
        except AttributeError:
            logger.warning("Twilio credentials not configured - SMS delivery disabled")
            self.enabled = False

    def _deliver(self, alert: Alert, recipient: str, **kwargs) -> str:
        """Send SMS via Twilio"""
        # Format phone number
        phone_number = self._format_phone_number(recipient)

        # Build message
        message = self._build_sms_message(alert)

        # Send
        message_obj = self.client.messages.create(
            body=message,
            from_=self.from_number,
            to=phone_number
        )

        logger.info(f"SMS sent to {phone_number}: {message_obj.sid}")
        return message_obj.sid

    def _format_phone_number(self, phone: str) -> str:
        """Format phone number for Twilio"""
        # Remove all non-numeric characters
        cleaned = ''.join(c for c in phone if c.isdigit())

        # Add +1 if US number without country code
        if len(cleaned) == 10:
            cleaned = '1' + cleaned

        return '+' + cleaned

    def _build_sms_message(self, alert: Alert) -> str:
        """Build SMS message (max 160 chars)"""
        emoji_map = {
            'CRITICAL': '🚨',
            'WARNING': '⚠️',
            'INFO': 'ℹ️'
        }

        emoji = emoji_map.get(alert.severity, '')
        restaurant = alert.restaurant.name

        # Keep it under 160 chars
        msg = f"{emoji} {restaurant}: {alert.title}"

        if len(msg) > 140:
            msg = msg[:137] + '...'

        return msg


class EmailDelivery(BaseNotificationDelivery):
    """Email delivery via SendGrid"""

    notification_type = NotificationLog.NotificationType.EMAIL

    def __init__(self):
        super().__init__()
        try:
            import sendgrid
            from sendgrid.helpers.mail import Mail, Email, To, Content

            self.sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
            self.Mail = Mail
            self.Email = Email
            self.To = To
            self.Content = Content
            self.from_email = settings.SENDGRID_FROM_EMAIL
            self.from_name = settings.SENDGRID_FROM_NAME
            self.enabled = True
        except ImportError:
            logger.warning("SendGrid not installed - Email delivery disabled")
            self.enabled = False
        except AttributeError:
            logger.warning("SendGrid credentials not configured - Email delivery disabled")
            self.enabled = False

    def _deliver(self, alert: Alert, recipient: str, **kwargs) -> str:
        """Send email via SendGrid"""
        # Build email content
        subject = self._build_subject(alert)
        html_content = self._build_html_content(alert, recipient)
        text_content = self._build_text_content(alert)

        # Create email
        message = self.Mail(
            from_email=self.Email(self.from_email, self.from_name),
            to_emails=To(recipient),
            subject=subject,
            html_content=self.Content("text/html", html_content),
            plain_text_content=self.Content("text/plain", text_content)
        )

        # Send
        response = self.sg.send(message)

        logger.info(f"Email sent to {recipient}: {response.headers.get('X-Message-Id')}")
        return response.headers.get('X-Message-Id', '')

    def _build_subject(self, alert: Alert) -> str:
        """Build email subject"""
        severity_prefix = {
            'CRITICAL': '🚨 CRITICAL: ',
            'WARNING': '⚠️ WARNING: ',
            'INFO': 'ℹ️ '
        }
        prefix = severity_prefix.get(alert.severity, '')
        return f"{prefix}{alert.restaurant.name} - {alert.title}"

    def _build_html_content(self, alert: Alert, recipient: str) -> str:
        """Build HTML email content"""
        context = {
            'alert': alert,
            'restaurant': alert.restaurant,
            'recipient': recipient,
            'severity_color': self._get_severity_color(alert.severity),
            'action_url': self._build_action_url(alert),
        }

        return render_to_string('alerts/alert_email.html', context)

    def _build_text_content(self, alert: Alert) -> str:
        """Build plain text email content"""
        return f"""{alert.title}

Restaurant: {alert.restaurant.name}
Severity: {alert.severity}

{alert.message}

---
View this alert: {self._build_action_url(alert)}
Manage notifications: Settings > Notifications
"""

    def _get_severity_color(self, severity: str) -> str:
        """Get color for severity"""
        colors = {
            'CRITICAL': '#dc2626',
            'WARNING': '#f59e0b',
            'INFO': '#3b82f6'
        }
        return colors.get(severity, '#6b7280')

    def _build_action_url(self, alert: Alert) -> str:
        """Build URL to view/acknowledge alert"""
        base_url = settings.FRONTEND_URL
        return f"{base_url}/alerts/{alert.id}"


class PushDelivery(BaseNotificationDelivery):
    """Push notification delivery via Firebase Cloud Messaging"""

    notification_type = NotificationLog.NotificationType.PUSH

    def __init__(self):
        super().__init__()
        try:
            from firebase_admin import messaging, get_app
            # Check if Firebase is initialized
            try:
                get_app()
            except ValueError:
                # Initialize Firebase
                import firebase_admin
                from firebase_admin import credentials
                cred = credentials.Certificate(settings.FIREBASE_SERVICE_ACCOUNT_KEY_PATH)
                firebase_admin.initialize_app(cred)

            self.messaging = messaging
            self.enabled = True
        except ImportError:
            logger.warning("Firebase Admin not installed - Push delivery disabled")
            self.enabled = False
        except AttributeError:
            logger.warning("Firebase not configured - Push delivery disabled")
            self.enabled = False

    def _deliver(self, alert: Alert, recipient: str, **kwargs) -> str:
        """Send push notification via FCM"""
        # recipient is the FCM token
        token = recipient

        # Build notification
        notification = self.messaging.Message(
            notification=self.messaging.Notification(
                title=self._build_title(alert),
                body=alert.message,
            ),
            data={
                'alert_id': str(alert.id),
                'restaurant_id': str(alert.restaurant.id),
                'severity': alert.severity,
                'type': alert.alert_type,
                'action_url': f"/alerts/{alert.id}",
            },
            token=token,
        )

        # Send
        response = self.messaging.send(notification)

        logger.info(f"Push notification sent: {response}")
        return response

    def _build_title(self, alert: Alert) -> str:
        """Build notification title"""
        return f"{alert.restaurant.name}: {alert.title}"


class WebhookDelivery(BaseNotificationDelivery):
    """Webhook delivery for third-party integrations"""

    notification_type = NotificationLog.NotificationType.WEBHOOK

    def __init__(self):
        super().__init__()
        import requests
        self.requests = requests
        self.enabled = True

    def _deliver(self, alert: Alert, recipient: str, **kwargs) -> str:
        """Send webhook POST request"""
        # recipient is the webhook URL
        url = recipient

        # Build payload
        payload = self._build_payload(alert)

        # Add signature if secret is configured
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': f'HealthGuard-Webhook/1.0'
        }

        secret = kwargs.get('webhook_secret')
        if secret:
            import hmac
            import hashlib
            signature = hmac.new(
                secret.encode(),
                str(payload).encode(),
                hashlib.sha256
            ).hexdigest()
            headers['X-HealthGuard-Signature'] = signature

        # Send
        response = self.requests.post(url, json=payload, headers=headers, timeout=10)
        response.raise_for_status()

        logger.info(f"Webhook sent to {url}: {response.status_code}")
        return str(response.status_code)

    def _build_payload(self, alert: Alert) -> dict:
        """Build webhook payload"""
        return {
            'id': str(alert.id),
            'type': alert.alert_type,
            'severity': alert.severity,
            'status': alert.status,
            'title': alert.title,
            'message': alert.message,
            'restaurant': {
                'id': str(alert.restaurant.id),
                'name': alert.restaurant.name,
                'address': alert.restaurant.address,
            },
            'device': {
                'id': str(alert.device.id) if alert.device else None,
                'device_id': alert.device.device_id if alert.device else None,
                'type': alert.device.device_type if alert.device else None,
            } if alert.device else None,
            'data': {
                'temperature': float(alert.temperature) if alert.temperature else None,
                'threshold_min': float(alert.threshold_min) if alert.threshold_min else None,
                'threshold_max': float(alert.threshold_max) if alert.threshold_max else None,
            },
            'timestamps': {
                'created': alert.created_at.isoformat(),
                'acknowledged': alert.acknowledged_at.isoformat() if alert.acknowledged_at else None,
                'resolved': alert.resolved_at.isoformat() if alert.resolved_at else None,
            },
            'urls': {
                'view': f"{settings.FRONTEND_URL}/alerts/{alert.id}",
                'acknowledge': f"{settings.API_URL}/api/v1/alerts/{alert.id}/acknowledge/",
            }
        }


class NotificationDispatcher:
    """Main dispatcher for routing notifications to appropriate delivery methods"""

    def __init__(self):
        self.delivery_methods = {
            'sms': SMSDelivery(),
            'email': EmailDelivery(),
            'push': PushDelivery(),
            'webhook': WebhookDelivery(),
        }

    def send_alert(self, alert: Alert, methods: List[str] = None, recipients: Dict[str, List[str]] = None):
        """
        Send alert via specified methods to specified recipients

        Args:
            alert: Alert to send
            methods: List of delivery methods (sms, email, push, webhook)
            recipients: Dict mapping method to list of recipients
                e.g., {'email': ['user@example.com'], 'sms': ['+15551234567']}

        Returns:
            Dict mapping method to list of NotificationLog objects
        """
        if methods is None:
            methods = alert.notification_methods or ['email']

        if recipients is None:
            recipients = self._get_default_recipients(alert)

        results = {}

        for method in methods:
            if method not in self.delivery_methods:
                logger.warning(f"Unknown delivery method: {method}")
                continue

            delivery = self.delivery_methods[method]
            method_recipients = recipients.get(method, [])

            if not method_recipients:
                logger.warning(f"No recipients for method: {method}")
                continue

            results[method] = []
            for recipient in method_recipients:
                log = delivery.send(alert, recipient)
                results[method].append(log)

        # Update alert notification tracking
        if results:
            alert.notification_sent = True
            alert.notification_sent_at = timezone.now()
            alert.save(update_fields=['notification_sent', 'notification_sent_at'])

        return results

    def _get_default_recipients(self, alert: Alert) -> Dict[str, List[str]]:
        """Get default recipients for alert based on restaurant settings"""
        recipients = {
            'email': [],
            'sms': [],
            'push': [],
        }

        # Get restaurant's notification preferences
        # This would be based on restaurant settings or alert rules
        restaurant = alert.restaurant

        # Get users with access to this restaurant
        from apps.accounts.models import User, RestaurantAccess

        # Get manager and admin users for this restaurant
        access_records = RestaurantAccess.objects.filter(
            restaurant=alert.restaurant,
            role__in=['MANAGER', 'ADMIN']
        ).select_related('user')

        for access in access_records:
            user = access.user

            # Check user's notification preferences
            prefs = getattr(user, 'notification_preferences', {})

            # Email
            if prefs.get('email_enabled', True) and alert.severity in prefs.get('email_severities', ['CRITICAL', 'WARNING']):
                recipients['email'].append(user.email)

            # SMS
            if prefs.get('sms_enabled', False) and alert.severity in prefs.get('sms_severities', ['CRITICAL']):
                if user.phone:
                    recipients['sms'].append(user.phone)

            # Push
            if prefs.get('push_enabled', True) and alert.severity in prefs.get('push_severities', ['CRITICAL', 'WARNING']):
                # Get user's FCM tokens
                tokens = [t.token for t in user.push_tokens.filter(is_active=True)]
                recipients['push'].extend(tokens)

        return recipients


# Singleton instance
dispatcher = NotificationDispatcher()
