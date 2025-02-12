from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.login, name='login'),
    path("logout/", views.logout, name="logout"),
    path("signup/", views.signup, name='signup'),
    path("signup-forms/", views.signup_forms, name='signup-forms'),


    path("", views.base, name="dashboard"),


    path("incidents/", views.incident, name="incidents"),
    path("incidents/forms", views.incident_forms, name="incident_forms"),
     path('incidents/<int:id>/', views.incident_details, name='incident_details'),

    path("vehicles/", views.vehicles, name="vehicles"),
    path("vehicles/forms", views.vehicle_forms, name="vehicle_forms"),
    path('vehicles/<int:id>/', views.vehicle_details, name='vehicle_details'),

    path("live_feed/", views.live_feed, name="live_feed"),
    path("about/", views.about, name="about"),
    path("face-enrollment/", views.face_enrollment, name="face_enrollment"),
    path("image_test/", views.image_test, name="image_test")
]

