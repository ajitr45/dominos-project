from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import require_admin
from app.schemas import (
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
)
from app.services.product_variant_service import (
    create_product_variant,
    get_product_variants,
    get_product_variant_by_id,
    update_product_variant,
    deactivate_product_variant,
)

router = APIRouter(
    prefix="/product-variants",
    tags=["Product Variants"],
)


@router.post(
    "/",
    response_model=ProductVariantResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_product_variant_api(
    variant_data: ProductVariantCreate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    try:
        return create_product_variant(db, variant_data)

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "/",
    response_model=list[ProductVariantResponse],
)
def get_product_variants_api(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return get_product_variants(db, skip, limit)


@router.get(
    "/{variant_id}",
    response_model=ProductVariantResponse,
)
def get_product_variant_api(
    variant_id: int,
    db: Session = Depends(get_db),
):
    variant = get_product_variant_by_id(db, variant_id)

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product variant not found",
        )

    return variant


@router.patch(
    "/{variant_id}",
    response_model=ProductVariantResponse,
)
def update_product_variant_api(
    variant_id: int,
    variant_data: ProductVariantUpdate,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    variant = get_product_variant_by_id(db, variant_id)

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product variant not found",
        )

    try:
        return update_product_variant(
            db,
            variant,
            variant_data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.patch(
    "/{variant_id}/deactivate",
    response_model=ProductVariantResponse,
)
def deactivate_product_variant_api(
    variant_id: int,
    db: Session = Depends(get_db),
    admin=Depends(require_admin),
):
    variant = get_product_variant_by_id(db, variant_id)

    if not variant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product variant not found",
        )

    return deactivate_product_variant(db, variant)