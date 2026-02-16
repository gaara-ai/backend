import json
from typing import Dict, List


class YogaCorrectionEngine:
    """Deterministic correction engine for yoga poses."""
    
    def __init__(self, knowledge_base_path: str):
        """Initialize correction engine with knowledge base."""
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
    
    def _load_knowledge_base(self, path: str) -> Dict:
        """Load JSON knowledge base."""
        with open(path, 'r') as f:
            return json.load(f)
    
    def generate_corrections(self, pose_name: str, issues: List[str]) -> Dict:
        """Generate corrections from biomechanical issues."""
        
        pose_knowledge = self.knowledge_base.get(pose_name)
        
        if not pose_knowledge:
            return {
                "pose_name": pose_name,
                "biomechanical_issues": issues,
                "verbal_corrections": ["Pose not found in knowledge base."],
                "priority_level": "low"
            }
        
        # Handle perfect alignment
        if not issues:
            return {
                "pose_name": pose_name,
                "biomechanical_issues": [],
                "verbal_corrections": ["Excellent alignment. Maintain steady breathing."],
                "priority_level": "low"
            }
        
        # Map issues to corrections
        correction_library = pose_knowledge.get('correction_library', {})
        verbal_corrections = []
        
        for issue in issues:
            if issue in correction_library:
                verbal_corrections.append(correction_library[issue])
        
        return {
            "pose_name": pose_name,
            "biomechanical_issues": issues,
            "verbal_corrections": verbal_corrections,
            "priority_level": "medium" if len(issues) > 2 else "low"
        }