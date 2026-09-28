from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ForgotPasswordRequest, LoginRequest, ResetPasswordRequest, UserCreate, UserResponse
from app.services.auth_service import authenticate_user, create_password_reset_token, register_user, reset_password
from app.core.security import create_access_token


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED,)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    
    # Keep business logic inside the service layer
    try:
        return register_user(db, user_data)

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc),)


@router.post("/login")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    # Verify email/phone and password
    user = authenticate_user(db, login_data.identifier, login_data.password)

    if not user:
        # Do not reveal whether email or phone exists
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # Generate JWT after successful authentication
    access_token = create_access_token(user.id)

    return {
        "message": "Login successful",
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone": user.phone,
        },
    }
    
@router.post("/forgot-password")
def forgot_password(password_data: ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        created_token = create_password_reset_token(db=db, email=password_data.email)

        response = {
            "message": (
                "If the account exists, a password reset link "
                "has been sent."
            )
        }

        return response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))
    
    
@router.post("/reset-password")
def reset_user_password(password_data: ResetPasswordRequest, db: Session = Depends(get_db)):
    
    try:
        updated_user = reset_password(db=db, token=password_data.token, new_password=password_data.new_password)

        response = {
            "message": "Password reset successfully",
            "user_id": updated_user.id,
        }

        return response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))