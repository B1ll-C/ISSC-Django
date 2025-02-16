import cv2
import os
import numpy as np
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from threading import Thread
from queue import Queue
import time
import signal
import sys
from django.template import loader

from ..models import AccountRegistration, IncidentReport, VehicleRegistration

SAVE_DIR = 'recordings'
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize cameras and frame queues
NUM_CAMERAS = 4
cameras = {i: cv2.VideoCapture(i) for i in range(NUM_CAMERAS)}
frame_queues = {i: Queue(maxsize=10) for i in cameras}
video_writers = {}

running = True

# Video settings
FRAME_WIDTH, FRAME_HEIGHT = 640, 480
FPS = 30
VIDEO_FORMAT = "XVID"

# Initialize video writers for each camera
for cam_id in cameras:
    fourcc = cv2.VideoWriter_fourcc(*VIDEO_FORMAT)
    video_path = os.path.join(SAVE_DIR, f'camera_{cam_id}.avi')
    video_writers[cam_id] = cv2.VideoWriter(video_path, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

def process_with_model(frame):
    return frame

def generate_no_signal_frame():
    """Creates a 'No Signal' frame with a gradient background and warning icon."""
    width, height = FRAME_WIDTH, FRAME_HEIGHT
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    for y in range(height):
        color = (255 - int(255 * y / height), 0, 128)
        frame[y, :] = color

    cv2.putText(frame, "NO SIGNAL", (130, 240), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)
    cv2.circle(frame, (320, 320), 50, (0, 0, 255), -1)
    cv2.putText(frame, "!", (305, 345), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)

    return frame

def capture_frames(camera_id):
    """Captures frames from a camera, stores them in a queue, and saves them to a video file."""
    cap = cameras[camera_id]
    video_writer = video_writers[camera_id]

    while running:
        success, frame = cap.read()

        if not success:
            frame = generate_no_signal_frame()
        else:
            frame = process_with_model(frame)

        # Add frame to the queue if it's not full
        if not frame_queues[camera_id].full():
            frame_queues[camera_id].put(frame)

        # Save frame to the video file
        video_writer.write(frame)

        time.sleep(1 / FPS)  # Control the frame rate

# Start a separate thread for each camera
for cam_id in cameras:
    Thread(target=capture_frames, args=(cam_id,), daemon=True).start()

def generate(camera_id):
    """Fetches frames from the queue and yields them as an HTTP stream."""
    while running:
        if not frame_queues[camera_id].empty():
            frame = frame_queues[camera_id].get()
            _, buffer = cv2.imencode('.jpg', frame)
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

def video_feed(request, camera_id):
    """Serves the video feed for a given camera."""
    camera_id = int(camera_id)

    if camera_id not in cameras:
        return HttpResponse(f"Camera {camera_id} not found", status=404)

    return StreamingHttpResponse(generate(camera_id), content_type='multipart/x-mixed-replace; boundary=frame')

def multiple_streams(request):
    """Renders a page with multiple camera streams."""
    user = AccountRegistration.objects.filter(username=request.user).values()
    template = loader.get_template('live-feed/live-feed.html')

    context = {
        'user_role': user[0]['privilege'],
        'user_data': user[0],
        'camera_ids': list(cameras.keys())
    }
    return HttpResponse(template.render(context, request))

def check_cams(request):
    """Returns the number of available cameras."""
    return HttpResponse(str(len(cameras)))

def handle_exit(signum, frame):
    """Handles graceful shutdown on Ctrl + C."""
    global running
    running = False
    print("\nShutting down... Closing video files.")

    for cam_id in cameras:
        if cameras[cam_id].isOpened():
            cameras[cam_id].release()
        video_writers[cam_id].release()
    
    sys.exit(0)

# Register signal handler for Ctrl + C
signal.signal(signal.SIGINT, handle_exit)
