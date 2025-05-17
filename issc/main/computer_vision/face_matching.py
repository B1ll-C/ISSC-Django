from ..models import FacesEmbeddings
from deepface import DeepFace
import numpy as np
from scipy.spatial.distance import cosine
import ast
import cv2

class FaceMatcher:
    def __init__(self):
        self.embeddings = []
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def load_embeddings(self):
        self.embeddings = []
        for entry in FacesEmbeddings.objects.select_related('id_number').all():
            person_record = {
                "id_number": entry.id_number.id_number,
                "front": np.array(ast.literal_eval(entry.front_embedding), dtype=np.float32),
                "left": np.array(ast.literal_eval(entry.left_embedding), dtype=np.float32),
                "right": np.array(ast.literal_eval(entry.right_embedding), dtype=np.float32),
            }
            self.embeddings.append(person_record)
            print(f"Loaded embeddings for {entry.id_number.id_number}")
        return self.embeddings

    def match(self, live_embedding, threshold=0.9):
        print("Live embedding shape:", live_embedding.shape)
        best_match = None
        lowest_distance = float('inf')

        for person in self.embeddings:
            for pose in ['front', 'left', 'right']:
                stored_embedding = person[pose]
                if stored_embedding is None or len(stored_embedding) == 0:
                    continue
                distance = cosine(live_embedding, stored_embedding)
                if distance < lowest_distance:
                    lowest_distance = distance
                    best_match = person["id_number"]

        if lowest_distance <= threshold:
            return best_match, lowest_distance
        else:
            return None, lowest_distance


