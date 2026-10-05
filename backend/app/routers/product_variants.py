from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_admin_or_manager
from app.schemas import (ProductVariantCreate, ProductVariantResponse, ProductVariantUpdate)
from app.services.product_variant_service import (create_product_variant, get_product_variant_for_admin, get_product_variants, get_product_variant_by_id, update_product_variant, deactivate_product_variant, activate_product_variant)


router = APIRouter(prefix="/product-variants", tags=["Product Variants"])


# Create Product Variant
@router.post("/", response_model=ProductVariantResponse, status_code=status.HTTP_201_CREATED,)
def create_product_variant_api(
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_manager),
):
    try:
        created_variant = create_product_variant(db, variant_data)

        return created_variant

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Get All Product Variants
@router.get( "/", response_model=list[ProductVariantResponse])
def get_product_variants_api(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    variants = get_product_variants(db, skip, limit)

    return variants


# Get Single Product Variant
@router.get("/{variant_id}", response_model=ProductVariantResponse)
def get_product_variant_api(variant_id: int, db: Session = Depends(get_db)):
    
    variant = get_product_variant_by_id(db, variant_id)

    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant not found")

    return variant


# Update Product Variant
@router.patch("/{variant_id}", response_model=ProductVariantResponse)
def update_product_variant_api(
    variant_id: int,
    variant_data: ProductVariantUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_manager),
):
    variant = get_product_variant_by_id(db, variant_id)

    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant not found")

    try:
        updated_variant = update_product_variant(db, variant, variant_data)

        return updated_variant

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


# Deactivate Product Variant
@router.patch("/{variant_id}/deactivate", response_model=ProductVariantResponse)
def deactivate_product_variant_api(variant_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin_or_manager)):
    
    variant = get_product_variant_by_id(db, variant_id)

    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant not found")

    try:
        deactivated_variant = deactivate_product_variant(db, variant)

        return deactivated_variant

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)
)


# Activate Product Variant
@router.patch("/{variant_id}/activate", response_model=ProductVariantResponse,)
def activate_product_variant_api(
    variant_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_manager),
):
    variant = get_product_variant_for_admin(db, variant_id)

    if not variant:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Product variant not found")

    if variant.is_active:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Product variant is already active")

    try:
        activated_variant = activate_product_variant(db, variant)

        return activated_variant

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc),)