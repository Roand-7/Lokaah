#!/usr/bin/env python3
"""
LOKAAH API - FastAPI Backend
"""

# Load .env FIRST - before any other imports
from dotenv import load_dotenv
import os

# Try multiple locations for .env
env_paths = [
    '.env',  # Current directory
    os.path.join(os.path.dirname(__file__), '.env'),  # Script directory
    os.path.abspath('.env')  # Absolute path
]

for env_path in env_paths:
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        print(f"Loaded .env from: {env_path}")
        break
else:
    print("Warning: .env file not found")

# Now import everything else
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uvicorn
import traceback

from app.core.config import settings
from app.api.endpoints import router

# Day-1 operations logging for router/oracle/sandbox visibility.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s",
)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="LOKAAH - AI-Powered Adaptive Learning for CBSE Class 10 Mathematics",
    version="1.0.0",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None
)

# CORS middleware - uses CORS_ORIGINS from .env for production safety
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
    expose_headers=["X-Request-Id"],
    max_age=86400,
)


@app.on_event("startup")
async def startup_preflight_checks():
    if not settings.has_gemini_auth:
        logging.warning(
            "No Gemini authentication found. Set GEMINI_API_KEY or GOOGLE_APPLICATION_CREDENTIALS."
        )
    if settings.ENV.lower() == "production" and settings.DEBUG:
        logging.warning("DEBUG is enabled in production; set DEBUG=false before release.")
    if "*" in settings.cors_origins_list:
        logging.warning("CORS allows all origins; restrict CORS_ORIGINS for production.")

# Error handling
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logging.getLogger(__name__).exception("Unhandled error: %s", exc)
    if settings.DEBUG:
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc), "type": type(exc).__name__}
        )
    return JSONResponse(
        status_code=500,
        content={"response": "Hmm, I'm having trouble right now. Could you try again?"}
    )

# Include routers
app.include_router(router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to LOKAAH API",
        "status": "operational",
        "docs": "/docs"
    }

if __name__ == "__main__":
    print(f"Starting {settings.APP_NAME}...")
    print(f"AI Ratio: {settings.AI_RATIO * 100}%")
    print(f"Debug Mode: {settings.DEBUG}")
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG,
        workers=1 if settings.DEBUG else 4
    )


