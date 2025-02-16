from django.http import HttpResponse, StreamingHttpResponse
from django.template import loader
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators import gzip

from ..models import AccountRegistration, FacesEmbeddings
from ..computer_vision.face_enrollment import FaceEnrollment

import cv2
import threading
import numpy as np
import hashlib
import time  # Track face detection time


class VideoCamera:
    def __init__(self, camera_id=0, user=None):
        self.video = cv2.VideoCapture(camera_id)
        if not self.video.isOpened():
            raise Exception("Could not open camera.")

        self.running = True
        self.face_enrollment = FaceEnrollment()
        self.last_detected_time = None  # Track the time when a face was last seen
        self.face_present = False
        self.frame = None  # Store the latest frame
        self.user = user  # Store the user instance

        threading.Thread(target=self.update, daemon=True).start()

    def __del__(self):
        self.running = False
        self.video.release()

    def get_frame(self):
        if self.frame is not None:
            detected_faces = self.face_enrollment.detect_faces(self.frame)

            if detected_faces:
                if not self.face_present:
                    self.last_detected_time = time.time()  # Start timer when face appears
                    self.face_present = True
                else:
                    elapsed_time = time.time() - self.last_detected_time
                    if elapsed_time >= 5:
                        self.enroll_face(detected_faces)
            else:
                self.face_present = False  # Reset if no face detected

            for (x, y, w, h, _) in detected_faces:
                cv2.rectangle(self.frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            _, jpeg = cv2.imencode('.jpg', self.frame)
            return jpeg.tobytes()
        return None

    def update(self):
        while self.running:
            ret, self.frame = self.video.read()
            if not ret:
                self.running = False
                break

    def enroll_face(self, detected_faces):
        """Enroll face embeddings after 5 seconds of continuous detection."""
        if not self.user:
            return  # Skip enrollment if user is missing

        user_instance = get_object_or_404(AccountRegistration, id_number=self.user.id_number)

        for (_, _, _, _, face) in detected_faces:
            embedding = self.face_enrollment.get_face_embedding(face)
            if embedding is not None:
                embedding_bytes = embedding.tobytes()
                image_hash = hashlib.sha256(embedding_bytes).hexdigest()

                FacesEmbeddings.objects.update_or_create(
                    id_number=user_instance,
                    image_hash=image_hash,
                    defaults={'embedding': embedding_bytes}
                )


def gen(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


@login_required(login_url='/login')
def video_feed_face(request, camera_id):
    """ Stream video feed dynamically for each camera with face detection """
    try:
        user = get_object_or_404(AccountRegistration, username=request.user.username)
        cam = VideoCamera(camera_id=int(camera_id), user=user)
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except Exception as e:
        return HttpResponse(f"Error: {e}")


@gzip.gzip_page
@login_required(login_url='/login')
def face_enrollment(request):
    """ Render face enrollment page with camera options """
    user = get_object_or_404(AccountRegistration, username=request.user.username)

    template = loader.get_template('face_enrollment/face.html')
    context = {
        'user_role': user.privilege,
        'user_data': user,
        'camera_ids': range(1)
    }
    return HttpResponse(template.render(context, request))
