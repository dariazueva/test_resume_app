from app.db import Base
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="resumes")
    improvements = relationship(
        "ResumeImprovement", back_populates="resume", cascade="all, delete-orphan"
    )


class ResumeImprovement(Base):
    __tablename__ = "resume_improvements"

    id = Column(Integer, primary_key=True, index=True)
    resume_id = Column(Integer, ForeignKey("resumes.id"), nullable=False)
    improved_content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    resume = relationship("Resume", back_populates="improvements")
