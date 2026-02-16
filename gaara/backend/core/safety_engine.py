import json
import numpy as np
from typing import Dict, List, Optional
from copy import deepcopy


class UserProfileManager:
    """Manages user profile and provides query methods."""
    
    def __init__(self, profile):
        """Initialize with user profile."""
        self.profile = profile
        self._condition_set = set(profile.conditions)
    
    def has_condition(self, condition_name: str) -> bool:
        """Check if user has specific condition."""
        return condition_name.lower().strip() in self._condition_set
    
    def is_beginner(self) -> bool:
        """Check if user is beginner level."""
        return self.profile.level == "beginner"
    
    def is_intermediate(self) -> bool:
        """Check if user is intermediate level."""
        return self.profile.level == "intermediate"
    
    def is_advanced(self) -> bool:
        """Check if user is advanced level."""
        return self.profile.level == "advanced"
    
    def get_conditions(self) -> List[str]:
        """Get list of user conditions."""
        return self.profile.conditions
    
    def get_level(self) -> str:
        """Get user experience level."""
        return self.profile.level


class SafetyAdaptationEngine:
    """Adapts pose rules based on user profile and safety requirements."""
    
    def __init__(self, knowledge_base_path: str):
        """Initialize with knowledge base."""
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        self._init_condition_mappings()
    
    def _load_knowledge_base(self, path: str) -> Dict:
        """Load JSON knowledge base."""
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _init_condition_mappings(self):
        """Initialize condition-specific adaptation rules."""
        self.condition_adaptations = {
            'back_pain': {
                'spine_extension_reduction': 0.20,
                'backbend_reduction': 0.25,
                'forward_bend_reduction': 0.15,
                'hold_duration_max': 8,
                'risk_increase': 1
            },
            'high_bp': {
                'forward_fold_duration_max': 5,
                'inversion_prohibited': True,
                'hold_duration_max': 5,
                'risk_increase': 2
            },
            'heart_ailments': {
                'intensity_reduction': 0.30,
                'hold_duration_max': 5,
                'backbend_reduction': 0.30,
                'risk_increase': 2
            },
            'recent_spinal_surgery': {
                'spine_extension_reduction': 0.50,
                'backbend_reduction': 0.60,
                'forward_bend_reduction': 0.40,
                'twist_reduction': 0.50,
                'risk_increase': 3
            }
        }
        
        self.level_adaptations = {
            'beginner': {
                'angle_tolerance': 10,
                'threshold_relaxation': 0.10
            },
            'intermediate': {
                'angle_tolerance': 5,
                'threshold_relaxation': 0.00
            },
            'advanced': {
                'angle_tolerance': -5,
                'threshold_tightening': 0.05
            }
        }
    
    def _get_pose_data(self, pose_name: str) -> Optional[Dict]:
        """Retrieve pose data from knowledge base."""
        return self.knowledge_base.get(pose_name)
    
    def _check_contraindications(self, pose_data: Dict, user_profile_manager) -> tuple:
        """Check if pose is contraindicated for user."""
        contraindications = pose_data.get('contraindications', [])
        
        for condition in user_profile_manager.get_conditions():
            if condition in contraindications:
                return False, f"Pose contraindicated due to {condition}"
        
        return True, None
    
    def adapt_rules(self, pose_name: str, base_rules: Dict, 
                   user_profile_manager) -> Dict:
        """Adapt pose rules based on user profile and safety requirements."""
        
        pose_data = self._get_pose_data(pose_name)
        
        if not pose_data:
            return {
                "pose_allowed": True,
                "adapted_rules": base_rules,
                "safety_modifications": [],
                "risk_level": "low"
            }
        
        allowed, reason = self._check_contraindications(pose_data, user_profile_manager)
        
        if not allowed:
            return {
                "pose_allowed": False,
                "reason": reason,
                "adapted_rules": {},
                "safety_modifications": [reason],
                "risk_level": "high"
            }
        
        adapted_rules = deepcopy(base_rules)
        safety_modifications = []
        
        # Apply level-based adaptations
        level_adaptation = self.level_adaptations.get(user_profile_manager.get_level(), {})
        angle_tolerance = level_adaptation.get('angle_tolerance', 0)
        
        for key, value in adapted_rules.items():
            if isinstance(value, (int, float)) and 'angle' in key:
                if 'min' in key:
                    adapted_rules[key] = value - angle_tolerance
                else:
                    adapted_rules[key] = value + angle_tolerance
        
        return {
            "pose_allowed": True,
            "adapted_rules": adapted_rules,
            "safety_modifications": safety_modifications,
            "risk_level": "low"
        }