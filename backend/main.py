"""
FastAPI application entry point for MOOSE LOON AI Mentor Platform.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="MOOSE LOON AI Mentor Platform",
    description="An AI Mentor for AI & Automation Education",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include auth routes
from auth.routes import router as auth_router
from database.session import init_db

from backend.chat import router as chat_router
from backend.mentor_features import router as mentor_router

app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(mentor_router)


@app.on_event("startup")
async def on_startup():
    # Initialize DB tables if not present
    try:
        init_db()
    except Exception:
        logger.exception("Failed to initialize database on startup")


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "message": "MOOSE LOON AI Mentor Platform is running",
        "environment": settings.ENVIRONMENT,
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check for load balancers."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        log_level="info",
    )
