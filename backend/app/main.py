from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models import User, Category, Product, ProductVariant
from app.schemas import (
    UserCreate,
    UserResponse,
    UserUpdate,
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


@app.post("/categories", response_model=CategoryResponse)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    
    db_category = Category(name=category.name)

    db.add(db_category)
    db.commit()
    db.refresh(db_category)

    return db_category


@app.get("/categories", response_model=list[CategoryResponse])
def get_categories(db: Session = Depends(get_db)):
    
    categories = db.query(Category).all()

    return categories


@app.get("/categories/{category_id}", response_model=CategoryResponse)
def get_category(category_id: int, db: Session = Depends(get_db)):
    
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@app.put("/categories/{category_id}", response_model=CategoryResponse)
def update_category(category_id: int, category_data: CategoryUpdate, db: Session = Depends(get_db)):
    
    category = db.query(Category).filter(Category.id == category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    if category_data.name is not None:
        category.name = category_data.name

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

    db.delete(category)
    db.commit()

    return {"message": "Category deleted successfully"}


# Products

@app.post("/products", response_model=ProductResponse)
def create_product(product: ProductCreate, db: Session = Depends(get_db)):
    # Check category exists
    category = db.query(Category).filter(Category.id == product.category_id).first()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

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
    
    products = db.query(Product).all()

    return products


@app.get("/products/{product_id}", response_model=ProductResponse)
def get_product(product_id: int, db: Session = Depends(get_db)):
    
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.put("/products/{product_id}", response_model=ProductResponse)
def update_product(product_id: int, product_data: ProductUpdate, db: Session = Depends(get_db)):
    
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.description is not None:
        product.description = product_data.description

    if product_data.image is not None:
        product.image = product_data.image

    if product_data.category_id is not None:

        category = db.query(Category).filter(
            Category.id == product_data.category_id
        ).first()

        if not category:
            raise HTTPException(
                status_code=404,
                detail="Category not found"
            )

        product.category_id = product_data.category_id

    if product_data.is_veg is not None:
        product.is_veg = product_data.is_veg

    if product_data.is_available is not None:
        product.is_available = product_data.is_available

    if product_data.is_active is not None:
        product.is_active = product_data.is_active

    db.commit()
    db.refresh(product)

    return product


@app.delete("/products/{product_id}")
def delete_product(product_id: int, db: Session = Depends(get_db)):
    
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db.delete(product)
    db.commit()

    return {"message": "Product deleted successfully"}


# Product Variants

@app.post("/product-variants", response_model=ProductVariantResponse)
def create_product_variant(variant: ProductVariantCreate, db: Session = Depends(get_db)):
    # Check product exists
    product = db.query(Product).filter(Product.id == variant.product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    db_variant = ProductVariant(
        product_id=variant.product_id,
        size=variant.size,
        price=variant.price
    )

    db.add(db_variant)
    db.commit()
    db.refresh(db_variant)

    return db_variant


@app.get("/product-variants", response_model=list[ProductVariantResponse])

def get_product_variants(db: Session = Depends(get_db)):
    variants = db.query(ProductVariant).all()

    return variants


@app.get("/product-variants/{variant_id}", response_model=ProductVariantResponse)
def get_product_variant(variant_id: int, db: Session = Depends(get_db)):
    
    variant = db.query(ProductVariant).filter(ProductVariant.id == variant_id).first()

    if not variant:
        raise HTTPException(status_code=404, detail="Product variant not found")

    return variant


@app.put(
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
        raise HTTPException(status_code=404, detail="Product variant not found")

    if variant_data.size is not None:
        variant.size = variant_data.size

    if variant_data.price is not None:
        variant.price = variant_data.price

    if variant_data.is_available is not None:
        variant.is_available = variant_data.is_available

    db.commit()
    db.refresh(variant)

    return variant

