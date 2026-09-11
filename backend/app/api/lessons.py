from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.domain import Course, CourseModule, Lesson, User, RoleEnum, Sign, LessonSign
from app.schemas.dto import CourseResponse, LessonResponse, LessonCreate, LessonUpdate
from app.api.deps import get_current_user, require_roles
from app.core.exceptions import NotFoundException

router = APIRouter(prefix="/lessons", tags=["Courses & Lessons"])

@router.get("/courses", response_model=List[CourseResponse])
def list_courses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Course).all()

@router.get("/", response_model=List[LessonResponse])
def list_lessons(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Lesson).order_by(Lesson.order_index.asc()).all()

@router.get("/{lesson_id}", response_model=LessonResponse)
def get_lesson(lesson_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException(message="Lesson not found.")
    return lesson

@router.post("/", response_model=LessonResponse, status_code=status.HTTP_201_CREATED)
def create_lesson(
    lesson_in: LessonCreate,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    sign_char = lesson_in.sign_character.upper()
    sign_obj = db.query(Sign).filter(Sign.character == sign_char).first()
    if not sign_obj:
        sign_obj = Sign(character=sign_char, description=f"ASL sign for '{sign_char}'")
        db.add(sign_obj)
        db.commit()
        db.refresh(sign_obj)

    lesson = Lesson(
        module_id=lesson_in.module_id,
        title=lesson_in.title,
        sign_character=sign_char,
        description=lesson_in.description,
        tips=lesson_in.tips,
        reference_image_url=lesson_in.reference_image_url or f"/assets/asl/{sign_char.lower()}.png",
        video_url=lesson_in.video_url,
        order_index=lesson_in.order_index or 1
    )
    db.add(lesson)
    db.commit()
    db.refresh(lesson)

    ls = LessonSign(lesson_id=lesson.id, sign_id=sign_obj.id)
    db.add(ls)
    db.commit()

    return lesson

@router.put("/{lesson_id}", response_model=LessonResponse)
def update_lesson(
    lesson_id: int,
    lesson_in: LessonUpdate,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException(message="Lesson not found.")

    if lesson_in.title is not None:
        lesson.title = lesson_in.title
    if lesson_in.sign_character is not None:
        lesson.sign_character = lesson_in.sign_character.upper()
    if lesson_in.description is not None:
        lesson.description = lesson_in.description
    if lesson_in.tips is not None:
        lesson.tips = lesson_in.tips
    if lesson_in.reference_image_url is not None:
        lesson.reference_image_url = lesson_in.reference_image_url
    if lesson_in.video_url is not None:
        lesson.video_url = lesson_in.video_url
    if lesson_in.order_index is not None:
        lesson.order_index = lesson_in.order_index

    db.commit()
    db.refresh(lesson)
    return lesson

@router.delete("/{lesson_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson(
    lesson_id: int,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if not lesson:
        raise NotFoundException(message="Lesson not found.")

    db.delete(lesson)
    db.commit()
    return None
