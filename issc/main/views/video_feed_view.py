import cv2
from django.http import StreamingHttpResponse
from django.shortcuts import render

class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, image = self.video.read()
        if success:
            _, jpeg = cv2.imencode('.jpg', image)
            return jpeg.tobytes()
        return None

def generate(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    return StreamingHttpResponse(generate(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')
