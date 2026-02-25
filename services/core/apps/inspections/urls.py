from django.urls import path
from . import views

app_name = "inspections"

urlpatterns = [
    path("", views.InspectionListCreateView.as_view(), name="list-create"),
    path("export/", views.InspectionExportView.as_view(), name="export"),
    path("schedule/", views.InspectionScheduleView.as_view(), name="schedule-list"),
    path("schedule/<int:pk>/", views.InspectionScheduleDetailView.as_view(), name="schedule-detail"),
    path("<int:pk>/", views.InspectionDetailView.as_view(), name="detail"),
    path("restaurant/<int:restaurant_id>/", views.RestaurantInspectionHistoryView.as_view(), name="restaurant-history"),
]
