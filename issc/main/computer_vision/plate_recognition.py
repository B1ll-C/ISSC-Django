import cv2
import numpy as np
import easyocr
from roboflow import Roboflow

DOWNSCALE_FACTOR = 0.8  # Reduce resolution by 50%

class LicencePlateRecognition:
    def __init__(self, roboflow_api_key, model_name, model_version):
        """
        Initialize the license plate recognizer with a Roboflow model and EasyOCR.
        
        :param roboflow_api_key: API key for Roboflow
        :param model_name: Name of the Roboflow model
        :param model_version: Version of the Roboflow model
        """
        self.rf = Roboflow(api_key=roboflow_api_key)
        self.model = self.rf.workspace().project(model_name).version(model_version).model
        self.reader = easyocr.Reader(['en'])  # Supports English OCR by default
    
    def detect_license_plate(self, frame):
        """Detect plates using a lower-resolution frame for faster processing."""
        small_frame = cv2.resize(frame, (0, 0), fx=DOWNSCALE_FACTOR, fy=DOWNSCALE_FACTOR)
        response = self.model.predict(small_frame, confidence=40, overlap=30).json()

        # Scale bounding boxes back to original size
        plates = []
        for pred in response.get('predictions', []):
            x_min, y_min, x_max, y_max = [int(p / DOWNSCALE_FACTOR) for p in 
                                        (pred['x'] - pred['width'] / 2, pred['y'] - pred['height'] / 2, 
                                        pred['x'] + pred['width'] / 2, pred['y'] + pred['height'] / 2)]
            plates.append((x_min, y_min, x_max, y_max))
        
        return plates
    
    def crop_license_plate(self, frame, bounding_boxes):
        """Crop detected license plates from a video frame."""
        cropped_plates = [frame[y_min:y_max, x_min:x_max] for (x_min, y_min, x_max, y_max) in bounding_boxes]
        return cropped_plates

    
    def recognize_text(self, cropped_images):
        """Extracts text using optimized preprocessing (grayscale + denoising)."""
        texts = []
        for img in cropped_images:
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Denoise the grayscale image (using Non-Local Means Denoising)
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

            # Thresholding to make the image more readable for OCR (optional)
            _, thresh = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Run OCR on the preprocessed image
            text = ' '.join(self.reader.readtext(thresh, detail=0))
            texts.append(text)
        
        return texts

