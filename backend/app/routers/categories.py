from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import require_admin_or_manager
from app.models import Category
from app.schemas import (CategoryCreate, CategoryUpdate, CategoryResponse)
from app.services.category_service import (create_category, get_categories, get_category_by_id, update_category, deactivate_category, activate_category)


router = APIRouter(prefix="/categories", tags=["Categories"])


# Create Category
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category_api(category_data: CategoryCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_or_manager)):
    
    try:
        category = create_category(db=db, category_data=category_data)

        return category

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Get All Categories
@router.get("/", response_model=list[CategoryResponse],)
def get_categories_api(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    
    categories = get_categories(db=db, skip=skip, limit=limit)

    return categories


# Get Single Category
@router.get("/{category_id}", response_model=CategoryResponse,)
def get_category_api(category_id: int, db: Session = Depends(get_db)):
    
    category = get_category_by_id(db=db, category_id=category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category


# Update Category
@router.patch("/{category_id}", response_model=CategoryResponse,)
def update_category_api(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_manager),
):
    category = get_category_by_id(db=db, category_id=category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    try:
        updated_category = update_category(db=db, category=category, category_data=category_data)

        return updated_category

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Deactivate Category
@router.patch("/{category_id}/deactivate", response_model=CategoryResponse)
def deactivate_category_api(
    category_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_manager),
):
    category = get_category_by_id(db=db, category_id=category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    try:
        deactivated_category = deactivate_category(db=db, category=category)

        return deactivated_category

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    

@router.patch("/{category_id}/activate", response_model=CategoryResponse)
def activate_category_api(category_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin_or_manager)):
    try:
        category = activate_category(db, category_id)

    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return category