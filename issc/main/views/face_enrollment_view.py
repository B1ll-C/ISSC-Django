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


class VideoRecorder:
    """ Records a short video and processes it for face enrollment """

    def __init__(self, camera_id=0, user=None, output_path="recorded_video.avi", record_time=5):
        self.video = cv2.VideoCapture(camera_id)
        if not self.video.isOpened():
            raise Exception("Could not open camera.")

        self.running = True
        self.record_time = record_time
        self.user = user
        self.output_path = output_path
        self.enrollment_successful = False

        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.frame_width = int(self.video.get(3))
        self.frame_height = int(self.video.get(4))
        self.out = cv2.VideoWriter(self.output_path, fourcc, 20.0, (self.frame_width, self.frame_height))

        self.recording_thread = threading.Thread(target=self.record, daemon=True)
        self.recording_thread.start()

    def record(self):
        """ Record video without GUI display (for web environment) """
        start_time = time.time()

        while self.running:
            ret, frame = self.video.read()
            if not ret:
                break

            self.out.write(frame)

            if time.time() - start_time >= self.record_time:
                self.running = False
                break

        self.video.release()
        self.out.release()
        self.process_video()

        if self.enrollment_successful:
            recorders[self.user.username] = None

    def process_video(self):
        """ Extract frames and process face enrollment """
        face_enrollment = FaceEnrollment()  
        cap = cv2.VideoCapture(self.output_path)

        detected_faces = []
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            faces = face_enrollment.detect_faces(frame)  # Detect faces in the frame
            detected_faces.extend([face for (_, _, _, _, face) in faces])

        cap.release()
        os.remove(self.output_path)

        print(f"Total faces detected: {len(detected_faces)}")  # Debugging print

        if detected_faces:
            self.enroll_faces(detected_faces)  # Call enroll_faces() for embedding
            self.enrollment_successful = True  # Mark as successful

    def enroll_faces(self, detected_faces):
        """Enroll face embeddings into the database"""
        if not self.user or not detected_faces:
            return  

        user_instance = get_object_or_404(AccountRegistration, id_number=self.user.id_number)

        face_enrollment = FaceEnrollment()  # Instantiate FaceEnrollment
        embeddings = face_enrollment.batch_process_faces(detected_faces)  # Batch process embeddings

        for embedding in embeddings:
            embedding_bytes = embedding.tobytes()
            image_hash = hashlib.sha256(embedding_bytes).hexdigest()

            FacesEmbeddings.objects.create(
                id_number=user_instance,
                image_hash=image_hash,
                embedding=embedding_bytes
            )




# Global dictionary to track user recording instances
recorders = {}


@csrf_exempt
@login_required(login_url='/login')
def start_recording(request):
    """Start recording a short video for face enrollment."""
    if request.method != "POST":
        return JsonResponse({"success": False, "message": "Invalid request method."})

    user = get_object_or_404(AccountRegistration, username=request.user.username)

    if user.username in recorders and recorders[user.username] and recorders[user.username].running:
        return JsonResponse({"message": "Recording already in progress."})

    try:
        recorder = VideoRecorder(camera_id=0, user=user)
        recorders[user.username] = recorder
        recorder.recording_thread.join()  # Ensure recording completes

        if recorder.enrollment_successful:  # ✅ Ensure this is set properly
            return JsonResponse({"redirect": True, "url": "/face-enrollment-success/"})  # Redirect to success page
        
        return JsonResponse({"message": "Recording completed, but face enrollment failed."})
    
    except Exception as e:
        return JsonResponse({"message": f"Error: {str(e)}"})




@gzip.gzip_page
@login_required(login_url='/login')
def face_enrollment(request):
    """ Render face enrollment page with camera options """
    user = get_object_or_404(AccountRegistration, username=request.user.username)

    return render(request, 'face_enrollment/faceenrollment.html', {
        'user_role': user.privilege,
        'user_data': user,
        'camera_ids': range(1)
    })


@login_required(login_url='/login')
def face_terms_agreement(request):
    """ Render face enrollment terms agreement page """
    user = get_object_or_404(AccountRegistration, username=request.user.username)

    return render(request, 'face_enrollment/agreement.html', {
        'user_role': user.privilege,
        'user_data': user,
        'camera_ids': range(1)
    })


@login_required(login_url='/login')
def face_enrollment_success(request):
    """ Render success page when face enrollment is completed """
    return render(request, 'face_enrollment/success.html')



video_capture = cv2.VideoCapture(0)

def generate_frames():
    """Generate frames from webcam with a green bounding box around detected faces"""
    face_enrollment = FaceEnrollment()  # Face detector instance

    while True:
        success, frame = video_capture.read()
        if not success:
            break

        # Detect faces
        detected_faces = face_enrollment.detect_faces(frame)

        for (x, y, w, h, _) in detected_faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)  # Green bounding box

        _, buffer = cv2.imencode('.jpg', frame)
        frame_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')


def video_feed(request):
    """Streaming HTTP response for video feed"""
    return StreamingHttpResponse(generate_frames(), content_type="multipart/x-mixed-replace; boundary=frame")
