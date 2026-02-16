import unittest
import numpy as np
from unittest.mock import Mock, MagicMock
from app.orchestrator import YogaMasterOrchestrator
from app.dependency_container import SystemDependencies


class TestOrchestrator(unittest.TestCase):
    """Test cases for YogaMasterOrchestrator."""
    
    def setUp(self):
        # Create mock dependencies
        self.deps = Mock(spec=SystemDependencies)
        self.deps.pose_detector = Mock()
        self.deps.physics_engine = Mock()
        self.deps.rule_engine = Mock()
        self.deps.safety_engine = Mock()
        self.deps.correction_engine = Mock()
        self.deps.progress_tracker = Mock()
        self.deps.llm_coaching_engine = None
        self.deps.voice_feedback_manager = None
        
        self.orchestrator = YogaMasterOrchestrator(self.deps)
    
    def test_process_frame_no_detection(self):
        """Test processing when no pose detected."""
        self.deps.pose_detector.detect.return_value = None
        
        frame = np.zeros((480, 640, 3), dtype=np.uint8)
        result = self.orchestrator.process_frame(frame)
        
        self.assertIsNotNone(result)
        self.assertFalse(result.pose_detected)
        self.assertEqual(result.pose_name, "unknown")


if __name__ == '__main__':
    unittest.main()