from typing import Dict, Optional
import logging

from core.physics_engine import YogaPhysicsEngine
from core.rule_engine import SuryaNamaskarRuleEngine
from core.safety_engine import SafetyAdaptationEngine, UserProfileManager
from core.correction_engine import YogaCorrectionEngine
from ai.llm_coaching_engine import LLMCoachingEngine
from models.user_profile import UserProfile

logger = logging.getLogger(__name__)


class StatelessSessionManager:
    """Stateless session manager for API requests."""
    
    def __init__(
        self,
        physics_engine: YogaPhysicsEngine,
        rule_engine: SuryaNamaskarRuleEngine,
        safety_engine: SafetyAdaptationEngine,
        correction_engine: YogaCorrectionEngine,
        llm_coaching_engine: Optional[LLMCoachingEngine] = None
    ):
        self.physics_engine = physics_engine
        self.rule_engine = rule_engine
        self.safety_engine = safety_engine
        self.correction_engine = correction_engine
        self.llm_coaching_engine = llm_coaching_engine
    
    def evaluate_pose(
        self,
        pose_name: str,
        angles: Dict[str, float],
        landmarks: Dict[str, list],
        user_profile: UserProfile
    ) -> Dict:
        """
        Evaluate pose without maintaining state.
        
        Args:
            pose_name: Name of the yoga pose
            angles: Joint angles calculated by frontend
            landmarks: 3D landmarks from MediaPipe JS
            user_profile: User profile with level and conditions
            
        Returns:
            Evaluation result dictionary
        """
        try:
            logger.info(f"Evaluating pose: {pose_name} for user level: {user_profile.level}")
            
            # Validate angles
            if not self.physics_engine.validate_angles(angles):
                logger.warning("Invalid angles received")
                return self._error_response("Invalid joint angles")
            
            # Convert landmarks to numpy arrays
            numpy_landmarks = self.physics_engine.convert_landmarks_to_numpy(landmarks)
            
            # Get base rules for pose
            base_rules = self.rule_engine.get_pose_rules(pose_name)
            
            if not base_rules:
                logger.warning(f"No rules found for pose: {pose_name}")
                return self._error_response(f"Pose '{pose_name}' not found")
            
            # Create user profile manager
            user_profile_manager = UserProfileManager(user_profile)
            
            # Adapt rules based on user profile and safety
            safety_result = self.safety_engine.adapt_rules(
                pose_name,
                base_rules,
                user_profile_manager
            )
            
            # Check if pose is allowed
            if not safety_result.get('pose_allowed', True):
                return {
                    "pose_name": pose_name,
                    "pose_detected": True,
                    "alignment_score": 0.0,
                    "issues": ["pose_contraindicated"],
                    "coaching_sentence": safety_result.get('reason', 'This pose is not recommended.'),
                    "risk_level": safety_result.get('risk_level', 'high')
                }
            
            # Evaluate alignment
            adapted_rules = safety_result.get('adapted_rules', base_rules)
            evaluation = self.rule_engine.evaluate_pose(
                pose_name,
                numpy_landmarks,
                angles,
                adapted_rules
            )
            
            issues = evaluation.get('issues', [])
            alignment_score = evaluation.get('alignment_score', 0.0)
            
            # Generate coaching sentence
            coaching_sentence = self._generate_coaching_sentence(pose_name, issues)
            
            return {
                "pose_name": pose_name,
                "pose_detected": True,
                "alignment_score": alignment_score,
                "issues": issues,
                "coaching_sentence": coaching_sentence,
                "risk_level": safety_result.get('risk_level', 'low')
            }
            
        except Exception as e:
            logger.error(f"Error evaluating pose: {e}", exc_info=True)
            return self._error_response("Internal evaluation error")
    
    def _generate_coaching_sentence(self, pose_name: str, issues: list) -> str:
        """Generate natural coaching sentence."""
        if self.llm_coaching_engine:
            try:
                return self.llm_coaching_engine.generate_coaching(
                    pose_name=pose_name,
                    issues=issues,
                    tone="calm"
                )
            except Exception as e:
                logger.error(f"LLM coaching error: {e}")
                # Fallback to rule-based
                return self._fallback_coaching(pose_name, issues)
        else:
            return self._fallback_coaching(pose_name, issues)
    
    def _fallback_coaching(self, pose_name: str, issues: list) -> str:
        """Fallback rule-based coaching."""
        if not issues:
            return "Excellent alignment. Maintain steady breathing."
        
        corrections = self.correction_engine.generate_corrections(pose_name, issues)
        verbal_corrections = corrections.get('verbal_corrections', [])
        
        if verbal_corrections:
            return " ".join(verbal_corrections[:2])  # Limit to 2 corrections
        
        return "Focus on your alignment and breathing."
    
    def _error_response(self, message: str) -> Dict:
        """Generate error response."""
        return {
            "pose_name": "unknown",
            "pose_detected": False,
            "alignment_score": 0.0,
            "issues": ["evaluation_error"],
            "coaching_sentence": message,
            "risk_level": "medium"
        }