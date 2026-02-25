from django.apps import AppConfig


class PrivacyConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.privacy"
    verbose_name = "Privacy & Consent"

    def ready(self):
        from apps.privacy.classification import register_defaults
        register_defaults()
