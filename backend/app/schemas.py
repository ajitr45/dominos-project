from pydantic import BaseModel, Field, ConfigDict


# =========================
# Users
# =========================

class UserCreate(BaseModel):
    username: str
    email: str
    password: str = Field(min_length=6)
    phone: str 


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    phone: str 

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    phone: str | None = None


# =========================
# Sizes
# =========================

class SizeCreate(BaseModel):
    name: str = Field(
        min_length=2,
        max_length=50
    )


class SizeResponse(BaseModel):
    id: int
    name: str
    is_active: bool

    model_config = ConfigDict(from_attributes=True)


class SizeUpdate(BaseModel):
    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=50
    )
    is_active: bool | None = None


# =========================
# Categories
# =========================

class CategoryCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=100)
    description: str | None = Field(default=None, max_length=500)


class CategoryResponse(BaseModel):
    id: int
    name: str
    description: str | None
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
    
    
# =========================
# Products
# =========================

class ProductCreate(BaseModel):
    name: str = Field(min_length=2)
    description: str | None = Field(default=None, max_length=500)
    image: str | None = None
    category_id: int = Field(gt=0)
    is_veg: bool = True


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2)
    description: str | None = None
    image: str | None = None
    category_id: int | None = Field(default=None, gt=0)
    is_veg: bool | None = None
    is_available: bool | None = None
 
 
class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None = None
    image: str | None = None
    category_id: int
    is_veg: bool
    is_available: bool
    is_active: bool
    variants: list["ProductVariantResponse"] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# =========================
# Product Variants
# =========================

class ProductVariantCreate(BaseModel):
    product_id: int
    size_id: int
    price: int = Field(gt=0)


class ProductVariantUpdate(BaseModel):
    size_id: int | None = None
    price: int | None = Field(default=None, gt=0)
    is_available: bool | None = None
    is_active: bool | None = None


class ProductVariantSizeResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ProductVariantResponse(BaseModel):
    id: int
    product_id: int
    size: ProductVariantSizeResponse
    price: int
    is_available: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)



    
## Login ##

class LoginRequest(BaseModel):
    identifier: str
    password: str = Field(min_length=6)    


#Cart and Cartitem


class CartItemCreate(BaseModel):
    product_variant_id: int = Field(gt=0)
    quantity: int = Field(default=1, ge=1)


class CartItemUpdate(BaseModel):
    quantity: int = Field(ge=1)


class CartItemResponse(BaseModel):
    id: int
    product_variant_id: int
    quantity: int
    unit_price: int
    subtotal: int

    model_config = ConfigDict(from_attributes=True)


class CartResponse(BaseModel):
    id: int
    is_active: bool
    items: list[CartItemResponse] = Field(default_factory=list)
    total_price: int

    model_config = ConfigDict(from_attributes=True)