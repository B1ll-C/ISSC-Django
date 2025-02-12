import cv2
import numpy as np
import hashlib
import uuid
import time
from PIL import Image
from io import BytesIO
from deepface import DeepFace
from django.http import StreamingHttpResponse
from main.models import FacesEmbeddings, AccountRegistration

class FaceEnrollment:
    def __init__(self, source=0, duration=10):
        """Initialize webcam and face detector"""
        self.source = source
        self.duration = duration  # Enrollment session time (seconds)
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    def generate_sha256_hash(self, image):
        """Generate SHA-256 hash of the image bytes"""
        img_bytes = BytesIO()
        image.save(img_bytes, format="JPEG")
        return hashlib.sha256(img_bytes.getvalue()).hexdigest()

    def extract_embedding(self, image):
        """Generate a face embedding using DeepFace"""
        np_image = np.array(image)  # Convert PIL image to NumPy array
        embedding = DeepFace.represent(np_image, model_name="VGG-Face")[0]['embedding']
        return embedding

    def enroll_face(self, id_number):
        """Capture video, process face enrollment, and store data"""
        cap = cv2.VideoCapture(self.source)
        start_time = time.time()
        captured_faces = []
        instructions = ["Look straight", "Turn left", "Turn right", "Tilt up", "Tilt down"]
        instruction_index = 0

        while (time.time() - start_time) < self.duration:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(50, 50))

            if len(faces) > 0:
                x, y, w, h = sorted(faces, key=lambda f: f[2] * f[3], reverse=True)[0]
                face_roi = frame[y:y+h, x:x+w]

                # Convert to PIL image
                face_pil = Image.fromarray(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))

                # Generate hash and embedding
                image_hash = self.generate_sha256_hash(face_pil)
                embedding = self.extract_embedding(face_pil)

                # Store captured face data
                captured_faces.append((image_hash, embedding))

            # Display instruction text
            cv2.putText(frame, f"Instruction: {instructions[instruction_index]}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

            # Change instruction every 2 seconds
            if int(time.time() - start_time) % 2 == 0 and instruction_index < len(instructions) - 1:
                instruction_index += 1

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

        cap.release()
        cv2.destroyAllWindows()

        if not captured_faces:
            return {"status": "error", "message": "No face detected during the enrollment session."}

        try:
            user = AccountRegistration.objects.get(id_number=id_number)

            # Store the best face in the database
            best_image_hash, best_embedding = captured_faces[0]

            existing_faces = FacesEmbeddings.objects.filter(image_hash=best_image_hash)
            if existing_faces.exists():
                return {"status": "error", "message": "This face is already enrolled."}

            face_entry = FacesEmbeddings.objects.create(
                face_id=uuid.uuid4(),
                id_number=user,
                embedding=best_embedding,
                image_hash=best_image_hash
            )

            return {"status": "success", "message": "Face enrolled successfully.", "face_id": str(face_entry.face_id)}

        except AccountRegistration.DoesNotExist:
            return {"status": "error", "message": "User ID not found."}

        except Exception as e:
            return {"status": "error", "message": f"An error occurred: {str(e)}"}

