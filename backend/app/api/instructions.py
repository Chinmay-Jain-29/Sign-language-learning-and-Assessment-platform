from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.domain import User, RoleEnum, InstructorInstruction, Notification
from app.api.deps import get_current_user, require_roles

router = APIRouter(prefix="/instructions", tags=["Instructor Instructions"])

class CreateInstructionRequest(BaseModel):
    learner_id: int
    message: str

class InstructionResponse(BaseModel):
    id: int
    instructor_id: int
    instructor_name: str
    learner_id: int
    message: str
    is_read: bool
    created_at: datetime
    read_at: Optional[datetime] = None

@router.post("", response_model=InstructionResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=InstructionResponse, status_code=status.HTTP_201_CREATED)
def create_instruction(
    payload: CreateInstructionRequest,
    current_user: User = Depends(require_roles([RoleEnum.INSTRUCTOR, RoleEnum.ADMINISTRATOR])),
    db: Session = Depends(get_db)
):
    """
    Instructor creates a private, targeted instruction for a learner.
    Enforces that target user exists.
    Spawns in-app notification for the learner.
    """
    target_learner = db.query(User).filter(User.id == payload.learner_id).first()
    if not target_learner:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Learner with ID {payload.learner_id} does not exist."
        )

    if not payload.message.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Instruction message cannot be empty."
        )

    instruction = InstructorInstruction(
        instructor_id=current_user.id,
        learner_id=payload.learner_id,
        message=payload.message.strip(),
        created_at=datetime.utcnow(),
        is_read=False
    )
    db.add(instruction)
    db.commit()
    db.refresh(instruction)

    return InstructionResponse(
        id=instruction.id,
        instructor_id=instruction.instructor_id,
        instructor_name=current_user.full_name,
        learner_id=instruction.learner_id,
        message=instruction.message,
        is_read=instruction.is_read,
        created_at=instruction.created_at,
        read_at=instruction.read_at
    )

@router.get("/me", response_model=List[InstructionResponse])
def get_my_instructions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Learner retrieves ONLY instructions addressed to them (learner_id == current_user.id).
    Strictly isolates data to prevent cross-user leakage (Admin, Instructors, Trainers receive empty list).
    """
    if current_user.role != RoleEnum.LEARNER:
        return []

    instructions = db.query(InstructorInstruction)\
        .filter(InstructorInstruction.learner_id == current_user.id)\
        .order_by(InstructorInstruction.created_at.desc())\
        .all()

    return [
        InstructionResponse(
            id=inst.id,
            instructor_id=inst.instructor_id,
            instructor_name=inst.instructor.full_name if inst.instructor else "Instructor",
            learner_id=inst.learner_id,
            message=inst.message,
            is_read=inst.is_read,
            created_at=inst.created_at,
            read_at=inst.read_at
        )
        for inst in instructions
    ]

@router.patch("/{instruction_id}/read", response_model=InstructionResponse)
@router.put("/{instruction_id}/read", response_model=InstructionResponse)
def mark_instruction_as_read(
    instruction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Learner marks an instruction as read.
    Enforces that the user is a Learner and strictly owns this instruction.
    """
    if current_user.role != RoleEnum.LEARNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only learners can mark their instructions as read."
        )

    inst = db.query(InstructorInstruction).filter(
        InstructorInstruction.id == instruction_id,
        InstructorInstruction.learner_id == current_user.id
    ).first()

    if not inst:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instruction not found or you are not authorized to access it."
        )

    inst.is_read = True
    inst.read_at = datetime.utcnow()
    db.commit()
    db.refresh(inst)

    return InstructionResponse(
        id=inst.id,
        instructor_id=inst.instructor_id,
        instructor_name=inst.instructor.full_name if inst.instructor else "Instructor",
        learner_id=inst.learner_id,
        message=inst.message,
        is_read=inst.is_read,
        created_at=inst.created_at,
        read_at=inst.read_at
    )
