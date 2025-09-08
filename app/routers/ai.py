from typing import Annotated, List

from app.db import get_db
from app.schemas import ResumeImprovement, UserResponse
from app.services.ai import AIService
from app.services.auth import AuthService
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/resume/{resume_id}/improve", response_model=ResumeImprovement)
async def improve_resume(
    resume_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: UserResponse = Depends(AuthService.get_current_user),
):
    """
    Улучшает резюме с помощью AI, автоматически сохраняет улучшенную версию
    и сохраняет историю улучшений
    """

    result = await AIService.improve_and_save_resume(db, resume_id, current_user.id)
    return result["improvement"]


@router.get("/resume/{resume_id}/improvements", response_model=List[ResumeImprovement])
async def get_improvements(
    resume_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: UserResponse = Depends(AuthService.get_current_user),
):
    """Получает историю улучшений для резюме"""

    improvements = await AIService.get_resume_improvements(
        db, resume_id, current_user.id
    )
    return improvements
