from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional


class JointAngles(BaseModel):
    """Joint angles data."""
    left_knee_angle: float = Field(..., ge=0, le=180)
    right_knee_angle: float = Field(..., ge=0, le=180)
    left_elbow_angle: float = Field(..., ge=0, le=180)
    right_elbow_angle: float = Field(..., ge=0, le=180)
    left_hip_angle: float = Field(..., ge=0, le=180)
    right_hip_angle: float = Field(..., ge=0, le=180)
    spine_angle: float = Field(..., ge=0, le=180)
    shoulder_angle: Optional[float] = Field(None, ge=0, le=180)


class Landmarks(BaseModel):
    """3D landmarks data from frontend."""
    left_shoulder: List[float]
    right_shoulder: List[float]
    left_elbow: List[float]
    right_elbow: List[float]
    left_wrist: List[float]
    right_wrist: List[float]
    left_hip: List[float]
    right_hip: List[float]
    left_knee: List[float]
    right_knee: List[float]
    left_ankle: List[float]
    right_ankle: List[float]
    left_heel: List[float]
    right_heel: List[float]
    left_ear: List[float]
    right_ear: List[float]
    
    @validator('*')
    def validate_landmark(cls, v):
        if len(v) != 3:
            raise ValueError('Each landmark must have exactly 3 coordinates [x, y, z]')
        return v


class UserProfileRequest(BaseModel):
    """User profile in request."""
    level: str = Field(..., pattern="^(beginner|intermediate|advanced)$")
    conditions: List[str] = Field(default_factory=list)
    age: Optional[int] = Field(None, ge=10, le=100)


class PoseEvaluationRequest(BaseModel):
    """Request model for pose evaluation."""
    pose_name: str = Field(..., min_length=1, max_length=100)
    angles: JointAngles
    landmarks: Landmarks
    user_profile: UserProfileRequest
    
    class Config:
        schema_extra = {
            "example": {
                "pose_name": "parvatasana",
                "angles": {
                    "left_knee_angle": 175.5,
                    "right_knee_angle": 173.2,
                    "left_elbow_angle": 178.0,
                    "right_elbow_angle": 176.5,
                    "left_hip_angle": 85.0,
                    "right_hip_angle": 87.0,
                    "spine_angle": 165.0
                },
                "landmarks": {
                    "left_shoulder": [0.3, 0.3, 0.0],
                    "right_shoulder": [0.7, 0.3, 0.0],
                    "left_elbow": [0.2, 0.5, 0.0],
                    "right_elbow": [0.8, 0.5, 0.0],
                    "left_wrist": [0.1, 0.7, 0.0],
                    "right_wrist": [0.9, 0.7, 0.0],
                    "left_hip": [0.35, 0.6, 0.0],
                    "right_hip": [0.65, 0.6, 0.0],
                    "left_knee": [0.33, 0.8, 0.0],
                    "right_knee": [0.67, 0.8, 0.0],
                    "left_ankle": [0.32, 1.0, 0.0],
                    "right_ankle": [0.68, 1.0, 0.0],
                    "left_heel": [0.31, 1.02, 0.0],
                    "right_heel": [0.69, 1.02, 0.0],
                    "left_ear": [0.35, 0.15, 0.0],
                    "right_ear": [0.65, 0.15, 0.0]
                },
                "user_profile": {
                    "level": "beginner",
                    "conditions": ["back_pain"],
                    "age": 30
                }
            }
        }


class SessionStartRequest(BaseModel):
    """Request to start a session."""
    user_profile: UserProfileRequest


class ProgressRequest(BaseModel):
    """Request for progress tracking."""
    days: int = Field(default=7, ge=1, le=90)