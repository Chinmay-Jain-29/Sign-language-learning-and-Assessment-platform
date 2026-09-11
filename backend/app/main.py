from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.core.logging import logger, setup_logging
from app.core.exceptions import AppException
from app.core.response import error_response
from app.database.session import SessionLocal
from app.database.init_db import init_db

from app.api.v1 import health, auth as v1_auth, ai as v1_ai
from app.api import (
    users, lessons, practice, assessment,
    analytics, recommendations, reports, certification,
    notifications, admin, recognition, instructions,
    achievements
)

setup_logging()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url=f"{settings.API_V1_STR}/docs",
    redoc_url=f"{settings.API_V1_STR}/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    logger.error(f"AppException: {exc.code} - {exc.message}")
    return error_response(
        message=exc.message,
        code=exc.code,
        details=exc.details,
        status_code=exc.status_code
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"HTTPException {exc.status_code}: {exc.detail}")
    return error_response(
        message=str(exc.detail),
        code="HTTP_ERROR",
        status_code=exc.status_code
    )

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.warning(f"ValidationError: {exc.errors()}")
    return error_response(
        message="Request validation error",
        code="VALIDATION_ERROR",
        details={"errors": exc.errors()},
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled Server Exception: {str(exc)}")
    return error_response(
        message="Internal server error",
        code="INTERNAL_SERVER_ERROR",
        details={"error_type": type(exc).__name__},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

app.include_router(health.router, prefix=settings.API_V1_STR)
app.include_router(v1_auth.router, prefix=settings.API_V1_STR)
app.include_router(v1_ai.router, prefix=settings.API_V1_STR)
app.include_router(users.router, prefix=settings.API_V1_STR)
app.include_router(lessons.router, prefix=settings.API_V1_STR)
app.include_router(practice.router, prefix=settings.API_V1_STR)
app.include_router(assessment.router, prefix=settings.API_V1_STR)
app.include_router(analytics.router, prefix=settings.API_V1_STR)
app.include_router(recommendations.router, prefix=settings.API_V1_STR)
app.include_router(reports.router, prefix=settings.API_V1_STR)
app.include_router(certification.router, prefix=settings.API_V1_STR)
app.include_router(notifications.router, prefix=settings.API_V1_STR)
app.include_router(admin.router, prefix=settings.API_V1_STR)
app.include_router(recognition.router, prefix=settings.API_V1_STR)
app.include_router(instructions.router, prefix=settings.API_V1_STR)
app.include_router(achievements.router, prefix=settings.API_V1_STR)

# Mount Static Files for Uploads (Avatars, Documents)
import os
from fastapi.staticfiles import StaticFiles

UPLOAD_DIR = os.path.join(os.getcwd(), "uploads")
os.makedirs(os.path.join(UPLOAD_DIR, "avatars"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

@app.on_event("startup")
def on_startup():
    try:
        db = SessionLocal()
        init_db(db)
        db.close()
        logger.info("FastAPI application database initialized successfully!")
    except Exception as e:
        logger.error(f"Error during init_db on startup: {e}")
    logger.info("FastAPI application started cleanly!")

@app.get("/")
def root():
    return {
        "success": True,
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "data": {
            "version": settings.VERSION,
            "docs": f"{settings.API_V1_STR}/docs",
            "health": f"{settings.API_V1_STR}/health"
        }
    }
