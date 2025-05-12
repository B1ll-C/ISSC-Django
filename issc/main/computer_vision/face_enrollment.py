import cv2
import numpy as np
from deepface import DeepFace
import hashlib

class FaceEnrollment:
    def __init__(self, model_name='Facenet'):
        self.model_name = model_name
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    
    def detect_faces(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, scaleFactor=1.2, minNeighbors=6, minSize=(60, 60)
        )

        cropped_faces = []
        for (x, y, w, h) in faces:
            cv2.rectangle(image, (x, y), (x + w, y + h), (255, 0, 0), 2)

            face = image[y:y+h, x:x+w]
            cropped_faces.append(face)

        return cropped_faces, image

    def get_face_embedding(self, image):
        try:
            embedding = DeepFace.represent(image, model_name=self.model_name)[0]['embedding']
            return embedding
        except Exception as e:
            print(f"Error in generating face embedding: {e}")
            return None
    