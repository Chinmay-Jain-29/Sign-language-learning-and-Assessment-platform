from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import User, Notification
from app.api.deps import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("/")
def get_user_notifications(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    notifications = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id, Notification.type != "instruction")
        .order_by(Notification.created_at.desc())
        .all()
    )
    if not notifications:
        n = Notification(
            user_id=current_user.id,
            title="Welcome to AI Sign Language Platform",
            message="Start practicing ASL letters with real-time MediaPipe AI gesture feedback today!",
            type="info"
        )
        db.add(n)
        db.commit()
        db.refresh(n)
        notifications = [n]
    return [
        {
            "id": n.id,
            "title": n.title,
            "message": n.message,
            "type": n.type,
            "is_read": n.is_read,
            "created_at": n.created_at
        }
        for n in notifications
    ]

@router.patch("/{notification_id}/read")
@router.put("/{notification_id}/read")
def mark_notification_as_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    n = db.query(Notification).filter(Notification.id == notification_id, Notification.user_id == current_user.id).first()
    if not n:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found.")
    n.is_read = True
    db.commit()
    db.refresh(n)
    return {
        "id": n.id,
        "title": n.title,
        "message": n.message,
        "type": n.type,
        "is_read": n.is_read,
        "created_at": n.created_at
    }
