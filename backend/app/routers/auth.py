from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import LoginRequest, UserCreate, UserResponse
from app.services.auth_service import authenticate_user, register_user
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