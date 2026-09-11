from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from app.database.session import get_db
from app.api.deps import get_current_user
from app.models.domain import User
from app.services.achievement_service import AchievementService

router = APIRouter(prefix="/achievements", tags=["Achievements"])

@router.get("", response_model=Dict[str, Any])
def get_user_achievements(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the authenticated user's personal 26 ASL alphabet achievements.
    Consumes canonical sign mastery analytics and preserves unlock history.
    Strictly private to the authenticated user.
    """
    return AchievementService.get_user_achievements(db=db, current_user=current_user)

@router.get("/{sign}", response_model=Dict[str, Any])
def get_single_achievement(
    sign: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Returns the achievement status for a specific sign for the authenticated user.
    """
    clean_sign = sign.strip().upper()
    data = AchievementService.get_user_achievements(db=db, current_user=current_user)
    ach = next((a for a in data["achievements"] if a["sign"] == clean_sign), None)
    if not ach:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Achievement for sign '{clean_sign}' not found."
        )
    return ach
