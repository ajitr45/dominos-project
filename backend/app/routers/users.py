from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import (get_current_user, require_admin, require_admin_or_manager, require_delivery_boy)
from app.models import User
from app.schemas import AdminUserCreateRequest, AdminUserResponse, ChangePasswordRequest, UserResponse, UserRoleUpdateRequest, UserStatusUpdateRequest
from app.services.auth_service import change_password
from app.services.user_service import create_user_by_admin, get_all_users, update_user_status, update_user_role


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
        

@router.get(
    "/",
    response_model=list[AdminUserResponse],
)
def get_users(db: Session = Depends(get_db), current_user: User = Depends(require_admin)):
    # Get all users for admin
    users = get_all_users(db)

    return users


@router.patch("/{user_id}/status", response_model=AdminUserResponse,)
def update_user_status_api(
    user_id: int,
    status_data: UserStatusUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    try:
        updated_user = update_user_status(
            db=db,
            user_id=user_id,
            is_active=status_data.is_active,
            current_admin=current_admin,
        )

        return updated_user

    except ValueError as exc:
        if str(exc) == "User not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc),)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    
    
@router.post("/", response_model=AdminUserResponse, status_code=status.HTTP_201_CREATED)
def create_user_as_admin(
    user_data: AdminUserCreateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    
    try:
        created_user = create_user_by_admin(
            db=db,
            username=user_data.username,
            email=user_data.email,
            phone=user_data.phone,
            password=user_data.password,
            role=user_data.role,
        )

        return created_user

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))
    

@router.patch(
    "/{user_id}/role",
    response_model=AdminUserResponse,
)
def update_user_role_api(
    user_id: int,
    role_data: UserRoleUpdateRequest,
    db: Session = Depends(get_db),
    current_admin: User = Depends(require_admin),
):
    try:
        updated_user = update_user_role(
            db=db,
            user_id=user_id,
            role=role_data.role,
            current_admin=current_admin,
        )

        return updated_user

    except ValueError as exc:
        if str(exc) == "User not found":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            )

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )
        
        
@router.get("/manager")
def manager_area(current_user: User = Depends(require_admin_or_manager)):
    
    manager_response = {
        "message": "Welcome to manager area",
        "manager_id": current_user.id,
    }

    return manager_response