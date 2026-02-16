import unittest
import numpy as np
from core.physics_engine import YogaPhysicsEngine


class TestPhysicsEngine(unittest.TestCase):
    """Test cases for YogaPhysicsEngine."""
    
    def setUp(self):
        self.engine = YogaPhysicsEngine()
        
        # Mock landmarks
        self.landmarks = {
            'left_shoulder': np.array([0.3, 0.3, 0.0]),
            'right_shoulder': np.array([0.7, 0.3, 0.0]),
            'left_elbow': np.array([0.2, 0.5, 0.0]),
            'right_elbow': np.array([0.8, 0.5, 0.0]),
            'left_wrist': np.array([0.1, 0.7, 0.0]),
            'right_wrist': np.array([0.9, 0.7, 0.0]),
            'left_hip': np.array([0.35, 0.6, 0.0]),
            'right_hip': np.array([0.65, 0.6, 0.0]),
            'left_knee': np.array([0.33, 0.8, 0.0]),
            'right_knee': np.array([0.67, 0.8, 0.0]),
            'left_ankle': np.array([0.32, 1.0, 0.0]),
            'right_ankle': np.array([0.68, 1.0, 0.0]),
            'left_ear': np.array([0.35, 0.15, 0.0]),
            'right_ear': np.array([0.65, 0.15, 0.0])
        }
    
    def test_calculate_angle(self):
        """Test angle calculation."""
        p1 = np.array([1, 0, 0])
        p2 = np.array([0, 0, 0])
        p3 = np.array([0, 1, 0])
        
        angle = self.engine.calculate_angle(p1, p2, p3)
        self.assertAlmostEqual(angle, 90.0, places=1)
    
    def test_compute_joint_angles(self):
        """Test joint angles computation."""
        angles = self.engine.compute_joint_angles(self.landmarks)
        
        self.assertIn('left_knee_angle', angles)
        self.assertIn('right_knee_angle', angles)
        self.assertIn('left_elbow_angle', angles)
        self.assertIn('spine_angle', angles)
        
        # Angles should be between 0 and 180
        for angle in angles.values():
            self.assertGreaterEqual(angle, 0)
            self.assertLessEqual(angle, 180)


if __name__ == '__main__':
    unittest.main()