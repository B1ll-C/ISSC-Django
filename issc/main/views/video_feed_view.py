import cv2
import os
import numpy as np
from django.http import StreamingHttpResponse, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from threading import Thread
from queue import Queue
import time
import signal
import sys
from django.template import loader
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()

from ..models import AccountRegistration, IncidentReport, VehicleRegistration


import subprocess

from django.conf import settings
import re

# from ..computer_vision.plate_recognition import LicencePlateRecognition
# recognizer = LicencePlateRecognition(os.getenv("ROBOFLOW_API_KEY"), os.getenv("PROJECT_NAME"), "1")   

SAVE_DIR = 'recordings'
os.makedirs(SAVE_DIR, exist_ok=True)

# Initialize cameras and frame queues
NUM_CAMERAS = 4
cameras = {i: cv2.VideoCapture(i) for i in range(NUM_CAMERAS)}
frame_queues = {i: Queue(maxsize=10) for i in cameras}
video_writers = {}

FRAME_SKIP = 5  # Process every 5th frame
frame_count = 0

running = True

# Video settings
FRAME_WIDTH, FRAME_HEIGHT = 640, 480
FPS = 30
VIDEO_FORMAT = "XVID"

recording = False

def initialize_video_writers():
    """Creates new video writers for each camera."""
    global video_writers
    date_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    new_video_writers = {}

    for cam_id in cameras:
        fourcc = cv2.VideoWriter_fourcc(*VIDEO_FORMAT)
        video_path = os.path.join(SAVE_DIR, f'camera_{cam_id}_{date_str}.avi')
        new_video_writers[cam_id] = cv2.VideoWriter(video_path, fourcc, FPS, (FRAME_WIDTH, FRAME_HEIGHT))

    video_writers = new_video_writers  # Replace old video writers

# Initialize video writers at startup
def start_record():
    global recording
    if recording:
        return redirect('multiple_streams')
    else:
        recording = True
        initialize_video_writers()
        return redirect('multiple_streams')

def stop_record(request):
    global recording
    if recording:
        recording = False
        global video_writers

        # Release current video writers
        for cam_id in video_writers:
            video_writers[cam_id].release()



        recordings_dir = os.path.join(settings.BASE_DIR, 'recordings')
        # reencode_avi_to_mp4(recordings_dir)

        return redirect('multiple_streams')

    else:
        return redirect('multiple_streams')

# start_record()
# initialize_video_writers()
def process_with_model(frame):
    """Processes a video frame to detect and recognize license plates efficiently."""
    
    bounding_boxes = recognizer.detect_license_plate(frame)
    
    if not bounding_boxes:
        return frame  

    cropped_plates = recognizer.crop_license_plate(frame, bounding_boxes)
    plate_texts = recognizer.recognize_text(cropped_plates) if cropped_plates else []
    
    for (box, text) in zip(bounding_boxes, plate_texts):
        x_min, y_min, x_max, y_max = box
        cv2.rectangle(frame, (x_min, y_min), (x_max, y_max), (0, 255, 0), 2)
        
        cv2.putText(frame, text, (x_min, y_min - 10), cv2.FONT_HERSHEY_SIMPLEX, 
                    0.9, (0, 0, 255), 2, cv2.LINE_AA)

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
    """Captures frames and skips unnecessary processing to speed up inference."""
    global frame_count
    cap = cameras[camera_id]

    while running:
        success, frame = cap.read()
        if not success:
            frame = generate_no_signal_frame()

        frame_count += 1
        # if frame_count % FRAME_SKIP == 0:  # Only process every 5th frame
            # frame = process_with_model(frame)

        if not frame_queues[camera_id].full():
            frame_queues[camera_id].put(frame)

        if camera_id in video_writers:
            video_writers[camera_id].write(frame)

        time.sleep(1/FPS)


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

def reset_recordings(request):
    """Stops current video recording and starts a new one for each camera."""
    global video_writers

    # Release current video writers
    for cam_id in video_writers:
        video_writers[cam_id].release()



    recordings_dir = os.path.join(settings.BASE_DIR, 'recordings')
    # reencode_avi_to_mp4(recordings_dir)

    # Create new video writers
    # initialize_video_writers()

    return redirect('recording_archive')


def recording_archive(request):
    """Renders the recording archive page with available recordings."""
    user = AccountRegistration.objects.filter(username=request.user).values()

    # Define the recordings directory
    recordings_dir = os.path.join(settings.BASE_DIR, 'recordings')

    filename_pattern = re.compile(r"camera_(\d+)_(\d+)-(\d+)-(\d+)_(\d+-\d+-\d+).mp4")

    categorized_recordings = {}

    if os.path.exists(recordings_dir):
        for filename in os.listdir(recordings_dir):
            match = filename_pattern.match(filename)
            if match:
                cam_id, year, month, day, time = match.groups()

                # Structure: {camera_id: {year: {month: {day: [filenames]}}}}
                categorized_recordings.setdefault(cam_id, {}).setdefault(year, {}).setdefault(month, {}).setdefault(day, []).append(filename)



    template = loader.get_template('live-feed/recording_arcihve.html')
    context = {
        'user_role': user[0]['privilege'],
        'user_data': user[0],
        'categorized_recordings': categorized_recordings,  # Pass the structured data
    }

    return HttpResponse(template.render(context, request))


def handle_exit(signum, frame):
    """Handles graceful shutdown on Ctrl + C."""
    global running
    running = False
    print("\nShutting down... Closing video files.")

    for cam_id in cameras:
        if cameras[cam_id].isOpened():
            cameras[cam_id].release()
        video_writers[cam_id].release()
    
    recordings_dir = os.path.join(settings.BASE_DIR, 'recordings')
    # reencode_avi_to_mp4(recordings_dir)
    
    sys.exit(0)

# Register signal handler for Ctrl + C
signal.signal(signal.SIGINT, handle_exit)


def reencode_avi_to_mp4(directory):
    """Searches for all .avi files in the specified directory, converts them to .mp4 using ffmpeg, and deletes the original .avi files."""
    
    if not os.path.exists(directory):
        print(f"Directory {directory} does not exist.")
        return

    for filename in os.listdir(directory):
        if filename.endswith(".avi"):
            avi_path = os.path.join(directory, filename)
            mp4_path = os.path.join(directory, filename.replace(".avi", ".mp4"))
            
            print(f"Converting {avi_path} to {mp4_path}...")
            
            # FFmpeg command for re-encoding AVI to MP4 (H.264 codec)
            command = [
                "ffmpeg",
                "-i", avi_path,         # Input file
                "-c:v", "libx264",      # Video codec
                "-preset", "fast",      # Encoding speed
                "-crf", "23",           # Quality (lower is better, 23 is default)
                "-c:a", "aac",          # Audio codec
                "-b:a", "128k",         # Audio bitrate
                mp4_path                # Output file
            ]
            
            try:
                subprocess.run(command, check=True)
                print(f"Successfully converted {avi_path} to {mp4_path}")

                # Delete the original .avi file
                os.remove(avi_path)
                print(f"Deleted original file: {avi_path}")

            except subprocess.CalledProcessError as e:
                print(f"Error converting {avi_path}: {e}")