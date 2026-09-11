from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.api.v1.auth import get_current_user, require_roles
from app.models.domain import User, Lesson, RoleEnum
from app.content.lesson_registry import lesson_registry, LessonContent

router = APIRouter()

@router.get("", response_model=List[LessonContent])
def list_lessons(current_user: User = Depends(get_current_user)):
    """Returns list of all available ASL alphabet sign lessons (A-Z)."""
    return lesson_registry.list_all_lessons()

@router.get("/{id}", response_model=LessonContent)
def get_lesson_by_id(id: str, current_user: User = Depends(get_current_user)):
    """Returns lesson details for a specific sign character (e.g., 'A')."""
    lesson = lesson_registry.get_lesson(id)
    if not lesson:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Lesson for sign '{id}' not found."
        )
    return lesson

@router.post("", response_model=LessonContent, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson_data: LessonContent,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    """Creates a new lesson entry (Instructor / Admin RBAC restricted)."""
    lesson_registry._lessons[lesson_data.sign.upper()] = lesson_data
    return lesson_data

@router.put("/{id}", response_model=LessonContent)
def update_lesson(
    id: str,
    lesson_data: LessonContent,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    """Updates an existing lesson entry (Instructor / Admin RBAC restricted)."""
    char = id.upper()
    lesson_registry._lessons[char] = lesson_data
    return lesson_data

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    id: str,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR]))
):
    """Deletes a lesson entry (Instructor / Admin RBAC restricted)."""
    char = id.upper()
    if char in lesson_registry._lessons:
        del lesson_registry._lessons[char]
    return None
