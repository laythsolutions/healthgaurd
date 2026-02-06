"""App config for restaurants"""

from django.apps import AppConfig


class RestaurantsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.restaurants'
    verbose_name = 'Restaurants & Locations'

    def ready(self):
        import apps.restaurants.signals
