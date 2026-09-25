from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from app.models import Category, Product, ProductVariant
from app.schemas import ProductCreate, ProductUpdate


def create_product(db: Session, product_data: ProductCreate) -> Product:

    # Check category exists and is active
    category = (db.query(Category).filter(Category.id == product_data.category_id, Category.is_active.is_(True))
        .first()
    )

    if not category:
        raise ValueError("Category not found")

    # Check duplicate product name
    existing_product = (db.query(Product).filter(Product.name == product_data.name, Product.is_active.is_(True)).first())

    if existing_product:
        raise ValueError("Product already exists")

    product = Product(
        name=product_data.name,
        description=product_data.description,
        image=product_data.image,
        category_id=product_data.category_id,
        is_veg=product_data.is_veg,
    )

    try:
        db.add(product)
        db.commit()
        db.refresh(product)

    except IntegrityError:
        db.rollback()
        raise ValueError("Product could not be created")

    return product


def get_products(db: Session, skip: int = 0, limit: int = 20) -> list[Product]:

    products = (
        db.query(Product).options(selectinload(Product.variants).selectinload(ProductVariant.size))
        .filter(Product.is_active.is_(True))
        .order_by(Product.id)
        .offset(skip)
        .limit(limit)
        .all()
    )

    # Return only active and available variants
    for product in products:
        product.variants = [variant for variant in product.variants if variant.is_active and variant.is_available]

    return products


def get_product_by_id(db: Session, product_id: int,) -> Product :

    product = (
        db.query(Product).options(selectinload(Product.variants).selectinload(ProductVariant.size))
        .filter(Product.id == product_id, Product.is_active.is_(True)).first()
    )

    if product:
        product.variants = [variant for variant in product.variants if variant.is_active and variant.is_available]

    return product


def update_product(db: Session, product: Product, product_data: ProductUpdate) -> Product:

    update_data = product_data.model_dump(exclude_unset=True)

    # Check category if category is being changed
    if "category_id" in update_data:

        category = (db.query(Category).filter(Category.id == update_data["category_id"], Category.is_active.is_(True))
        .first())

        if not category:
            raise ValueError("Category not found")

    # Check duplicate name if name is being changed
    if "name" in update_data:

        existing_product = (
            db.query(Product).filter(
                Product.name == update_data["name"],
                Product.id != product.id,
                Product.is_active.is_(True),
            )
            .first()
        )

        if existing_product:
            raise ValueError("Product already exists")

    for field, value in update_data.items():
        setattr(product, field, value)

    try:
        db.commit()
        db.refresh(product)

    except IntegrityError:
        db.rollback()
        raise ValueError("Product could not be updated")

    return product


def deactivate_product(db: Session, product: Product) -> Product:

    product.is_active = False

    db.commit()
    db.refresh(product)

    return product