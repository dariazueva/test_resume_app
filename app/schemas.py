from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, EmailStr


class CreateUser(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool


class TokenData(BaseModel):
    access_token: str


class ResumeBase(BaseModel):
    title: str
    content: str


class ResumeCreate(ResumeBase):
    pass


class Resume(ResumeBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class ResumeImprovementBase(BaseModel):
    improved_content: str


class ResumeImprovementCreate(ResumeImprovementBase):
    resume_id: int


class ResumeImprovement(ResumeImprovementBase):
    id: int
    resume_id: int
    created_at: datetime

    class Config:
        from_attributes = True


class ResumeWithImprovements(Resume):
    improvements: List[ResumeImprovement] = []
