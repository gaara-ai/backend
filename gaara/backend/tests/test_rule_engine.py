import unittest
import numpy as np
from core.rule_engine import SuryaNamaskarRuleEngine


class TestRuleEngine(unittest.TestCase):
    """Test cases for SuryaNamaskarRuleEngine."""
    
    def setUp(self):
        self.engine = SuryaNamaskarRuleEngine(
            knowledge_base_path="knowledge/surya_namaskar.json"
        )
    
    def test_get_pose_rules(self):
        """Test retrieving pose rules."""
        rules = self.engine.get_pose_rules("parvatasana")
        self.assertIsNotNone(rules)
        self.assertIn('knee_angle_min', rules)
    
    def test_evaluate_pose(self):
        """Test pose evaluation."""
        # Mock data
        landmarks = {}
        joint_angles = {
            'left_knee_angle': 165,
            'right_knee_angle': 168,
            'left_elbow_angle': 172,
            'right_elbow_angle': 175
        }
        rules = {
            'knee_angle_min': 170,
            'elbow_angle_min': 170
        }
        
        result = self.engine.evaluate_pose(
            "parvatasana",
            landmarks,
            joint_angles,
            rules
        )
        
        self.assertIn('issues', result)
        self.assertIn('alignment_score', result)


if __name__ == '__main__':
    unittest.main()