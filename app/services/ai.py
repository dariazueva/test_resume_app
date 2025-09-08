from typing import List

from app.models.resume import Resume
from app.models.resume import ResumeImprovement as ResumeImprovementModel
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


class AIService:
    """Сервис для работы с AI улучшением резюме."""

    @staticmethod
    def improve_resume_content(content: str) -> str:
        """Улучшает содержание резюме (заглушка)."""

        return f"{content} [Improved with AI - Enhanced content structure and keywords]"

    @staticmethod
    async def improve_and_save_resume(
        db: AsyncSession, resume_id: int, user_id: int
    ) -> dict:
        """
        Улучшает резюме через AI, сохраняет улучшенную версию
        и сохраняет историю улучшений.
        """

        result = await db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.owner_id == user_id)
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
            )
        improved_content = AIService.improve_resume_content(resume.content)
        resume.content = improved_content
        await db.commit()
        await db.refresh(resume)
        improvement = ResumeImprovementModel(
            resume_id=resume_id, improved_content=improved_content
        )
        db.add(improvement)
        await db.commit()
        await db.refresh(improvement)
        return {"resume": resume, "improvement": improvement}

    @staticmethod
    async def get_resume_improvements(
        db: AsyncSession, resume_id: int, user_id: int
    ) -> List[ResumeImprovementModel]:
        """Получает историю улучшений для резюме."""

        result = await db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.owner_id == user_id)
        )
        if not result.scalar_one_or_none():
            raise HTTPException(status_code=404, detail="Resume not found")
        result = await db.execute(
            select(ResumeImprovementModel)
            .where(ResumeImprovementModel.resume_id == resume_id)
            .order_by(ResumeImprovementModel.created_at.desc())
        )
        return result.scalars().all()
