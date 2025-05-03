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

