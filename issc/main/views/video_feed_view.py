import cv2
import numpy as np
from django.http import StreamingHttpResponse, HttpResponse
from django.shortcuts import render
from threading import Thread
from queue import Queue
import time
from django.template import loader


from ..models import AccountRegistration, IncidentReport, VehicleRegistration

# Initialize cameras and frame queues
NUM_CAMERAS = 4
cameras = {i: cv2.VideoCapture(i) for i in range(NUM_CAMERAS)}
frame_queues = {i: Queue(maxsize=10) for i in cameras}
running = True

def process_with_model(frame):
    #add model and annotate
    return frame

def generate_no_signal_frame():
    """Creates a 'No Signal' frame with a gradient background and warning icon."""
    width, height = 640, 480
    frame = np.zeros((height, width, 3), dtype=np.uint8)

    # Generate a purple gradient background
    for y in range(height):
        color = (255 - int(255 * y / height), 0, 128)
        frame[y, :] = color

    # Add 'NO SIGNAL' text
    cv2.putText(frame, "NO SIGNAL", (130, 240), cv2.FONT_HERSHEY_DUPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)

    # Add warning icon
    cv2.circle(frame, (320, 320), 50, (0, 0, 255), -1)
    cv2.putText(frame, "!", (305, 345), cv2.FONT_HERSHEY_SIMPLEX, 2, (255, 255, 255), 4, cv2.LINE_AA)

    return frame


def capture_frames(camera_id):
    """Captures frames from a camera and stores them in a queue for streaming."""
    cap = cameras[camera_id]
    
    while running:
        success, frame = cap.read()

        # If the camera fails, use the 'No Signal' frame
        if not success:
            frame = generate_no_signal_frame()
        else:
            #CODE FOR COMPUTER VISION MODEL| frame = process_with_model(frame)
            frame = process_with_model(frame)            

        # Add frame to the queue if it's not full
        if not frame_queues[camera_id].full():
            frame_queues[camera_id].put(frame)

        time.sleep(0.03)  # Control the frame rate


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
        'user_data':user[0],
        'camera_ids':list(cameras.keys())
    }
    # return render(request, 'live-feed/live-feed.html', {'camera_ids': list(cameras.keys())})
    return HttpResponse(template.render(context,request))


def check_cams(request):
    """Returns the number of available cameras."""
    return HttpResponse(str(len(cameras)))