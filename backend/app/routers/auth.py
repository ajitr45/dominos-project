from fastapi import APIRouter, Depends, HTTPException, status
import jwt
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import (ForgotPasswordRequest, LoginRequest, RefreshTokenRequest, ChangePasswordRequest, ResetPasswordRequest, UserCreate, UserResponse)
from app.services.auth_service import (authenticate_user, create_password_reset_token, create_user_refresh_token, change_password, register_user, reset_password, rotate_refresh_token)
from app.core.security import (create_access_token, decode_refresh_token)
from app.dependencies.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    try:
        registered_user = register_user(db, user_data)
        return registered_user
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = authenticate_user(
        db,
        login_data.identifier,
        login_data.password,
    )

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(user.id)
    refresh_token = create_user_refresh_token(db, user)

    response = {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
        },
    }

    return response


@router.post("/refresh")
def refresh_access_token(token_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        payload = decode_refresh_token(token_data.refresh_token)

        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Invalid refresh token")

        try:
            user_id = int(user_id)
        except (TypeError, ValueError):
            raise ValueError("Invalid refresh token")

        new_refresh_token = rotate_refresh_token(
            db=db,
            refresh_token=token_data.refresh_token,
            user_id=user_id,
        )

        access_token = create_access_token(user_id)

        response = {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

        return response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))

    except jwt.InvalidTokenError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")


@router.post("/change-password")
def change_user_password(
    password_data: ChangePasswordRequest,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        updated_user = change_password(
            db=db,
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )

        response = {
            "message": "Password changed successfully",
            "user": updated_user.username,
            "user_id":updated_user.id
        }

        return response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/forgot-password")
def forgot_password(request: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        reset_token = create_password_reset_token(db=db, email=request.email)

        response = {
            "message": (
                "If the email is registered, a password reset link has been sent"
            ),
        }

        return response

    except ValueError as exc:
        raise HTTPException( status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.post("/reset-password")
def reset_user_password(request: ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        updated_user = reset_password(db=db, token=request.token, new_password=request.new_password)

        response = {
            "message": "Password reset successfully",
            "user": updated_user.id,
            "username":updated_user.username
        }

        return response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))