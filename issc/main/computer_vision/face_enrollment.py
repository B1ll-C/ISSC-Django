import cv2
import numpy as np
import hashlib
import uuid
from PIL import Image
from io import BytesIO
from deepface import DeepFace
from django.http import JsonResponse
from main.models import FacesEmbeddings, AccountRegistration


class FaceEnrollment:
    def __init__(self, source=0):
        """Initialize webcam source and face detector."""
        self.source = source
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def generate_sha256_hash(self, image):
        """Generate SHA-256 hash for image uniqueness."""
        img_bytes = BytesIO()
        image.save(img_bytes, format="JPEG")
        return hashlib.sha256(img_bytes.getvalue()).hexdigest()

    def extract_embedding(self, image):
        """Extract face embedding using DeepFace."""
        np_image = np.array(image)
        return DeepFace.represent(np_image, model_name="VGG-Face")[0]['embedding']

    def capture_frame(self):
        """Capture a frame from the webcam."""
        cap = cv2.VideoCapture(self.source)
        ret, frame = cap.read()
        cap.release()

        if not ret:
            return None, "Failed to capture image."
        
        return frame, None

    def detect_face(self, frame):
        """Detect the largest face in the frame and draw a bounding box."""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

        if len(faces) == 0:
            return None, "No face detected! Try again."
        
        # Select the largest face detected
        x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]

        # Draw bounding box on the frame
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Convert face region to PIL format
        face_roi = frame[y:y+h, x:x+w]
        face_pil = Image.fromarray(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))
        
        return face_pil, frame, None  # Return both cropped face and full frame with bounding box

    def enroll_face(self, id_number):
        """Capture, process, and store the user's face embedding."""
        try:
            frame, error = self.capture_frame()
            if error:
                return JsonResponse({"status": "error", "message": error})

            face_pil, frame_with_box, error = self.detect_face(frame)
            if error:
                return JsonResponse({"status": "warning", "message": error})

            # Generate hash and embedding
            image_hash = self.generate_sha256_hash(face_pil)
            embedding = self.extract_embedding(face_pil)

            # Check if user exists
            user = AccountRegistration.objects.get(id_number=id_number)

            # Prevent duplicate face enrollment
            if FacesEmbeddings.objects.filter(image_hash=image_hash).exists():
                return JsonResponse({"status": "error", "message": "This face is already enrolled."})

            # Store face data in DB
            face_entry = FacesEmbeddings.objects.create(
                face_id=uuid.uuid4(),
                id_number=user,
                embedding=embedding,
                image_hash=image_hash
            )

            # Convert processed frame with bounding box to base64 (for rendering in HTML)
            _, buffer = cv2.imencode('.jpg', frame_with_box)
            frame_base64 = BytesIO(buffer).getvalue()

            return JsonResponse({
                "status": "success",
                "message": "Face enrolled successfully!",
                "face_id": str(face_entry.face_id),
                "frame": frame_base64.decode('latin1')  # Send image to frontend
            })

        except AccountRegistration.DoesNotExist:
            return JsonResponse({"status": "error", "message": "User ID not found."})

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
