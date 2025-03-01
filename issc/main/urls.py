from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import (
        auth_view, 
        dashboard_view, 
        incident_view, 
        vehicle_view, 
        live_view, 
        about_view, 
        face_enrollment_view, 
        video_feed_view
    ) 
urlpatterns = [

    path("login/", auth_view.login, name='login'),
    path("logout/", auth_view.logout, name="logout"),
    path("signup/", auth_view.signup, name='signup'),
    path("signup-forms/", auth_view.signup_forms, name='signup-forms'),

    path("account/password-reset/", auth_view.CustomPasswordResetView.as_view(), name="password_reset"),
    # path("account/password-reset/done/", auth_view.CustomPasswordResetDoneView.as_view(), name="password_reset_done"),
    path('account/password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/acc_reset_done.html'), name='password_reset_done'),

    path("account/password-reset-confirm/<uidb64>/<token>/", auth_view.CustomPasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("account/password-reset-complete/", auth_view.CustomPasswordResetCompleteView.as_view(), name="password_reset_complete"),



    path("", dashboard_view.base, name="dashboard"),


    path("incidents/", incident_view.incident, name="incidents"),
    path("incidents/forms", incident_view.incident_forms, name="incident_forms"),
    path('incidents/<int:id>/', incident_view.incident_details, name='incident_details'),

    path("vehicles/", vehicle_view.vehicles, name="vehicles"),
    path("vehicles/forms", vehicle_view.vehicle_forms, name="vehicle_forms"),
    path('vehicles/<int:id>/', vehicle_view.vehicle_details, name='vehicle_details'),


    path('video-feed/<int:camera_id>/', video_feed_view.video_feed, name='video_feed'),
    path('live-feed/', video_feed_view.multiple_streams, name='multiple_streams'),
    path('live-feed/start-record', video_feed_view.start_record, name='start_record'),
    path('live-feed/stop-record', video_feed_view.stop_record, name='stop_record'),
    path('check_cams/', video_feed_view.check_cams, name='check_cams'),
    path('live-feed/archive', video_feed_view.recording_archive, name="recording_archive"),
    path('live-feed/reset', video_feed_view.reset_recordings, name="reset_recordings"),

    path("about/", about_view.about, name="about"),


    path("face-enrollment/", face_enrollment_view.face_enrollment, name="face_enrollment"),
    path("video-feed-face/<int:camera_id>/", face_enrollment_view.video_feed_face, name="video_feed_face"),

   
]

