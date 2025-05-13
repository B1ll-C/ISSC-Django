import cv2
import threading
import numpy as np
import hashlib
import time
import os
import base64

from django.views.decorators import gzip
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, render, redirect
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

            _, annotated_frame = face_enrollment.detect_faces(frame)

            _, buffer = cv2.imencode('.jpg', annotated_frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')



def face_video_feed(request):
    return StreamingHttpResponse(generate_face_feed(),
                                  content_type='multipart/x-mixed-replace; boundary=frame')

def handle_base64_image(data):
    format, imgstr = data.split(';base64,')
    img_data = base64.b64decode(imgstr)
    img_array = np.frombuffer(img_data, dtype=np.uint8)
    return cv2.imdecode(img_array, cv2.IMREAD_COLOR)


@login_required(login_url='/login')
def face_enrollment_view(request, id_number):
    user_privilege = AccountRegistration.objects.filter(username=request.user).values()


    user = get_object_or_404(AccountRegistration, id_number=id_number)

    if request.method == "POST":
        front_image = request.POST.get('front_image')
        left_image = request.POST.get('left_image')
        right_image = request.POST.get('right_image')

        if front_image and left_image and right_image:
            try:
                face_enrollment = FaceEnrollment()

                front_img = handle_base64_image(front_image)
                left_img = handle_base64_image(left_image)
                right_img = handle_base64_image(right_image)

                front_faces, _ = face_enrollment.detect_faces(front_img)
                left_faces, _ = face_enrollment.detect_faces(left_img)
                right_faces, _ = face_enrollment.detect_faces(right_img)


                if len(front_faces) == 1:

                    front_face = front_faces[0]
                    left_face = left_faces[0]
                    right_face = right_faces[0]

                    front_embedding = face_enrollment.get_face_embedding(front_face)
                    left_embedding = face_enrollment.get_face_embedding(left_face)
                    right_embedding = face_enrollment.get_face_embedding(right_face)


                    if front_embedding is not None and left_embedding is not None and right_embedding is not None:

                        front_embedding_str = str(front_embedding)
                        left_embedding_str = str(left_embedding)
                        right_embedding_str = str(right_embedding)

                        FacesEmbeddings.objects.create(
                            id_number=user,
                            front_embedding=front_embedding_str,
                            left_embedding=left_embedding_str,
                            right_embedding=right_embedding_str,
                        )


                        return render(request, 'face_enrollment/success_page.html')
                    else:
                        return render(request, 'face_enrollment/error.html', {'message': 'Failed to extract embeddings for one or more images.'})

                else:
                    return render(request, 'face_enrollment/error.html', {'message': 'More than one face detected, please use only one face per image.'})

            except Exception as e:
                return render(request, 'face_enrollment/error.html', {'message': f'Error processing images. : {e}'})

    else:
        return render(request, 'face_enrollment/error.html', {'message': 'Missing image data!'})

    return render(request, 'face_enrollment/faceenrollment.html', {
        'user_role': user_privilege[0]['privilege'],
        'user_data': user,
        'camera_ids': range(5),
    })

@login_required(login_url='/login')
def enrollee_view(request):
    user_privilege = AccountRegistration.objects.filter(username=request.user).values()
    user_data = AccountRegistration.objects.all()

    enrolled_ids = FacesEmbeddings.objects.values_list('id_number', flat=True)

    return render(request, 'face_enrollment/enrollee.html', {
        'user_role': user_privilege[0]['privilege'],
        'user_data': user_data,
        'camera_ids': range(5),
        'enrolled_ids': enrolled_ids,
    })

@login_required(login_url='/login')
def success_page(request):
    user_privilege = AccountRegistration.objects.filter(username=request.user).values()
    return render(request, 'face_enrollment/success_page.html', {
        'user_role': user_privilege[0]['privilege'],
    })

def error_page(request):
    user_privilege = AccountRegistration.objects.filter(username=request.user).values()

    return render(request, 'face_enrollment/error.html', {
        'user_role': user_privilege[0]['privilege'],
    })

