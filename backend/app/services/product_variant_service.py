from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Product, ProductVariant, Size
from app.schemas import ProductVariantCreate, ProductVariantUpdate


def create_product_variant(db: Session, variant_data: ProductVariantCreate) -> ProductVariant:

    # Check product
    product = (db.query(Product).filter(Product.id == variant_data.product_id, Product.is_active.is_(True)).first())

    if not product:
        raise ValueError("Product not found")

    # Check size
    size = (db.query(Size).filter(
            Size.id == variant_data.size_id,
            Size.is_active.is_(True),
        )
        .first()
    )

    if not size:
        raise ValueError("Size not found")

    # Check duplicate product + size
    existing_variant = (
        db.query(ProductVariant)
        .filter(
            ProductVariant.product_id == variant_data.product_id,
            ProductVariant.size_id == variant_data.size_id,
            ProductVariant.is_active.is_(True),
        )
        .first()
    )

    if existing_variant:
        raise ValueError("Product variant already exists")

    variant = ProductVariant(
        product_id=variant_data.product_id,
        size_id=variant_data.size_id,
        price=variant_data.price,
    )

    try:
        db.add(variant)
        db.commit()
        db.refresh(variant)

    except IntegrityError:
        db.rollback()
        raise ValueError("Product variant could not be created")

    return variant


def get_product_variants(
    db: Session,
    skip: int = 0,
    limit: int = 20,
) -> list[ProductVariant]:

    return (
        db.query(ProductVariant)
        .filter(ProductVariant.is_active.is_(True))
        .order_by(ProductVariant.id)
        .offset(skip)
        .limit(limit)
        .all()
    )


def get_product_variant_by_id(db: Session, variant_id: int) -> ProductVariant | None:

    return (
        db.query(ProductVariant)
        .filter(
            ProductVariant.id == variant_id,
            ProductVariant.is_active.is_(True),
        )
        .first()
    )


def get_product_variant_for_admin(db: Session, variant_id: int) -> ProductVariant | None:

    variant = (db.query(ProductVariant).filter(ProductVariant.id == variant_id).first())

    return variant


def update_product_variant(
    db: Session,
    variant: ProductVariant,
    variant_data: ProductVariantUpdate,
) -> ProductVariant:

    if not variant.product.is_active:
        raise ValueError("Product is inactive")

    update_data = variant_data.model_dump(exclude_unset=True)

    # Validate active size
    if "size_id" in update_data:
        size = (
            db.query(Size)
            .filter(
                Size.id == update_data["size_id"],
                Size.is_active.is_(True),
            )
            .first()
        )

        if not size:
            raise ValueError("Size not found")

    # Product cannot be changed
    new_product_id = variant.product_id
    new_size_id = update_data.get("size_id", variant.size_id)

    # Prevent duplicate product + size
    existing_variant = (
        db.query(ProductVariant)
        .filter(
            ProductVariant.product_id == new_product_id,
            ProductVariant.size_id == new_size_id,
            ProductVariant.id != variant.id,
            ProductVariant.is_active.is_(True),
        )
        .first()
    )

    if existing_variant:
        raise ValueError("Product variant already exists")

    # Update only provided fields
    for field, value in update_data.items():
        setattr(variant, field, value)

    try:
        db.commit()
        db.refresh(variant)

    except IntegrityError:
        db.rollback()
        raise ValueError("Product variant could not be updated")

    return variant


def deactivate_product_variant(db: Session, variant: ProductVariant) -> ProductVariant:

    if not variant.is_active:
        raise ValueError("Product variant is already inactive")

    variant.is_active = False

    try:
        db.commit()
        db.refresh(variant)

    except IntegrityError:
        db.rollback()
        raise ValueError("Product variant could not be deactivated")

    return variant


def activate_product_variant(db: Session, variant: ProductVariant) -> ProductVariant:

    if variant.is_active:
        raise ValueError("Product variant is already active")

    if not variant.product.is_active:
        raise ValueError("Product is inactive")

    existing_variant = (
        db.query(ProductVariant)
        .filter(
            ProductVariant.product_id == variant.product_id,
            ProductVariant.size_id == variant.size_id,
            ProductVariant.id != variant.id,
            ProductVariant.is_active.is_(True),
        )
        .first()
    )

    if existing_variant:
        raise ValueError("Another active variant already exists for this product and size")

    variant.is_active = True

    try:
        db.commit()
        db.refresh(variant)

    except IntegrityError:
        db.rollback()
        raise ValueError("Product variant could not be activated")

    return variant