from pydantic import BaseModel
from typing import List, Optional, Dict


class UserProfileSchema(BaseModel):
    """User profile schema."""
    user_id: str
    name: str
    level: str
    conditions: List[str] = []
    age: Optional[int] = None


class SessionStartRequest(BaseModel):
    """Session start request."""
    user_profile: Optional[UserProfileSchema] = None


class SessionStartResponse(BaseModel):
    """Session start response."""
    status: str
    session_id: str
    timestamp: float


class FrameProcessResponse(BaseModel):
    """Frame processing response."""
    pose_name: str
    pose_detected: bool = True
    alignment_score: float
    issues: List[str]
    coaching_sentence: str
    risk_level: str = "low"


class SessionSummaryResponse(BaseModel):
    """Session summary response."""
    status: str
    session_id: str
    summary: Dict


class SessionStatsResponse(BaseModel):
    """Session statistics response."""
    session_id: str
    duration: float
    frame_count: int