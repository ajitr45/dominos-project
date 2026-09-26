from pydantic import BaseModel, Field, ConfigDict
from app.models import OrderStatus


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
    

class AddressCreate(BaseModel):
    label: str = Field(min_length=2, max_length=30)
    recipient_name: str = Field(min_length=2, max_length=100)
    phone: str = Field(min_length=10, max_length=20)
    address_line1: str = Field(min_length=5, max_length=255)
    address_line2: str | None = Field(default=None, max_length=255)
    landmark: str | None = Field(default=None, max_length=150)
    city: str = Field(min_length=2, max_length=100)
    state: str = Field(min_length=2, max_length=100)
    postal_code: str = Field(min_length=4, max_length=10)
    is_default: bool = False


class AddressUpdate(BaseModel):
    label: str | None = Field(default=None, min_length=2, max_length=30)
    recipient_name: str | None = Field(default=None, min_length=2, max_length=100)
    phone: str | None = Field(default=None, min_length=10, max_length=20)
    address_line1: str | None = Field(default=None, min_length=5, max_length=255,)
    address_line2: str | None = Field(default=None, max_length=255)
    landmark: str | None = Field(default=None, max_length=150)
    city: str | None = Field(default=None, min_length=2, max_length=100)
    state: str | None = Field(default=None, min_length=2, max_length=100)
    postal_code: str | None = Field(default=None, min_length=4, max_length=10)
    is_default: bool | None = None


class AddressResponse(BaseModel):
    id: int
    label: str
    recipient_name: str
    phone: str
    address_line1: str
    address_line2: str | None
    landmark: str | None
    city: str
    state: str
    postal_code: str
    is_default: bool
    is_active: bool

    model_config = ConfigDict(from_attributes=True)
    
    
#---------------Order Record----------------#

class OrderCreate(BaseModel):
    address_id: int = Field(gt=0)
    

class OrderItemResponse(BaseModel):
    id: int
    product_variant_id: int
    product_name: str
    size_name: str
    unit_price: int
    quantity: int
    subtotal: int

    model_config = ConfigDict(from_attributes=True)


class OrderResponse(BaseModel):
    id: int
    address_id: int
    status: str

    subtotal: int
    delivery_fee: int
    discount: int
    tax: int
    total_amount: int

    recipient_name: str
    phone: str
    address_line1: str
    address_line2: str | None
    landmark: str | None
    city: str
    state: str
    postal_code: str

    items: list[OrderItemResponse] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)
    
    
class OrderStatusUpdate(BaseModel):
    status: OrderStatus