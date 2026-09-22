from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user, require_admin
from app.models import User
from app.schemas import UserResponse


router = APIRouter(prefix="/users", tags=["Users"])


@router.get("/user-profile", response_model=UserResponse)
def get_my_profile(current_user: User = Depends(get_current_user)):
    # Return the currently authenticated user's profile
    return current_user



@router.get("/admin")
def admin_area(current_user: User = Depends(require_admin),):
    # Allow access only to authenticated admin users
    return {
        
        "message": "Welcome to admin area",
        "admin_id": current_user.id,
    }   