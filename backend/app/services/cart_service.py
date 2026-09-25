from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload
from app.models import  Cart, CartItem, Product, ProductVariant
from app.schemas import CartItemCreate, CartItemUpdate


def get_or_create_active_cart(db: Session, user_id: int) -> Cart:
    
    # Find user's existing active cart
    cart = (
        db.query(Cart)
        .options(
            selectinload(Cart.items)
            .selectinload(CartItem.product_variant)
            .selectinload(ProductVariant.product)
        )
        .filter(
            Cart.user_id == user_id,
            Cart.is_active.is_(True),
        )
        .first()
    )

    if cart:
        return cart

    # Create a new active cart if one does not exist
    cart = Cart(user_id=user_id, is_active=True)

    try:
        db.add(cart)
        db.commit()
        db.refresh(cart)
    except IntegrityError:
        db.rollback()

        # Another request may have created the cart
        cart = (
            db.query(Cart)
            .options(
                selectinload(Cart.items)
                .selectinload(CartItem.product_variant)
                .selectinload(ProductVariant.product)
            )
            .filter(
                Cart.user_id == user_id,
                Cart.is_active.is_(True),
            )
            .first()
        )

        if not cart:
            raise ValueError("Active cart could not be created")

    return cart


def build_cart_response(cart: Cart) -> dict:
    """
    Build cart response with calculated prices.

    unit_price = current ProductVariant price
    subtotal = unit_price * quantity
    total_price = sum of all item subtotals
    """

    items = []
    total_price = 0

    for cart_item in cart.items:
        unit_price = cart_item.product_variant.price
        subtotal = unit_price * cart_item.quantity

        items.append(
            {
                "id": cart_item.id,
                "product_variant_id": cart_item.product_variant_id,
                "quantity": cart_item.quantity,
                "unit_price": unit_price,
                "subtotal": subtotal,
            }
        )

        total_price += subtotal

    return {
        "id": cart.id,
        "is_active": cart.is_active,
        "items": items,
        "total_price": total_price,
    }


def get_cart(db: Session, user_id: int) -> dict:
    cart = (
        db.query(Cart)
        .options(
            selectinload(Cart.items)
            .selectinload(CartItem.product_variant)
            .selectinload(ProductVariant.product)
        )
        .filter(
            Cart.user_id == user_id,
            Cart.is_active.is_(True),
        )
        .first()
    )

    if not cart:
        cart = get_or_create_active_cart(db, user_id)

    return build_cart_response(cart)


def add_item_to_cart(db: Session, user_id: int, item_data: CartItemCreate) -> dict:
    
    # Get or create user's active cart
    cart = get_or_create_active_cart(db, user_id)

    # Validate product variant and its product
    variant = (
        db.query(ProductVariant)
        .join(Product)
        .filter(
            ProductVariant.id == item_data.product_variant_id,
            ProductVariant.is_active.is_(True),
            ProductVariant.is_available.is_(True),
            Product.is_active.is_(True),
            Product.is_available.is_(True),
        )
        .first()
    )

    if not variant:
        raise ValueError("Product variant is not available")

    # Check if this variant already exists in cart
    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.cart_id == cart.id,
            CartItem.product_variant_id == variant.id,
        )
        .first()
    )

    if cart_item:
        
        # Existing item → increase quantity
        cart_item.quantity += item_data.quantity
    else:
        # New item → create cart item
        cart_item = CartItem(
            cart_id=cart.id,
            product_variant_id=variant.id,
            quantity=item_data.quantity,
        )

        db.add(cart_item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Cart item could not be added")

    return get_cart(db, user_id)


def update_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int,
    item_data: CartItemUpdate,
) -> dict:
    
    cart = get_or_create_active_cart(db, user_id)

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id,
        )
        .first()
    )

    if not cart_item:
        raise ValueError("Cart item not found")

    # Replace quantity
    cart_item.quantity = item_data.quantity

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Cart item could not be updated")

    return get_cart(db, user_id)


def remove_cart_item(
    db: Session,
    user_id: int,
    cart_item_id: int,
) -> dict:
    
    cart = get_or_create_active_cart(db, user_id)

    cart_item = (
        db.query(CartItem)
        .filter(
            CartItem.id == cart_item_id,
            CartItem.cart_id == cart.id,
        )
        .first()
    )

    if not cart_item:
        raise ValueError("Cart item not found")

    db.delete(cart_item)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise ValueError("Cart item could not be removed")

    return get_cart(db, user_id)