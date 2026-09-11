import os
import joblib
import numpy as np
from typing import List, Dict, Tuple, Any
from app.ai.preprocessing.extract_landmarks import normalize_landmarks
from app.ai.ml.train import MODEL_PATH, train_and_save_model

class GestureClassifier:
    def __init__(self):
        self.model = None
        self._load_model()
        
    def _load_model(self):
        if not os.path.exists(MODEL_PATH):
            print("Gesture model not found. Training model now...")
            self.model = train_and_save_model()
        else:
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception as e:
                print(f"Failed to load model: {e}. Retraining...")
                self.model = train_and_save_model()

    def predict(self, raw_landmarks: List[Dict[str, float]]) -> Tuple[str, float]:
        """
        Takes list of 21 landmark dicts [{'x':, 'y':, 'z':}, ...]
        Returns predicted sign character (e.g., 'A') and confidence percentage (e.g., 95.4).
        """
        if self.model is None:
            self._load_model()

        norm_features = normalize_landmarks(raw_landmarks).reshape(1, -1)
        
        # Predict class and probabilities
        pred_class = self.model.predict(norm_features)[0]
        probs = self.model.predict_proba(norm_features)[0]
        
        # Get maximum probability confidence score
        max_prob_idx = np.argmax(probs)
        confidence = float(probs[max_prob_idx] * 100.0)
        
        # Ensure confidence is well-scaled
        if confidence < 50.0 and pred_class is None:
            pred_class = "Unknown"
            
        return str(pred_class), round(confidence, 2)

gesture_classifier = GestureClassifier()
