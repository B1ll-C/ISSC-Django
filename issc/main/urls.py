from django.urls import path
from . import views
from .views import auth_view, dashboard_view, incident_view, vehicle_view, live_view, about_view, face_enrollment_view, video_feed_view
urlpatterns = [

    path("login/", auth_view.login, name='login'),
    path("logout/", auth_view.logout, name="logout"),
    path("signup/", auth_view.signup, name='signup'),
    path("signup-forms/", auth_view.signup_forms, name='signup-forms'),


    path("", dashboard_view.base, name="dashboard"),


    path("incidents/", incident_view.incident, name="incidents"),
    path("incidents/forms", incident_view.incident_forms, name="incident_forms"),
    path('incidents/<int:id>/', incident_view.incident_details, name='incident_details'),

    path("vehicles/", vehicle_view.vehicles, name="vehicles"),
    path("vehicles/forms", vehicle_view.vehicle_forms, name="vehicle_forms"),
    path('vehicles/<int:id>/', vehicle_view.vehicle_details, name='vehicle_details'),


    path('video-feed/<int:camera_id>/', video_feed_view.video_feed, name='video_feed'),


    path('live-feed/', video_feed_view.multiple_streams, name='multiple_streams'),
    path('check_cams/', video_feed_view.check_cams, name='check_cams'),

    path("about/", about_view.about, name="about"),


    path("face-enrollment/", face_enrollment_view.face_enrollment, name="face_enrollment"),
    path("video-feed-face/<int:camera_id>/", face_enrollment_view.video_feed_face, name="video_feed_face"),

   
]

