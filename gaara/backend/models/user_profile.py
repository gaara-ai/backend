from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class UserProfile:
    """User profile with experience level and health conditions."""
    user_id: str
    name: str
    level: str  # beginner, intermediate, advanced
    conditions: List[str] = field(default_factory=list)
    age: Optional[int] = None
    flexibility_score: Optional[int] = None
    goals: List[str] = field(default_factory=list)