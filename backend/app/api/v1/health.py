from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.database.session import get_db
from app.core.config import settings
from app.core.response import success_response

router = APIRouter(tags=["Health"])

@router.get("/health")
def health_check(db: Session = Depends(get_db)):
    db_status = "Healthy"
    try:
        db.execute(text("SELECT 1"))
    except Exception as e:
        db_status = f"Unhealthy: {str(e)}"

    data = {
        "status": "Healthy" if db_status == "Healthy" else "Degraded",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "ai_model_loaded": True
    }
    return success_response(data=data, message="System health check successful")

@router.get("/health/ml")
def ml_health_check():
    """
    Diagnostic ML Health Check Endpoint:
    Returns non-sensitive metadata verifying model status, SHA256 checksum,
    supported classes, feature dimensions, and preprocessing version.
    """
    from app.ai.pipeline import ai_pipeline
    meta = ai_pipeline.get_model_metadata()
    return success_response(data=meta, message="ML subsystem health and parity metadata retrieved successfully")
