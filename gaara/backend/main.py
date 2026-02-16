from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
import logging
from contextlib import asynccontextmanager

from config.settings import Settings
from app.dependency_container import DependencyContainer
from app.session_manager import StatelessSessionManager
from auth.firebase_auth import initialize_firebase, get_current_user
from models.request_models import PoseEvaluationRequest, SessionStartRequest
from models.response_models import (
    PoseEvaluationResponse,
    HealthCheckResponse,
    ErrorResponse
)
from models.user_profile import UserProfile
from utils.logger import setup_logger

# Initialize settings
settings = Settings()

# Setup logging
logger = setup_logger("yoga_master_api", level=settings.log_level)

# Initialize dependency container
container = DependencyContainer(settings)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    # Startup
    logger.info("Starting AI Yoga Master API...")
    
    try:
        # Initialize Firebase
        initialize_firebase(settings.firebase_service_account_path)
        
        # Initialize dependencies
        container.initialize()
        
        logger.info("API startup complete")
        
    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down API...")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    description=settings.api_description,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests."""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {process_time:.3f}s"
    )
    
    return response


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            status_code=exc.status_code
        ).dict()
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc),
            status_code=500
        ).dict()
    )


# Health check endpoint (public)
@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthCheckResponse(
        status="healthy",
        version=settings.api_version,
        timestamp=time.time()
    )


# Main evaluation endpoint (protected)
@app.post(
    "/evaluate",
    response_model=PoseEvaluationResponse,
    tags=["Evaluation"],
    dependencies=[Depends(get_current_user)]
)
async def evaluate_pose(
    request: PoseEvaluationRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Evaluate yoga pose alignment and provide coaching feedback.
    
    Requires Firebase authentication.
    
    Args:
        request: Pose evaluation request with angles, landmarks, and user profile
        current_user: Current authenticated user from Firebase
        
    Returns:
        Pose evaluation response with alignment score and coaching
    """
    logger.info(f"Evaluating pose for user: {current_user['uid']}")
    
    try:
        # Create user profile
        user_profile = UserProfile(
            user_id=current_user['uid'],
            name=current_user.get('name', 'User'),
            level=request.user_profile.level,
            conditions=request.user_profile.conditions,
            age=request.user_profile.age
        )
        
        # Create session manager
        session_manager = StatelessSessionManager(
            physics_engine=container.physics_engine,
            rule_engine=container.rule_engine,
            safety_engine=container.safety_engine,
            correction_engine=container.correction_engine,
            llm_coaching_engine=container.llm_coaching_engine
        )
        
        # Evaluate pose
        result = session_manager.evaluate_pose(
            pose_name=request.pose_name,
            angles=request.angles.dict(),
            landmarks=request.landmarks.dict(),
            user_profile=user_profile
        )
        
        return PoseEvaluationResponse(**result)
        
    except Exception as e:
        logger.error(f"Evaluation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Evaluation failed")


# Test endpoint for development (remove in production)
@app.post(
    "/evaluate-test",
    response_model=PoseEvaluationResponse,
    tags=["Testing"],
    include_in_schema=False  # Hide from docs in production
)
async def evaluate_pose_test(request: PoseEvaluationRequest):
    """
    Test evaluation endpoint without authentication.
    FOR DEVELOPMENT ONLY - Remove in production.
    """
    logger.warning("Using unauthenticated test endpoint")
    
    user_profile = UserProfile(
        user_id="test_user",
        name="Test User",
        level=request.user_profile.level,
        conditions=request.user_profile.conditions,
        age=request.user_profile.age
    )
    
    session_manager = StatelessSessionManager(
        physics_engine=container.physics_engine,
        rule_engine=container.rule_engine,
        safety_engine=container.safety_engine,
        correction_engine=container.correction_engine,
        llm_coaching_engine=container.llm_coaching_engine
    )
    
    result = session_manager.evaluate_pose(
        pose_name=request.pose_name,
        angles=request.angles.dict(),
        landmarks=request.landmarks.dict(),
        user_profile=user_profile
    )
    
    return PoseEvaluationResponse(**result)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )