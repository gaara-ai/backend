from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import cv2
import numpy as np
from typing import Optional

from app.dependency_container import DependencyContainer
from app.session_manager import SessionManager
from config.settings import Settings
from models.user_profile import UserProfile
from api.schemas import (
    SessionStartRequest,
    SessionStartResponse,
    FrameProcessResponse,
    SessionSummaryResponse
)

app = FastAPI(title="AI Yoga Master API")

# Global state (in production, use proper state management)
session_manager: Optional[SessionManager] = None
settings = Settings()


@app.on_event("startup")
async def startup_event():
    """Initialize system on startup."""
    global session_manager
    
    # Default user profile
    user_profile = UserProfile(
        user_id="api_user",
        name="API User",
        level="intermediate",
        conditions=[]
    )
    
    container = DependencyContainer(settings, user_profile)
    dependencies = container.initialize()
    session_manager = SessionManager(dependencies)


@app.post("/session/start", response_model=SessionStartResponse)
async def start_session(request: SessionStartRequest):
    """Start a new yoga session."""
    if not session_manager:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    # Update user profile if provided
    if request.user_profile:
        # Reinitialize with new profile
        pass
    
    result = session_manager.start_session()
    return SessionStartResponse(**result)


@app.post("/session/stop", response_model=SessionSummaryResponse)
async def stop_session():
    """Stop current yoga session."""
    if not session_manager:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    result = session_manager.stop_session()
    return SessionSummaryResponse(**result)


@app.post("/frame/process", response_model=FrameProcessResponse)
async def process_frame(file: UploadFile = File(...)):
    """Process a single frame image."""
    if not session_manager:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    if not session_manager.is_active():
        raise HTTPException(status_code=400, detail="No active session")
    
    # Read image
    contents = await file.read()
    nparr = np.frombuffer(contents, np.uint8)
    frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if frame is None:
        raise HTTPException(status_code=400, detail="Invalid image")
    
    # Process frame
    result = session_manager.process_frame(frame)
    
    if not result:
        return FrameProcessResponse(
            pose_name="unknown",
            pose_detected=False,
            alignment_score=0.0,
            issues=[],
            coaching_sentence="Processing..."
        )
    
    return FrameProcessResponse(**result)


@app.get("/session/stats")
async def get_session_stats():
    """Get current session statistics."""
    if not session_manager:
        raise HTTPException(status_code=500, detail="System not initialized")
    
    return session_manager.get_session_stats()


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": "1.0.0"}