from typing import List

from app.models.resume import Resume
from app.schemas import Resume as ResumeSchema
from app.schemas import ResumeCreate
from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status


class ResumeService:
    """Сервис для работы с резюме."""

    @staticmethod
    async def get_user_resumes(db: AsyncSession, user_id: int) -> List[ResumeSchema]:
        """Получает все резюме пользователя."""

        result = await db.execute(select(Resume).where(Resume.owner_id == user_id))
        resumes = result.scalars().all()
        return [ResumeSchema.from_orm(resume) for resume in resumes]

    @staticmethod
    async def get_resume_by_id(
        db: AsyncSession, resume_id: int, user_id: int
    ) -> ResumeSchema:
        """Получает резюме по ID."""

        result = await db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.owner_id == user_id)
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
            )
        return ResumeSchema.from_orm(resume)

    @staticmethod
    async def create_resume(
        db: AsyncSession, resume_data: ResumeCreate, user_id: int
    ) -> ResumeSchema:
        """Создает новое резюме."""

        db_resume = Resume(**resume_data.model_dump(), owner_id=user_id)
        db.add(db_resume)
        await db.commit()
        await db.refresh(db_resume)
        return ResumeSchema.from_orm(db_resume)

    @staticmethod
    async def update_resume(
        db: AsyncSession, resume_id: int, resume_data: ResumeCreate, user_id: int
    ) -> ResumeSchema:
        """Обновляет резюме."""

        result = await db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.owner_id == user_id)
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
            )
        resume.title = resume_data.title
        resume.content = resume_data.content
        await db.commit()
        await db.refresh(resume)
        return ResumeSchema.from_orm(resume)

    @staticmethod
    async def delete_resume(db: AsyncSession, resume_id: int, user_id: int) -> None:
        """Удаляет резюме."""

        result = await db.execute(
            select(Resume).where(Resume.id == resume_id, Resume.owner_id == user_id)
        )
        resume = result.scalar_one_or_none()
        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found"
            )
        await db.delete(resume)
        await db.commit()
