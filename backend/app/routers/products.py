from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import require_admin_or_manager
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import (activate_product, create_product, get_products, get_product_by_id, update_product, deactivate_product)


router = APIRouter(prefix="/products", tags=["Products"])


# Create Product
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product_api(product_data: ProductCreate, db: Session = Depends(get_db), current_user=Depends(require_admin_or_manager)):
    
    try:
        product = create_product(db=db, product_data=product_data)

        return product

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc),)


# Get All Products
@router.get("/", response_model=list[ProductResponse])
def get_products_api(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    products = get_products(db=db, skip=skip, limit=limit)

    return products


# Get Single Product
@router.get("/{product_id}", response_model=ProductResponse)
def get_product_api(product_id: int, db: Session = Depends(get_db)):
    
    product = get_product_by_id(db=db, product_id=product_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product


# Update Product
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product_api(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_manager),
):
    
    product = get_product_by_id(db=db, product_id=product_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found",)

    try:
        updated_product = update_product(db=db, product=product, product_data=product_data)

        return updated_product

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Deactivate Product
@router.patch("/{product_id}/deactivate", response_model=ProductResponse)
def deactivate_product_api(
    product_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_manager),
):
    product = get_product_by_id(db=db, product_id=product_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    deactivated_product = deactivate_product(db=db, product=product)

    return deactivated_product

#Activate Product
@router.patch("/{product_id}/activate", response_model=ProductResponse)
def activate_product_api(product_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin_or_manager)):
    try:
        activated_product = activate_product(db=db, product_id=product_id)

        return activated_product

    except ValueError as exc:
        if str(exc) == "Product not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))

        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))