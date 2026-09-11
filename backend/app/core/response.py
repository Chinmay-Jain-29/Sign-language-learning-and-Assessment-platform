from typing import Any, Optional, Dict
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

class ErrorDetail(BaseModel):
    code: str
    details: Optional[Dict[str, Any]] = None

class APIEnvelope(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[ErrorDetail] = None
    meta: Optional[Dict[str, Any]] = None

def success_response(
    data: Any = None,
    message: str = "Operation completed successfully",
    meta: Optional[Dict[str, Any]] = None,
    status_code: int = 200
) -> JSONResponse:
    content = {
        "success": True,
        "message": message,
        "data": data,
        "error": None,
        "meta": meta or {}
    }
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content))

def error_response(
    message: str = "An error occurred",
    code: str = "INTERNAL_ERROR",
    details: Optional[Dict[str, Any]] = None,
    status_code: int = 400,
    meta: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    content = {
        "success": False,
        "message": message,
        "data": None,
        "error": {
            "code": code,
            "details": details or {}
        },
        "meta": meta or {}
    }
    return JSONResponse(status_code=status_code, content=jsonable_encoder(content))

