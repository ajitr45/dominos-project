from sqlalchemy.orm import Session, selectinload

from app.models import (
    Cart,
    CartItem,
    Order,
    OrderItem,
    Address,
    OrderStatus,
    ProductVariant,
    Product,
)
from app.schemas import OrderCreate




def create_order(
    db: Session,
    user_id: int,
    order_data: OrderCreate,
):
    # Get active cart with products and variants
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
        raise ValueError("Active cart not found")

    if not cart.items:
        raise ValueError("Cart is empty")

    # Get selected address
    address = (
        db.query(Address)
        .filter(
            Address.id == order_data.address_id,
            Address.user_id == user_id,
            Address.is_active.is_(True),
        )
        .first()
    )

    if not address:
        raise ValueError("Address not found")

    subtotal = 0
    order_items = []

    for cart_item in cart.items:
        variant = cart_item.product_variant
        product = variant.product

        if not variant.is_active or not variant.is_available:
            raise ValueError(
                f"Product variant {variant.id} is not available"
            )

        if not product.is_active or not product.is_available:
            raise ValueError(
                f"Product {product.id} is not available"
            )

        item_subtotal = variant.price * cart_item.quantity
        subtotal += item_subtotal

        order_item = OrderItem(
            product_variant_id=variant.id,
            product_name=product.name,
            size_name=variant.size.name,
            unit_price=variant.price,
            quantity=cart_item.quantity,
            subtotal=item_subtotal,
        )

        order_items.append(order_item)

    delivery_fee = 0
    discount = 0
    tax = 0

    total_amount = subtotal + delivery_fee + tax - discount

    order = Order(
        user_id=user_id,
        address_id=address.id,
        subtotal=subtotal,
        delivery_fee=delivery_fee,
        discount=discount,
        tax=tax,
        total_amount=total_amount,
        recipient_name=address.recipient_name,
        phone=address.phone,
        address_line1=address.address_line1,
        address_line2=address.address_line2,
        landmark=address.landmark,
        city=address.city,
        state=address.state,
        postal_code=address.postal_code,
        items=order_items,
    )

    db.add(order)

    # Remove items from cart after order is prepared
    for cart_item in cart.items:
        db.delete(cart_item)

    db.commit()
    db.refresh(order)

    return order


def get_user_orders(db: Session, user_id: int):
    orders = (
        db.query(Order)
        .options(
            selectinload(Order.items)
        )
        .filter(
            Order.user_id == user_id
        )
        .order_by(
            Order.created_at.desc()
        )
        .all()
    )

    return orders


def get_user_order(
    db: Session,
    user_id: int,
    order_id: int,
):
    order = (
        db.query(Order)
        .options(
            selectinload(Order.items)
        )
        .filter(
            Order.id == order_id,
            Order.user_id == user_id,
        )
        .first()
    )

    return order

def update_order_status(db: Session, order_id: int, status: OrderStatus):
    order = (
        db.query(Order)
        .filter(Order.id == order_id)
        .first()
    )

    if not order:
        return None

    order.status = status

    db.commit()
    db.refresh(order)

    return order