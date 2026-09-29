from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    UserResponse,
)
from app.services.auth_service import AuthService
from app.api.dependencies import get_current_user
from app.models.user import User


router = APIRouter(
    prefix="/api/auth",
    tags=["Authentication"],
)


@router.post(
    "/register",
    response_model=AuthResponse,
)
def register(
    request: RegisterRequest,
    db: Session = Depends(get_db),
):

    try:

        user, token = AuthService.register(
            db=db,
            name=request.name,
            email=request.email,
            password=request.password,
        )

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
            ),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e),
        )


@router.post(
    "/login",
    response_model=AuthResponse,
)
def login(
    request: LoginRequest,
    db: Session = Depends(get_db),
):

    try:

        user, token = AuthService.login(
            db=db,
            email=request.email,
            password=request.password,
        )

        return AuthResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse(
                id=user.id,
                name=user.name,
                email=user.email,
                role=user.role,
                is_active=user.is_active,
            ),
        )

    except ValueError as e:

        raise HTTPException(
            status_code=401,
            detail=str(e),
        )


@router.get(
    "/me",
    response_model=UserResponse,
)
def get_me(
    current_user: User = Depends(get_current_user),
):
    return UserResponse(
        id=current_user.id,
        name=current_user.name,
        email=current_user.email,
        role=current_user.role,
        is_active=current_user.is_active,
    )