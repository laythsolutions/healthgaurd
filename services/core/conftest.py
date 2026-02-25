import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
os.environ.setdefault("DEBUG", "True")
os.environ.setdefault("ANONYMIZATION_SALT", "test-salt-not-for-production")
