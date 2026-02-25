from django.urls import path
from . import views

app_name = "privacy"

urlpatterns = [
    # Consent management
    path(
        "consent/<str:subject_hash>/",
        views.ConsentSummaryView.as_view(),
        name="consent-summary",
    ),
    path(
        "consent/<str:subject_hash>/<str:scope>/",
        views.ConsentScopeView.as_view(),
        name="consent-scope",
    ),
    path(
        "consent/<str:subject_hash>/<str:scope>/history/",
        views.ConsentHistoryView.as_view(),
        name="consent-history",
    ),
    # Audit log
    path("audit/", views.AuditLogView.as_view(), name="audit-log"),
    # Development helper
    path("anonymize/test/", views.AnonymizeTestView.as_view(), name="anonymize-test"),
]
