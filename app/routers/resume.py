from typing import Annotated, List

from app.db import get_db
from app.schemas import Resume as ResumeSchema
from app.schemas import ResumeCreate, UserResponse
from app.services.auth import AuthService
from app.services.resume import ResumeService
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.get("/", response_model=List[ResumeSchema])
async def get_user_resumes(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: UserResponse = Depends(AuthService.get_current_user),
):
    """Получает все резюме текущего пользователя"""
    return await ResumeService.get_user_resumes(db, current_user.id)


@router.get("/{resume_id}", response_model=ResumeSchema)
async def get_resume(
    resume_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: UserResponse = Depends(AuthService.get_current_user),
):
    """Получает резюме по ID"""
    return await ResumeService.get_resume_by_id(db, resume_id, current_user.id)


@router.post("/", response_model=ResumeSchema, status_code=status.HTTP_201_CREATED)
async def create_resume(
    resume_data: ResumeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: UserResponse = Depends(AuthService.get_current_user),
):
    """Создает новое резюме"""
    return await ResumeService.create_resume(db, resume_data, current_user.id)


@router.put("/{resume_id}", response_model=ResumeSchema)
async def update_resume(
    resume_id: int,
    resume_data: ResumeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: UserResponse = Depends(AuthService.get_current_user),
):
    """Обновляет резюме"""
    return await ResumeService.update_resume(
        db, resume_id, resume_data, current_user.id
    )


@router.delete("/{resume_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_resume(
    resume_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: UserResponse = Depends(AuthService.get_current_user),
):
    """Удаляет резюме"""
    await ResumeService.delete_resume(db, resume_id, current_user.id)
