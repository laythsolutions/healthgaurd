from django.urls import path
from . import views

app_name = "recalls"

urlpatterns = [
    path("", views.RecallListView.as_view(), name="list"),
    path("<int:pk>/", views.RecallDetailView.as_view(), name="detail"),
    path("acknowledgments/", views.RecallAcknowledgmentView.as_view(), name="acknowledgments"),
    path("acknowledgments/<int:pk>/", views.RecallAcknowledgmentDetailView.as_view(), name="acknowledgment-detail"),
]
