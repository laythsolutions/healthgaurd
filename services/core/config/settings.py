"""
Django settings for HealthGuard Cloud Backend
"""

import os
from datetime import timedelta
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent.parent

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
DEBUG = os.getenv('DEBUG', 'True') == 'True'
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Production safety: refuse to run with insecure defaults when DEBUG is off
if not DEBUG and 'dev' in SECRET_KEY:
    raise RuntimeError(
        "Refusing to start: SECRET_KEY contains 'dev' while DEBUG=False. "
        "Set a strong, unique SECRET_KEY for production."
    )

# Application definition
DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',
    'django_filters',
    'channels',
    # OIDC federation — only loaded when mozilla-django-oidc is installed
    # pip install mozilla-django-oidc
    *(['mozilla_django_oidc'] if __import__('importlib.util', fromlist=['find_spec']).find_spec('mozilla_django_oidc') else []),
]

LOCAL_APPS = [
    'apps.accounts',
    'apps.restaurants',
    'apps.devices',
    'apps.sensors',
    'apps.alerts',
    'apps.analytics',
    'apps.reports',
    'apps.ota',
    # OSFI: new apps
    'apps.privacy',
    'apps.recalls',
    'apps.inspections',
    'apps.clinical',
    # RFC-002: product & transaction data pipeline
    'apps.products',
    # Jurisdiction submission push API
    'apps.submissions',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

AUTH_USER_MODEL = 'accounts.User'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'apps.middleware.SecurityHeadersMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'apps.privacy.audit_middleware.DataAccessAuditMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.middleware.TenantMiddleware',
    'apps.middleware.APIVersionHeaderMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

# Database - TimescaleDB for time-series data
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'healthguard'),
        'USER': os.getenv('DB_USER', 'healthguard'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'dev_password'),
        'HOST': os.getenv('DB_HOST', 'postgres'),
        'PORT': os.getenv('DB_PORT', '5432'),
    },
    'timeseries': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('TIMESCALEDB_NAME', 'healthguard_timeseries'),
        'USER': os.getenv('TIMESCALEDB_USER', 'healthguard'),
        'PASSWORD': os.getenv('TIMESCALEDB_PASSWORD', 'dev_password'),
        'HOST': os.getenv('TIMESCALEDB_HOST', 'timescaledb'),
        'PORT': os.getenv('TIMESCALEDB_PORT', '5432'),
    },
}

# Database routers
DATABASE_ROUTERS = ['config.routers.TimeSeriesRouter']

# Cache - Redis
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.getenv('REDIS_URL', 'redis://redis:6379/1'),
    }
}

# Password validation — minimum 12 characters, not in common list, not all-numeric
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {'min_length': 12},
    },
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# ---------------------------------------------------------------------------
# Security hardening — safe defaults; production values override via env
# ---------------------------------------------------------------------------
X_FRAME_OPTIONS = 'DENY'
SECURE_CONTENT_TYPE_NOSNIFF = True   # Django adds X-Content-Type-Options: nosniff
SECURE_BROWSER_XSS_FILTER = True     # Sets X-XSS-Protection: 1; mode=block (legacy)

# Production-only settings (skipped in DEBUG so local dev works over HTTP)
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000       # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    CSRF_COOKIE_HTTPONLY = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Supported languages — used by Django's LocaleMiddleware and API locale headers
from django.utils.translation import gettext_lazy as _   # noqa: E402
LANGUAGES = [
    ('en', _('English')),
    ('es', _('Spanish')),
    ('zh-hans', _('Simplified Chinese')),
    ('vi', _('Vietnamese')),
    ('ko', _('Korean')),
    ('tl', _('Filipino')),
]
LOCALE_PATHS = [BASE_DIR / 'locale']

# Static files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend',
        'rest_framework.filters.SearchFilter',
        'rest_framework.filters.OrderingFilter',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DATETIME_FORMAT': '%Y-%m-%dT%H:%M:%S%z',
    # Rate limiting — applied per-view using throttle_classes or globally on public endpoints
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.AnonRateThrottle',
        'rest_framework.throttling.UserRateThrottle',
        'rest_framework.throttling.ScopedRateThrottle',
    ],
    'DEFAULT_THROTTLE_RATES': {
        'anon':                '200/hour',   # Unauthenticated public API
        'user':                '2000/hour',  # Authenticated users (health dept etc.)
        'public_data':         '100/hour',   # Stricter tier for /api/v1/public/* endpoints
        'clinical':            '500/day',    # Institution API key submissions
        'burst':               '30/min',     # Burst protection for all anon requests
        'consumer_report':     '3/hour',     # RFC-001: anonymous consumer exposure reports
        # Auth endpoint specific — stricter to block brute-force and enumeration
        'auth_login':          '5/min',      # JWT token obtain (login attempts)
        'auth_register':       '10/hour',    # New account registration
        'auth_password_reset': '3/hour',     # Password-reset email requests
        'auth_mfa':            '10/10min',   # MFA verification attempts per user
        # AI features — Claude API calls are expensive; 20/hour keeps costs bounded
        'ai_operations':       '20/hour',    # Advisory drafting, triage, normalization
        # Jurisdiction submission API
        'submission_bulk':     '10/hour',    # Per-key batch submission limit
        'submission_register': '5/hour',     # Public registration form
    },
}

# JWT Settings
SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

# CORS Settings
CORS_ALLOWED_ORIGINS = os.getenv(
    'CORS_ALLOWED_ORIGINS',
    'http://localhost:3000,http://127.0.0.1:3000'
).split(',')
CORS_ALLOW_CREDENTIALS = True

# Channels (WebSocket)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            'hosts': [(os.getenv('REDIS_HOST', 'redis'), 6379)],
        },
    },
}

# Celery (Background Tasks)
CELERY_BROKER_URL = os.getenv('REDIS_URL', 'redis://redis:6379/2')
CELERY_RESULT_BACKEND = os.getenv('REDIS_URL', 'redis://redis:6379/2')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# MQTT Configuration
MQTT_BROKER = {
    'HOST': os.getenv('MQTT_BROKER_HOST', 'mosquitto'),
    'PORT': int(os.getenv('MQTT_BROKER_PORT', 1883)),
    'KEEPALIVE': 60,
    'QOS': 1,
}

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'apps': {'handlers': ['console'], 'level': 'DEBUG', 'propagate': False},
    },
}

# HealthGuard Specific
COMPLIANCE_RULES = {
    'DANGER_ZONE_TEMP_MIN': 41,  # Fahrenheit
    'DANGER_ZONE_TEMP_MAX': 135,
    'REFRIGERATION_TEMP_MAX': 41,
    'HOT_HOLDING_TEMP_MIN': 135,
    'FREEZER_TEMP_MAX': 0,
}

ALERT_THRESHOLDS = {
    'CRITICAL': 0,  # Immediate alert
    'WARNING': 15,  # 15 minutes
    'INFO': 30,     # 30 minutes
}

# Notification Settings
# Twilio (SMS)
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', '')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', '')
TWILIO_PHONE_NUMBER = os.getenv('TWILIO_PHONE_NUMBER', '')

# SendGrid (Email)
SENDGRID_API_KEY = os.getenv('SENDGRID_API_KEY', '')
SENDGRID_FROM_EMAIL = os.getenv('SENDGRID_FROM_EMAIL', 'alerts@healthguard.com')
SENDGRID_FROM_NAME = os.getenv('SENDGRID_FROM_NAME', 'HealthGuard')

# Firebase Cloud Messaging (Push)
FIREBASE_SERVICE_ACCOUNT_KEY_PATH = os.getenv('FIREBASE_SERVICE_ACCOUNT_KEY_PATH', '')
FCM_SERVER_KEY = os.getenv('FCM_SERVER_KEY', '')

# Webhook Settings
WEBHOOK_TIMEOUT_SECONDS = int(os.getenv('WEBHOOK_TIMEOUT_SECONDS', 10))
WEBHOOK_MAX_RETRIES = int(os.getenv('WEBHOOK_MAX_RETRIES', 3))

# Frontend URLs
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000')
API_URL = os.getenv('API_URL', 'http://localhost:8000')

# OAuth2 Configuration
GOOGLE_OAUTH2_CLIENT_ID = os.getenv('GOOGLE_OAUTH2_CLIENT_ID', '')
GOOGLE_OAUTH2_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH2_CLIENT_SECRET', '')
MICROSOFT_OAUTH2_CLIENT_ID = os.getenv('MICROSOFT_OAUTH2_CLIENT_ID', '')
MICROSOFT_OAUTH2_CLIENT_SECRET = os.getenv('MICROSOFT_OAUTH2_CLIENT_SECRET', '')

# ---------------------------------------------------------------------------
# OIDC Federation — health department SSO (mozilla-django-oidc)
# pip install mozilla-django-oidc
# ---------------------------------------------------------------------------
# RP (Relying Party) credentials — issued by the health dept's IdP
OIDC_RP_CLIENT_ID     = os.getenv('OIDC_RP_CLIENT_ID', '')
OIDC_RP_CLIENT_SECRET = os.getenv('OIDC_RP_CLIENT_SECRET', '')

# OP (OpenID Provider) endpoints — fill in from IdP's discovery document
OIDC_OP_JWKS_ENDPOINT          = os.getenv('OIDC_OP_JWKS_ENDPOINT', '')
OIDC_OP_AUTHORIZATION_ENDPOINT = os.getenv('OIDC_OP_AUTHORIZATION_ENDPOINT', '')
OIDC_OP_TOKEN_ENDPOINT         = os.getenv('OIDC_OP_TOKEN_ENDPOINT', '')
OIDC_OP_USER_ENDPOINT          = os.getenv('OIDC_OP_USER_ENDPOINT', '')

# Algorithm the IdP uses to sign JWTs (RS256 for Azure AD / Okta)
OIDC_RP_SIGN_ALGO = os.getenv('OIDC_RP_SIGN_ALGO', 'RS256')

# Scopes to request (openid + email required; groups for role mapping)
OIDC_RP_SCOPES = os.getenv('OIDC_RP_SCOPES', 'openid email profile groups')

# Redirect users here after successful OIDC login
LOGIN_REDIRECT_URL  = os.getenv('OIDC_LOGIN_REDIRECT_URL', '/portal/')
LOGOUT_REDIRECT_URL = os.getenv('OIDC_LOGOUT_REDIRECT_URL', '/')

# Optional: restrict OIDC login to users from a specific email domain
OIDC_HEALTH_DEPT_DOMAIN = os.getenv('OIDC_HEALTH_DEPT_DOMAIN', '')

# IdP group claim names (customize to match the IdP's token structure)
OIDC_GROUPS_CLAIM     = os.getenv('OIDC_GROUPS_CLAIM', 'groups')
OIDC_INSPECTOR_GROUP  = os.getenv('OIDC_INSPECTOR_GROUP', 'HealthDeptInspector')
OIDC_ADMIN_GROUP      = os.getenv('OIDC_ADMIN_GROUP', 'HealthDeptAdmin')

# Session: re-verify token every 15 minutes
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = int(
    os.getenv('OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS', 900)
)

# Add the OIDC backend only when credentials are configured
if OIDC_RP_CLIENT_ID:
    AUTHENTICATION_BACKENDS = [
        'django.contrib.auth.backends.ModelBackend',
        'apps.accounts.oidc.HealthDeptOIDCBackend',
    ]

# MFA Configuration
MFA_ISSUER_NAME = os.getenv('MFA_ISSUER_NAME', 'HealthGuard')
MFA_REQUIRED_FOR_ADMINS = os.getenv('MFA_REQUIRED_FOR_ADMINS', 'True') == 'True'

# Password Reset
PASSWORD_RESET_TOKEN_EXPIRY_HOURS = int(os.getenv('PASSWORD_RESET_TOKEN_EXPIRY_HOURS', '24'))
SUPPORT_EMAIL = os.getenv('SUPPORT_EMAIL', 'support@healthguard.com')

# ---------------------------------------------------------------------------
# Privacy & Anonymization (OSFI)
# ---------------------------------------------------------------------------
# REQUIRED in production. Generate with:
#   python -c "import secrets; print(secrets.token_hex(32))"
ANONYMIZATION_SALT = os.getenv('ANONYMIZATION_SALT', '')

if not DEBUG and not ANONYMIZATION_SALT:
    raise RuntimeError(
        "ANONYMIZATION_SALT must be set in production. "
        "Generate with: python -c \"import secrets; print(secrets.token_hex(32))\""
    )

# Intelligence service URL (for inspection record ingestion bridge)
INTELLIGENCE_SERVICE_URL = os.getenv('INTELLIGENCE_SERVICE_URL', 'http://intelligence:8001')

# Gateway API key — used by Pi MQTT bridges to push topology snapshots
GATEWAY_API_KEY = os.getenv('GATEWAY_API_KEY', '')

# ---------------------------------------------------------------------------
# AI / LLM — Claude API (Anthropic)
# ---------------------------------------------------------------------------
# Required for: outbreak advisory drafting, consumer report triage
# Generate at: https://console.anthropic.com/
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
# Model used for AI features — claude-sonnet-4-6 balances capability and cost
ANTHROPIC_MODEL = os.getenv('ANTHROPIC_MODEL', 'claude-sonnet-4-6')

# Celery Beat schedule
CELERY_BEAT_SCHEDULE = {
    # Recall feed synchronization
    'sync-fda-recalls-nightly': {
        'task': 'apps.recalls.tasks.sync_fda_recalls',
        'schedule': 60 * 60 * 24,
        'kwargs': {'days_back': 7},
    },
    'sync-usda-recalls-nightly': {
        'task': 'apps.recalls.tasks.sync_usda_recalls',
        'schedule': 60 * 60 * 24,
        'kwargs': {'days_back': 7},
    },
    # Inspection ingest bridge — harvester → core DB
    'ingest-ca-inspections-nightly': {
        'task': 'apps.inspections.tasks.ingest_state_inspections',
        'schedule': 60 * 60 * 24,
        'kwargs': {'state': 'CA', 'days_back': 1},
    },
    'ingest-nyc-inspections-nightly': {
        'task': 'apps.inspections.tasks.ingest_state_inspections',
        'schedule': 60 * 60 * 24,
        'kwargs': {'state': 'NYC', 'days_back': 1},
    },
    'ingest-il-inspections-nightly': {
        'task': 'apps.inspections.tasks.ingest_state_inspections',
        'schedule': 60 * 60 * 24,
        'kwargs': {'state': 'IL', 'days_back': 1},
    },
    # Cluster detection — Year 3
    'run-cluster-detection-daily': {
        'task': 'apps.clinical.tasks.run_cluster_detection',
        'schedule': 60 * 60 * 24,
        'kwargs': {'lookback_days': 30},
    },
    # Recall acknowledgment sweep — runs every 6 hours
    'auto-create-acknowledgments': {
        'task': 'apps.recalls.tasks.auto_create_acknowledgments_for_active',
        'schedule': 60 * 60 * 6,
    },
    # IoT equipment failure risk scoring — nightly
    'device-risk-scoring-nightly': {
        'task': 'apps.devices.tasks.update_device_risk_scores',
        'schedule': 60 * 60 * 24,
    },
    # RFC-001: purge consumer report photos past their 24-hour expiry (hourly)
    'purge-consumer-report-photos-hourly': {
        'task': 'apps.clinical.tasks.purge_consumer_report_photos',
        'schedule': 60 * 60,
    },
    # RFC-002: sync retail transactions from all enabled partners every 6 hours
    'sync-retail-transactions': {
        'task': 'apps.products.tasks.sync_all_retail_partners',
        'schedule': 60 * 60 * 6,
    },
    # RFC-002: nightly purge of transactions past their retention window
    'purge-old-retail-transactions': {
        'task': 'apps.products.tasks.purge_old_transactions',
        'schedule': 60 * 60 * 24,
    },
    # Phase B: IoT anomaly detection — hourly fleet scan
    'iot-anomaly-detection-hourly': {
        'task': 'apps.devices.tasks.detect_fleet_anomalies',
        'schedule': 60 * 60,
    },
}
