from django.urls import path
from .public_views import PublicRestaurantDetailView, PublicRestaurantListView
from apps.clinical.public_views import PublicAdvisoryListView

app_name = "public_restaurants"

urlpatterns = [
    path("restaurants/", PublicRestaurantListView.as_view(), name="list"),
    path("restaurants/<int:pk>/", PublicRestaurantDetailView.as_view(), name="detail"),
    path("advisories/", PublicAdvisoryListView.as_view(), name="advisories"),
]
