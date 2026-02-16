import json
import numpy as np
from typing import Dict, List, Optional


class SuryaNamaskarRuleEngine:
    """Rule engine for Surya Namaskar pose evaluation."""
    
    def __init__(self, knowledge_base_path: str):
        """Initialize rule engine with JSON knowledge base."""
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
    
    def _load_knowledge_base(self, path: str) -> Dict:
        """Load JSON knowledge base."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def get_pose_rules(self, pose_name: str) -> Dict:
        """Extract alignment rules for specific pose."""
        surya_namaskar = self.knowledge_base.get('surya_namaskar', {})
        sequence = surya_namaskar.get('chakras', {}).get('sequence', [])
        
        for pose in sequence:
            if pose['asana'] == pose_name:
                # Return default rules for the pose
                return self._get_default_rules(pose_name)
        
        return {}
    
    def _get_default_rules(self, pose_name: str) -> Dict:
        """Get default alignment rules for pose."""
        rules_map = {
            'parvatasana': {
                'knee_angle_min': 170,
                'elbow_angle_min': 170,
                'hip_height_above_shoulder': True,
                'heel_height_max': 0.05
            },
            'hasta_uttanasana': {
                'elbow_angle_min': 165,
                'spine_extension_min': 10,
                'arms_overhead': True
            },
            'bhujangasana': {
                'elbow_angle_min': 150,
                'spine_extension_min': 15,
                'pelvis_grounded': True
            },
            'ashwa_sanchalanasana': {
                'front_knee_angle_min': 80,
                'front_knee_angle_max': 110,
                'back_knee_angle_min': 160,
                'spine_extension_min': 10
            },
            'pranamasana': {
                'spine_vertical': True,
                'feet_together': True
            }
        }
        
        return rules_map.get(pose_name, {})
    
    def identify_pose(self, landmarks_dict: Dict[str, np.ndarray]) -> Optional[str]:
        """Identify current pose from landmarks."""
        # Simple heuristic-based identification
        mid_hip = (landmarks_dict['left_hip'] + landmarks_dict['right_hip']) / 2
        mid_shoulder = (landmarks_dict['left_shoulder'] + landmarks_dict['right_shoulder']) / 2
        
        # Check if hips are higher than shoulders (downward dog)
        if mid_hip[1] < mid_shoulder[1] - 0.1:
            return 'parvatasana'
        
        # Check if arms are raised (raised arms pose)
        if landmarks_dict['left_wrist'][1] < landmarks_dict['left_shoulder'][1] - 0.2:
            return 'hasta_uttanasana'
        
        # Default to pranamasana
        return 'pranamasana'
    
    def evaluate_pose(self, pose_name: str, landmarks_dict: Dict[str, np.ndarray],
                     joint_angles: Dict[str, float], rules: Dict) -> Dict:
        """Evaluate pose against rules."""
        issues = []
        passed_rules = {}
        failed_rules = {}
        total_rules = 0
        passed_count = 0
        
        # Evaluate knee angles
        if 'knee_angle_min' in rules:
            total_rules += 2
            left_knee_pass = joint_angles['left_knee_angle'] >= rules['knee_angle_min']
            right_knee_pass = joint_angles['right_knee_angle'] >= rules['knee_angle_min']
            
            if left_knee_pass and right_knee_pass:
                passed_rules['knees_extended'] = True
                passed_count += 2
            else:
                failed_rules['knees_extended'] = False
                issues.append('knees_bent')
        
        # Evaluate elbow angles
        if 'elbow_angle_min' in rules:
            total_rules += 2
            left_elbow_pass = joint_angles['left_elbow_angle'] >= rules['elbow_angle_min']
            right_elbow_pass = joint_angles['right_elbow_angle'] >= rules['elbow_angle_min']
            
            if left_elbow_pass and right_elbow_pass:
                passed_rules['elbows_extended'] = True
                passed_count += 2
            else:
                failed_rules['elbows_extended'] = False
                issues.append('elbows_bent')
        
        # Evaluate hip height
        if 'hip_height_above_shoulder' in rules and rules['hip_height_above_shoulder']:
            total_rules += 1
            mid_hip = (landmarks_dict['left_hip'] + landmarks_dict['right_hip']) / 2
            mid_shoulder = (landmarks_dict['left_shoulder'] + landmarks_dict['right_shoulder']) / 2
            
            hip_above_shoulder = mid_hip[1] < mid_shoulder[1]
            
            if hip_above_shoulder:
                passed_rules['hip_elevation'] = True
                passed_count += 1
            else:
                failed_rules['hip_elevation'] = False
                issues.append('hips_low')
        
        # Calculate alignment score
        alignment_score = (passed_count / total_rules * 100) if total_rules > 0 else 0
        
        return {
            "issues": issues,
            "alignment_score": round(alignment_score, 2),
            "passed_rules": passed_rules,
            "failed_rules": failed_rules
        }