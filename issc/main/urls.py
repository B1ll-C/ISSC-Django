from django.urls import path
from . import views

urlpatterns = [
    path("", views.base, name="dashboard"),
    path("incidents/", views.incident, name="incidents"),
    path("vehicles/", views.vehicles, name="vehicles"),
    path("live_feed/", views.live_feed, name="live_feed"),
    path("about/", views.about, name="about"),
    path("logout/", views.logout, name="logout"),
]