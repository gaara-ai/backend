from pydantic import BaseModel, Field
from typing import List, Dict, Optional


class PoseEvaluationResponse(BaseModel):
    """Response model for pose evaluation."""
    pose_name: str
    pose_detected: bool = True
    alignment_score: float = Field(..., ge=0, le=100)
    issues: List[str]
    coaching_sentence: str
    risk_level: str = Field(..., regex="^(low|medium|high)$")
    
    class Config:
        schema_extra = {
            "example": {
                "pose_name": "parvatasana",
                "pose_detected": True,
                "alignment_score": 78.5,
                "issues": ["knees_bent", "hips_low"],
                "coaching_sentence": "Gently straighten your knees and lift your hips higher.",
                "risk_level": "low"
            }
        }


class SessionStartResponse(BaseModel):
    """Response for session start."""
    status: str
    session_id: str
    message: str


class SessionSummaryResponse(BaseModel):
    """Response for session summary."""
    session_id: str
    duration: float
    average_alignment_score: float
    stability_score: float
    symmetry_score: float
    poses_performed: List[str]
    improvement_message: str


class ProgressResponse(BaseModel):
    """Response for progress data."""
    sessions_count: int
    total_duration: float
    average_alignment: float
    average_stability: float
    improvement_trend: str


class HealthCheckResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: float


class ErrorResponse(BaseModel):
    """Error response model."""
    error: str
    detail: Optional[str] = None
    status_code: int