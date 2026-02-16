import numpy as np
from typing import Dict


class YogaPhysicsEngine:
    """
    Physics engine for yoga pose analysis.
    Note: Frontend calculates angles using MediaPipe JS.
    This validates and processes received angles.
    """
    
    def validate_angles(self, angles: Dict[str, float]) -> bool:
        """Validate received joint angles."""
        for angle_name, angle_value in angles.items():
            if not (0 <= angle_value <= 180):
                return False
        return True
    
    def convert_landmarks_to_numpy(self, landmarks: Dict[str, list]) -> Dict[str, np.ndarray]:
        """Convert landmark lists to numpy arrays."""
        numpy_landmarks = {}
        for name, coords in landmarks.items():
            numpy_landmarks[name] = np.array(coords)
        return numpy_landmarks
    
    def compute_additional_metrics(self, landmarks_dict: Dict[str, np.ndarray]) -> Dict[str, float]:
        """Compute additional metrics from landmarks if needed."""
        metrics = {}
        
        # Compute hip-shoulder height difference
        mid_hip = (landmarks_dict['left_hip'] + landmarks_dict['right_hip']) / 2
        mid_shoulder = (landmarks_dict['left_shoulder'] + landmarks_dict['right_shoulder']) / 2
        
        metrics['hip_shoulder_height_diff'] = float(mid_shoulder[1] - mid_hip[1])
        
        return metrics