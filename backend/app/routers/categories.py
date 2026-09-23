from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import  CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.category_service import  create_category, get_categories, get_category_by_id, update_category, deactivate_category
from app.dependencies.auth import require_admin



router = APIRouter(prefix="/categories", tags=["Categories"],)


# Create Category
@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED,)
def create_category_api(category_data: CategoryCreate, db: Session = Depends(get_db), admin= Depends(require_admin)):
    try:
        return create_category(db, category_data)

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Get All Categories
@router.get("/", response_model=list[CategoryResponse],)
def get_categories_api(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    
    return get_categories( db, skip, limit)


# Get Single Category
@router.get( "/{category_id}", response_model=CategoryResponse,)
def get_category_api(category_id: int, db: Session = Depends(get_db),):
    category = get_category_by_id(db, category_id,)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found",)

    return category


# Update Category
@router.patch("/{category_id}", response_model=CategoryResponse,)
def update_category_api(
    category_id: int, 
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin)):
    
    
    category = get_category_by_id(db, category_id)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    try:
        return update_category(db, category, category_data)

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Deactivate Category
@router.patch("/{category_id}/deactivate", response_model=CategoryResponse,)
def deactivate_category_api(category_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    category = get_category_by_id(db, category_id,)

    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found",)

    return deactivate_category(db, category)