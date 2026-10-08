from django.urls import path
from . import views

urlpatterns = [
    path("catalog/", views.CatalogView.as_view()),
    path("availability/", views.AvailabilityView.as_view()),
    path("auth/session/", views.SessionView.as_view()),
    path("auth/register/", views.RegisterView.as_view()),
    path("auth/login/", views.LoginView.as_view()),
    path("auth/logout/", views.LogoutView.as_view()),
    path("appointments/", views.AppointmentsView.as_view()),
    path("appointments/<int:pk>/", views.AppointmentDetailView.as_view()),
    path("appointments/<int:pk>/cancel/", views.CancelAppointmentView.as_view()),
]
