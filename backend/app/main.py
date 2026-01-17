"""
EduSynapse Backend Application
Main FastAPI entry point
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from loguru import logger
import sys

from app.config import settings
from app.database import Database

# Configure logging
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="DEBUG" if settings.debug else "INFO"
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info(f"Starting {settings.app_name} Backend...")
    await Database.connect()
    
    # Initialize knowledge base and vector store
    from app.services.knowledge_base import KnowledgeBaseService
    await KnowledgeBaseService.initialize()
    
    logger.info(f"{settings.app_name} Backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.app_name} Backend...")
    await Database.disconnect()
    logger.info("Shutdown complete")


# Create FastAPI application
app = FastAPI(
    title=f"{settings.app_name} API",
    description="Multi-Agent Adaptive Learning Platform Backend",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.app_env
    }


# API info endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "Multi-Agent Adaptive Learning Platform",
        "docs": "/docs",
        "health": "/health"
    }


# Import and include routers
from app.routes import auth, sessions, assessments, dashboard

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(sessions.router, prefix="/api/sessions", tags=["Learning Sessions"])
app.include_router(assessments.router, prefix="/api/assessments", tags=["Assessments"])
app.include_router(dashboard.router, prefix="/api/dashboard", tags=["Dashboard"])


# Agent orchestration endpoint (for direct testing)
@app.post("/api/orchestrate")
async def orchestrate_agents(request: Request):
    """
    Direct endpoint to trigger CrewAI agent orchestration
    Primarily for testing and debugging
    """
    from app.agents.crew import EduSynapseCrew
    
    body = await request.json()
    
    crew = EduSynapseCrew()
    result = await crew.execute(
        user_input=body.get("input", ""),
        user_id=body.get("user_id"),
        session_id=body.get("session_id"),
        modality=body.get("modality", "text")
    )
    
    return {
        "success": True,
        "result": result
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
