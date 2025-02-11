from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name='login'),
    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name='signup'),
    path("", views.base, name="dashboard"),
    path("incidents/", views.incident, name="incidents"),
    path("incidents/forms", views.incident_forms, name="incident_forms"),
    path("vehicles/", views.vehicles, name="vehicles"),
    path("vehicles/forms", views.vehicle_forms, name="vehicle_forms"),
    path("live_feed/", views.live_feed, name="live_feed"),
    path("about/", views.about, name="about"),
    path("face-enrollment/", views.face_enrollment, name="face_enrollment"),


]