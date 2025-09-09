from datetime import timedelta
from typing import Annotated

from app.config import settings
from app.db import get_db
from app.models.user import User
from app.schemas import CreateUser, TokenData, UserResponse
from app.services.auth import AuthService, bcrypt_context, oauth2_scheme
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from loguru import logger
from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def create_user(
    db: Annotated[AsyncSession, Depends(get_db)], create_user: CreateUser
):
    """Регистрирует нового пользователя в системе."""

    try:
        existing_user = await db.scalar(
            select(User).where(
                (User.username == create_user.username)
                | (User.email == create_user.email)
            )
        )
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username or email already exists",
            )
        await db.execute(
            insert(User).values(
                username=create_user.username,
                email=create_user.email,
                hashed_password=bcrypt_context.hash(create_user.password),
            )
        )
        await db.commit()
        return {"message": "User created successfully"}
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during user creation",
        )


@router.post("/token", response_model=TokenData)
async def login(
    db: Annotated[AsyncSession, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """Аутентифицирует пользователя и возвращает JWT токены."""

    user = await AuthService.authenticate_user(
        db, form_data.username, form_data.password
    )
    access_token = await AuthService.create_token(
        user.username,
        user.id,
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )
    return TokenData(
        access_token=access_token,
    )


@router.get("/me", response_model=UserResponse)
async def read_current_user(user: UserResponse = Depends(AuthService.get_current_user)):
    """Получает данные текущего авторизованного пользователя."""

    return user


@router.get("/check_token")
async def check_token_validity(
    user: UserResponse = Depends(AuthService.get_current_user),
):
    """Проверяет валидность текущего токена."""

    return {"is_valid": True, "user": user.model_dump(), "message": "Token is valid"}


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user_profile(
    user_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: UserResponse = Depends(AuthService.get_current_user),
):
    """Получает профиль пользователя по ID."""

    await AuthService.validate_user_access(current_user, user_id)
    user = await db.scalar(
        select(User).where(User.id == user_id, User.is_active == True)
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[UserResponse, Depends(AuthService.get_current_user)],
    user_id: int,
):
    """Деактивирует пользователя (мягкое удаление)."""

    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You cannot delete yourself",
        )
    user = await db.scalar(select(User).where(User.id == user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.is_active:
        return
    await db.execute(update(User).where(User.id == user.id).values(is_active=False))
    await db.commit()


@router.get("/users", response_model=list[UserResponse])
async def get_users(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Получает список всех активных пользователей."""

    users = await db.scalars(select(User).where(User.is_active == True))
    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            is_active=user.is_active,
        )
        for user in users
    ]
