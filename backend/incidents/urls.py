from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy
from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("elevators/", views.elevator_list, name="elevator-list"),
    path("report/", views.report_incident, name="report-incident"),
    path("staff/incidents/", views.incident_list, name="incident-list"),
    path("staff/incidents/<int:pk>/", views.incident_detail, name="incident-detail"),
    path("api/v1/incidents/", views.device_incident_api, name="device-incident-api"),
    path("login/", auth_views.LoginView.as_view(template_name="incidents/public/login.html"), name="login"),
    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="incidents/shared/password_change.html",
            success_url=reverse_lazy("password-change-done"),
        ),
        name="password-change",
    ),
    path(
        "password/change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="incidents/shared/password_change_done.html"),
        name="password-change-done",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
]
