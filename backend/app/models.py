from datetime import datetime
from enum import Enum
from sqlalchemy import Column, DateTime, Integer, String, Boolean, ForeignKey, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship
from app.database import Base


class UserRole(str, Enum):
    CUSTOMER = "customer"
    ADMIN = "admin"
    DELIVERY_BOY = "delivery_boy"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), nullable=False, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    phone = Column(String(20), unique=True, nullable=True)

    role = Column(
        SQLEnum(
            UserRole,
            values_callable=lambda enum_class: [member.value for member in enum_class],
        ),
        nullable=False,
        default=UserRole.CUSTOMER,
    )

    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow,)


class Size(Base):
    __tablename__ = "sizes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    variants = relationship("ProductVariant", back_populates="size",)


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow,)
    products = relationship("Product", back_populates="category",)


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    image = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    is_veg = Column(Boolean, nullable=False, default=True)
    is_available = Column(Boolean, nullable=False, default=True,)
    is_active = Column(Boolean, nullable=False, default=True)
    category = relationship("Category", back_populates="products")
    variants = relationship("ProductVariant", back_populates="product")


class ProductVariant(Base):
    __tablename__ = "product_variants"

    __table_args__ = (
        UniqueConstraint("product_id","size_id",
            name="uq_product_variants_product_size"),
    )

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False,)
    size_id = Column(Integer, ForeignKey("sizes.id"), nullable=False,)
    price = Column(Integer, nullable=False)
    is_available = Column( Boolean, nullable=False, default=True,)
    is_active = Column(Boolean, nullable=False,default=True,)
    product = relationship("Product", back_populates="variants")
    size = relationship("Size", back_populates="variants",)