from django.urls import path

from .views import (
    AdminRegistrationListView,
    AdminRegistrationReviewView,
    BatchDetailView,
    BatchListView,
    JurisdictionRegisterView,
    SubmitInspectionsView,
)

urlpatterns = [
    path("register/",                               JurisdictionRegisterView.as_view(),    name="submission-register"),
    path("inspections/",                            SubmitInspectionsView.as_view(),        name="submission-inspections"),
    path("batches/",                                BatchListView.as_view(),                name="submission-batch-list"),
    path("batches/<int:pk>/",                       BatchDetailView.as_view(),              name="submission-batch-detail"),
    path("admin/registrations/",                    AdminRegistrationListView.as_view(),    name="submission-admin-registrations"),
    path("admin/registrations/<int:pk>/review/",    AdminRegistrationReviewView.as_view(),  name="submission-admin-review"),
]
