import cv2
from django.http import StreamingHttpResponse


class VideoCamera:
    def __init__(self):
        self.video = cv2.VideoCapture(0)  # Open default webcam (0)

    def __del__(self):
        self.video.release()

    def get_frame(self):
        success, frame = self.video.read()
        if not success:
            return None
        _, jpeg = cv2.imencode('.jpg', frame)
        return jpeg.tobytes()

def generate_frames(camera):
    while True:
        frame = camera.get_frame()
        if frame:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    return StreamingHttpResponse(generate_frames(VideoCamera()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')
