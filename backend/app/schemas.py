from pydantic import BaseModel, Field
from typing import Literal


class UserCreate(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=6)
    phone: str | None = None
    
    
class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: str | None = None
    
    
class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    phone: str | None = None
    
    
class CategoryCreate(BaseModel):
    name: str = Field(min_length=2)


class CategoryResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    
    
class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    is_active: bool | None = None
    
    
class ProductCreate(BaseModel):
    name: str = Field(min_length=2)
    description: str | None = None
    image: str | None = None
    category_id: int
    is_veg: bool = True
    
    
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    image: str | None = None
    category_id: int
    is_veg: bool
    is_available: bool
    is_active: bool
    

class ProductVariantCreate(BaseModel):
    product_id: int
    size: Literal["Small", "Medium", "Large"]
    price: int = Field(gt=0)


class ProductVariantResponse(BaseModel):
    id: int
    product_id: int
    size: Literal["Small", "Medium", "Large"]
    price: int
    is_available: bool
    
class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    description: str | None = None
    image: str | None = None
    category_id: int | None = None
    is_veg: bool | None = None
    is_available: bool | None = None
    is_active: bool | None = None