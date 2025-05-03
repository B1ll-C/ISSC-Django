import cv2
import threading
import numpy as np
import hashlib
import time
import os

from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required

from ..models import AccountRegistration, FacesEmbeddings
from ..computer_vision.face_enrollment import FaceEnrollment

from .video_feed_view import face_frame_queue


face_enrollment = FaceEnrollment()

face_cam_index = 1
face_cap = cv2.VideoCapture(face_cam_index)


def generate_face_feed():
    while True:
        if not face_frame_queue.empty():
            frame = face_frame_queue.get()

            # Optional face detection
            # frame = detect_faces(frame)

            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


def face_video_feed(request):
    return StreamingHttpResponse(generate_face_feed(),
                                  content_type='multipart/x-mixed-replace; boundary=frame')


@login_required(login_url='/login')
def face_enrollment_view(request):
    user = get_object_or_404(AccountRegistration, username=request.user.username)


    return render(request, 'face_enrollment/faceenrollment.html', {
        'user_role': user.privilege,
        'user_data': user,
        'camera_ids': range(5),
    })
