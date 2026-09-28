from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import (get_current_user, require_admin, require_delivery_boy)
from app.models import User
from app.schemas import ChangePasswordRequest, UserResponse
from app.services.auth_service import change_password


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/me", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    # Return the currently authenticated user's profile
    user_profile = current_user

    return user_profile


@router.get("/admin")
def admin_area(current_user: User = Depends(require_admin)):
    # Allow access only to authenticated admin users
    admin_response = {
        "message": "Welcome to admin area",
        "admin_id": current_user.id,
    }

    return admin_response


@router.get("/delivery")
def delivery_area(current_user: User = Depends(require_delivery_boy)):
    # Allow access only to authenticated delivery boys
    delivery_response = {
        "message": "Welcome to delivery area",
        "delivery_boy_id": current_user.id,
    }

    return delivery_response



@router.post("/change-password")
def change_user_password(
    password_data: ChangePasswordRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        updated_user = change_password(
            db=db,
            user=current_user,
            current_password=password_data.current_password,
            new_password=password_data.new_password,
        )

        return {
            "message": "Password changed successfully",
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )