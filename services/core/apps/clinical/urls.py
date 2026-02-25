from django.urls import path
from . import views

app_name = "clinical"

urlpatterns = [
    path("cases/", views.ClinicalCaseView.as_view(), name="cases"),
    path("cases/<int:pk>/", views.ClinicalCaseDetailView.as_view(), name="case-detail"),
    path("investigations/", views.OutbreakInvestigationView.as_view(), name="investigations"),
    path("investigations/<int:pk>/", views.OutbreakInvestigationDetailView.as_view(), name="investigation-detail"),
    # Analytics endpoints
    path("investigations/<int:pk>/stats/", views.InvestigationStatsView.as_view(), name="investigation-stats"),
    path("investigations/<int:pk>/traceback/", views.InvestigationTracebackView.as_view(), name="investigation-traceback"),
    path("stats/geohash/", views.GeohashStatsView.as_view(), name="geohash-stats"),
]
