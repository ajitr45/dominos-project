from fastapi import APIRouter, Depends
from app.dependencies.auth import get_current_user, require_admin, require_delivery_boy
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
    
@router.get("/delivery")
def delivery_area(current_user: User = Depends(require_delivery_boy)):
    
    return {"message": "Welcome to delivery area", "delivery_boy_id": current_user.id}