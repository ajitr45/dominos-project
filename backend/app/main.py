from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload

from app.database import SessionLocal
from app.models import User, Category, Product, ProductVariant, Size
from app.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
    SizeCreate,
    SizeResponse,
    SizeUpdate,
    CategoryCreate,
    CategoryResponse,
    CategoryUpdate,
    ProductCreate,
    ProductResponse,
    ProductVariantCreate,
    ProductVariantResponse,
    ProductVariantUpdate,
    ProductUpdate,
)


app = FastAPI()


# Database Session
def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

@app.get("/")
def home():
    return {"message": "Welcome to Domino's Food Ordering API"}


@app.post("/users")
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    
    db_user = User(
        username=user.username,
        email=user.email,
        password=user.password,
        phone=user.phone
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    return {
        "id": db_user.id,
        "username": db_user.username,
        "email": db_user.email,
        "phone": db_user.phone
    }


@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    
    users = db.query(User).all()

    return users


@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return user


@app.put("/users/{user_id}", response_model=UserResponse)
def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user_data.username is not None:
        user.username = user_data.username

    if user_data.email is not None:
        user.email = user_data.email

    if user_data.phone is not None:
        user.phone = user_data.phone

    db.commit()
    db.refresh(user)

    return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted successfully"}


@app.post("/sizes", response_model=SizeResponse, status_code=201)
def create_size(size: SizeCreate, db: Session = Depends(get_db)):
    
    existing_size = db.query(Size).filter(Size.name == size.name).first()

    if existing_size:
        raise HTTPException(status_code=409, detail="Size already exists")

    db_size = Size(name=size.name)

    db.add(db_size)
    db.commit()
    db.refresh(db_size)

    return db_size

@app.get("/sizes", response_model=list[SizeResponse])
def get_sizes(db: Session = Depends(get_db)):

    sizes = db.query(Size).filter(Size.is_active == True).all()

    return sizes


@app.get("/sizes/{size_id}", response_model=SizeResponse)
def get_size(size_id: int, db: Session = Depends(get_db)):
    
    size = db.query(Size).filter(Size.id == size_id, Size.is_active == True).first()

    if not size:
        raise HTTPException(status_code=404, detail="Size not found")

    return size


@app.patch("/sizes/{size_id}", response_model=SizeResponse)
def update_size(size_id: int, size_data: SizeUpdate,db: Session = Depends(get_db)):
    
    size = db.query(Size).filter(Size.id == size_id).first()

    if not size:
        raise HTTPException(status_code=404, detail="Size not found")

    if size_data.name is not None:
        existing_size = db.query(Size).filter(
            Size.name == size_data.name,
            Size.id != size_id
        ).first()

        if existing_size:
            raise HTTPException(status_code=409, detail="Size already exists")

        size.name = size_data.name

    if size_data.is_active is not None:
        size.is_active = size_data.is_active

    db.commit()
    db.refresh(size)

    return size



@app.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    
    db_category = Category(name=category.name)

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


@app.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    
    categories = (db.query(Category).filter(Category.is_active == True).order_by(Category.id).all())

    return categories


@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    
    category = db.query(Category).filter(Category.id == category_id, Category.is_active == True).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@app.patch("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Check for duplicate category name
    if category_data.name is not None:
        existing_category = db.query(Category).filter(Category.name == category_data.name,
        Category.id != category_id).first()

        if existing_category:
            raise HTTPException(status_code=409, detail="Category name already exists")

        category.name = category_data.name

    # Update active status
    if category_data.is_active is not None:
        category.is_active = category_data.is_active

    db.commit()
    db.refresh(category)

    return category


@app.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    # Deactivate the category
    category.is_active = False

    # Deactivate all products under this category
    for product in category.products:
        product.is_active = False
        product.is_available = False

        # Deactivate all variants of the product
        for variant in product.variants:
            variant.is_active = False
            variant.is_available = False

    db.commit()

    return {"message": "Category deactivated successfully"}


# Products

@app.post("/products", response_model=ProductResponse, status_code=201)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    
    # Check if the category exists and is active
    category = db.query(Category).filter(Category.id == product.category_id, Category.is_active == True
    ).first()

    if not category:
        raise HTTPException(status_code=404, detail="Active category not found")

    # Check for duplicate active product name
    existing_product = db.query(Product).filter(Product.name == product.name, Product.is_active == True
    ).first()

    if existing_product:
        raise HTTPException(status_code=409, detail="Product with this name already exists")

    # Create the product
    db_product = Product(
        name=product.name,
        description=product.description,
        image=product.image,
        category_id=product.category_id,
        is_veg=product.is_veg
    )

    db.add(db_product)
    db.commit()
    db.refresh(db_product)

    return db_product


@app.get("/products", response_model=list[ProductResponse])
def get_products(db: Session = Depends(get_db)):
    
    products = db.query(Product).options(selectinload(Product.variants).selectinload(ProductVariant.size)
    ).filter(Product.is_active == True, Product.is_available == True).all()
    
    for product in products:
        
        product.variants = [variant for variant in product.variants if variant.is_active and variant.is_available]

    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product).options(selectinload(Product.variants).selectinload(ProductVariant.size))
        .filter(Product.id == product_id, Product.is_active == True, Product.is_available == True).first()
    )

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.variants = [variant for variant in product.variants if variant.is_active and 
    variant.is_available]

    return product


@app.patch("/product-variants/{variant_id}", response_model=ProductVariantResponse)
def update_product_variant(variant_id: int, variant_data: ProductVariantUpdate, db: Session = Depends(get_db)):
    
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Product variant not found")

    if variant_data.size_id is not None:

        size = db.query(Size).filter(Size.id == variant_data.size_id, Size.is_active == True).first()

        if not size:
            raise HTTPException(status_code=404, detail="Size not found")

        existing_variant = db.query(ProductVariant).filter(
            ProductVariant.product_id == variant.product_id,
            ProductVariant.size_id == variant_data.size_id,
            ProductVariant.id != variant.id
        ).first()

        if existing_variant:
            raise HTTPException(status_code=409, detail="This size already exists for this product")

        variant.size_id = variant_data.size_id

    if variant_data.price is not None:
        variant.price = variant_data.price

    if variant_data.is_available is not None:
        variant.is_available = variant_data.is_available

    if variant_data.is_active is not None:
        variant.is_active = variant_data.is_active

    db.commit()
    db.refresh(variant)

    return variant


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


# Product Variants

@app.post("/product-variants", response_model=ProductVariantResponse, status_code=201)
def create_product_variant(variant: ProductVariantCreate, db: Session = Depends(get_db)):
    
    # Check product exists and is active
    product = db.query(Product).filter(Product.id == variant.product_id, Product.is_active == True).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    # Check size exists and is active
    size = db.query(Size).filter(
        Size.id == variant.size_id,
        Size.is_active == True
    ).first()

    if not size:
        raise HTTPException(status_code=404, detail="Size not found")

    # Prevent duplicate product + size
    existing_variant = db.query(ProductVariant).filter(
        ProductVariant.product_id == variant.product_id,
        ProductVariant.size_id == variant.size_id
    ).first()

    if existing_variant:
        raise HTTPException(status_code=409, detail="This size already exists for this product")

    # Create variant
    db_variant = ProductVariant(
        product_id=variant.product_id,
        size_id=variant.size_id,
        price=variant.price
    )

    db.add(db_variant)
    db.commit()
    db.refresh(db_variant)

    return db_variant


@app.get("/product-variants", response_model=list[ProductVariantResponse])
def get_product_variants(db: Session = Depends(get_db)):

    variants = (db.query(ProductVariant).options(selectinload(ProductVariant.size))
        .filter(ProductVariant.is_active == True, ProductVariant.is_available == True).all()
    )

    return variants


@app.get("/product-variants/{variant_id}", response_model=ProductVariantResponse)
def get_product_variant(variant_id: int, db: Session = Depends(get_db)):
    
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id, Product.is_active == True,
        ProductVariant.is_available == True).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Product variant currently unavailable")

    return variant


@app.patch(
    "/product-variants/{variant_id}",
    response_model=ProductVariantResponse
)
def update_product_variant(
    variant_id: int,
    variant_data: ProductVariantUpdate,
    db: Session = Depends(get_db)
):
    variant = db.query(ProductVariant).filter(
        ProductVariant.id == variant_id
    ).first()

    if not variant:
        raise HTTPException(
            status_code=404,
            detail="Product variant not found"
        )

    if variant_data.size_id is not None:

        size = db.query(Size).filter(
            Size.id == variant_data.size_id,
            Size.is_active == True
        ).first()

        if not size:
            raise HTTPException(
                status_code=404,
                detail="Size not found"
            )

        variant.size_id = variant_data.size_id

    if variant_data.price is not None:
        variant.price = variant_data.price

    if variant_data.is_available is not None:
        variant.is_available = variant_data.is_available

    if variant_data.is_active is not None:
        variant.is_active = variant_data.is_active

    db.commit()
    db.refresh(variant)

    return variant


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.is_active = False
    product.is_available = False

    # Product ke variants bhi deactivate
    for variant in product.variants:
        variant.is_active = False
        variant.is_available = False

    db.commit()

    return {"message": "Product deactivated successfully"}
