import cv2
import numpy as np
from deepface import DeepFace

class FaceEnrollment:
    def __init__(self, model_name='Facenet'):
        self.model_name = model_name
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_faces(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        
        detected_faces = []
        for (x, y, w, h) in faces:
            face = image[y:y+h, x:x+w]
            detected_faces.append((x, y, w, h, face))
        
        return detected_faces
    
    def get_face_embedding(self, face_image):
        embedding = DeepFace.represent(face_image, model_name=self.model_name, enforce_detection=False)
        return np.array(embedding[0]['embedding'])
    
    def batch_process_faces(self, face_images):
        embeddings = []
        for face in face_images:  # Process each face separately
            try:
                embedding = DeepFace.represent(face, model_name=self.model_name, enforce_detection=False)
                embeddings.append(np.array(embedding[0]['embedding']))  # Extract and convert to numpy array
            except Exception as e:
                print(f"Error processing face: {e}")  # Debugging
                continue
        return embeddings

