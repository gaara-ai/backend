import json
import time
import numpy as np
from typing import Dict, List
from pathlib import Path
from collections import deque
from dataclasses import asdict

from models.pose_evaluation import FrameMetrics
from models.session_metrics import SessionMetrics


class YogaProgressTracker:
    """Tracks yoga practice progress and improvements."""
    
    def __init__(self, storage_path: str = "data/yoga_progress.json"):
        self.storage_path = Path(storage_path)
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.session_id = None
        self.session_start_time = None
        self.frame_metrics_history: deque = deque(maxlen=1000)
        
        self.alignment_scores: List[float] = []
        self.left_angles_history: List[Dict[str, float]] = []
        self.right_angles_history: List[Dict[str, float]] = []
        self.spine_extensions: List[float] = []
        self.poses_performed: set = set()
        
        self.fatigue_window = deque(maxlen=24)
        self.fatigue_detected = False
        
        self.session_history = self._load_history()
    
    def start_session(self):
        """Start a new tracking session."""
        self.session_id = f"session_{int(time.time())}"
        self.session_start_time = time.time()
        
        self.frame_metrics_history.clear()
        self.alignment_scores.clear()
        self.left_angles_history.clear()
        self.right_angles_history.clear()
        self.spine_extensions.clear()
        self.poses_performed.clear()
        self.fatigue_window.clear()
        self.fatigue_detected = False
    
    def update(self, frame_metrics: FrameMetrics):
        """Update tracker with new frame metrics."""
        self.frame_metrics_history.append(frame_metrics)
        self.alignment_scores.append(frame_metrics.alignment_score)
        self.poses_performed.add(frame_metrics.pose_name)
        
        self._track_angles(frame_metrics.joint_angles)
        self._update_fatigue_detection(frame_metrics.alignment_score)
    
    def _track_angles(self, joint_angles: Dict[str, float]):
        """Track left and right joint angles separately."""
        left_angles = {}
        right_angles = {}
        
        for key, value in joint_angles.items():
            if 'left' in key:
                left_angles[key] = value
            elif 'right' in key:
                right_angles[key] = value
        
        if left_angles:
            self.left_angles_history.append(left_angles)
        if right_angles:
            self.right_angles_history.append(right_angles)
        
        if 'spine_angle' in joint_angles:
            spine_extension = 180 - joint_angles['spine_angle']
            self.spine_extensions.append(spine_extension)
    
    def _update_fatigue_detection(self, alignment_score: float):
        """Update fatigue detection based on alignment score trends."""
        self.fatigue_window.append(alignment_score)
        
        if len(self.fatigue_window) >= 24:
            scores = list(self.fatigue_window)
            first_half = np.mean(scores[:12])
            second_half = np.mean(scores[12:])
            
            if first_half > 70 and second_half < first_half - 15:
                self.fatigue_detected = True
    
    def compute_stability(self) -> float:
        """Compute stability score based on angle variance."""
        if len(self.left_angles_history) < 10:
            return 0.0
        
        all_variances = []
        
        for angles_list in [self.left_angles_history[-50:], self.right_angles_history[-50:]]:
            angle_keys = set()
            for angles in angles_list:
                angle_keys.update(angles.keys())
            
            for key in angle_keys:
                values = [angles[key] for angles in angles_list if key in angles]
                if len(values) >= 10:
                    variance = np.var(values)
                    all_variances.append(variance)
        
        if not all_variances:
            return 0.0
        
        avg_variance = np.mean(all_variances)
        stability_score = max(0, 100 - avg_variance)
        
        return round(stability_score, 2)
    
    def compute_symmetry(self) -> float:
        """Compute symmetry score comparing left vs right angles."""
        if not self.left_angles_history or not self.right_angles_history:
            return 0.0
        
        symmetry_diffs = []
        
        for left_angles, right_angles in zip(
            self.left_angles_history[-50:],
            self.right_angles_history[-50:]
        ):
            for left_key, left_value in left_angles.items():
                right_key = left_key.replace('left', 'right')
                
                if right_key in right_angles:
                    diff = abs(left_value - right_angles[right_key])
                    symmetry_diffs.append(diff)
        
        if not symmetry_diffs:
            return 0.0
        
        avg_diff = np.me