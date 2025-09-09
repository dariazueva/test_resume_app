from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas import UserResponse
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


class AuthService:
    """Сервис для работы с аутентификацией и авторизацией"""

    @staticmethod
    async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> UserResponse:
        """Получает текущего пользователя по JWT токену."""

        try:
            payload = jwt.decode(
                token, settings.secret_key, algorithms=[settings.algorithm]
            )
            user_id: int | None = payload.get("id")
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token",
                )
            user = await db.scalar(
                select(User).where(User.id == user_id, User.is_active == True)
            )
            if not user:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found",
                )
            return UserResponse(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
            )
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )

    @staticmethod
    async def authenticate_user(
        db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str
    ) -> User:
        """Аутентифицирует пользователя по логину и паролю."""

        user = await db.scalar(
            select(User).where(User.username == username, User.is_active == True)
        )
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        if not bcrypt_context.verify(password, user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect password",
            )
        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User inactive",
            )
        return user

    @staticmethod
    async def create_token(
        username: str,
        user_id: int,
        expires_delta: timedelta = None,
    ) -> str:
        """Создает JWT токен."""

        expires_delta = expires_delta or timedelta(
            minutes=settings.access_token_expire_minutes
        )
        expire = datetime.now(timezone.utc) + expires_delta
        payload = {
            "sub": username,
            "id": user_id,
            "exp": int(expire.timestamp()),
        }
        return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)

    @staticmethod
    async def validate_user_access(current_user: UserResponse, user_id: int) -> None:
        """Проверяет права доступа к данным пользователя."""

        if current_user.id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Access denied"
            )
