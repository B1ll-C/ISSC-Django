from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="dashboard"),
    path("incidents/", views.index, name="incidents"),
    path("vehicles/", views.index, name="vehicles"),
    path("live_feed/", views.index, name="live_feed"),
    path("about/", views.index, name="about"),
    path("logout/", views.index, name="logout"),
]