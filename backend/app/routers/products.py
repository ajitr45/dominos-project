from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import require_admin
from app.schemas import ProductCreate, ProductUpdate, ProductResponse
from app.services.product_service import  create_product, get_products, get_product_by_id, update_product, deactivate_product


router = APIRouter(prefix="/products", tags=["Products"])


# Create Product
@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED,)
def create_product_api(
    product_data: ProductCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    try:
        return create_product(db, product_data,)

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Get All Products
@router.get("/", response_model=list[ProductResponse])
def get_products_api(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_products(db, skip, limit)


# Get Single Product
@router.get("/{product_id}", response_model=ProductResponse)
def get_product_api(product_id: int, db: Session = Depends(get_db)):
    
    product = get_product_by_id(db, product_id,)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return product


# Update Product
@router.patch("/{product_id}", response_model=ProductResponse)
def update_product_api(
    product_id: int,
    product_data: ProductUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    try:
        return update_product(db, product, product_data)

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Deactivate Product
@router.patch("/{product_id}/deactivate", response_model=ProductResponse)
def deactivate_product_api(
    product_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    product = get_product_by_id(db, product_id)

    if not product:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product not found")

    return deactivate_product(db, product)