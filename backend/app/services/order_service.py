from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload
from app.models import (Cart, CartItem, Order, OrderItem, Address, OrderStatus, ProductVariant, Product, User, UserRole)
from app.schemas import OrderCreate


def create_order(db: Session, user_id: int, order_data: OrderCreate):
    # Get user's active cart with product and variant details
    cart = (
        db.query(Cart)
        .options(
            selectinload(Cart.items)
            .selectinload(CartItem.product_variant)
            .selectinload(ProductVariant.product)
        )
        .filter(Cart.user_id == user_id, Cart.is_active.is_(True))
        .first()
    )

    if not cart:
        raise ValueError("Active cart not found")

    if not cart.items:
        raise ValueError("Cart is empty")

    # Get user's active address
    address = (db.query(Address)
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

        # Validate variant availability
        if not variant.is_active or not variant.is_available:
            raise ValueError(f"Product variant {variant.id} is not available")

        # Validate product availability
        if not product.is_active or not product.is_available:
            raise ValueError(f"Product {product.id} is not available")

        # Calculate item subtotal
        item_subtotal = variant.price * cart_item.quantity
        subtotal += item_subtotal

        # Create order item snapshot
        order_item = OrderItem(
            product_variant_id=variant.id,
            product_name=product.name,
            size_name=variant.size.name,
            unit_price=variant.price,
            quantity=cart_item.quantity,
            subtotal=item_subtotal,
        )

        order_items.append(order_item)

    # Pricing rules
    delivery_fee = 0
    discount = 0
    tax = 0

    total_amount = (
        subtotal
        + delivery_fee
        + tax
        - discount
    )

    # Create order with address snapshot
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

    try:
        db.add(order)

        # Clear cart after preparing the order
        for cart_item in cart.items:
            db.delete(cart_item)

        # Commit order creation and cart clearing together
        db.commit()
        db.refresh(order)

    except Exception:
        db.rollback()
        raise

    created_order = order

    return created_order


def get_user_orders(db: Session, user_id: int):
    orders = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.user_id == user_id)
        .order_by(Order.created_at.desc())
        .all()
    )

    user_orders = orders

    return user_orders


def get_user_order(db: Session, user_id: int, order_id: int):
    order = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.id == order_id, Order.user_id == user_id)
        .first()
    )

    user_order = order

    return user_order


def get_all_orders(db: Session):
    orders = (
        db.query(Order)
        .options(selectinload(Order.items))
        .order_by(Order.created_at.desc())
        .all()
    )

    all_orders = orders

    return all_orders


def get_order_by_id(db: Session, order_id: int,):
    order = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(Order.id == order_id)
        .first()
    )

    order_by_id = order

    return order_by_id


def update_order_status(db: Session, order_id: int, status: OrderStatus):
    order = (db.query(Order).filter(Order.id == order_id).first())

    if not order:
        return None

    allowed_transitions = {
        OrderStatus.PENDING: {
            OrderStatus.CONFIRMED,
            OrderStatus.CANCELLED,
        },
        OrderStatus.CONFIRMED: {
            OrderStatus.PREPARING,
            OrderStatus.CANCELLED,
        },
        OrderStatus.PREPARING: {
            OrderStatus.OUT_FOR_DELIVERY,
        },
        OrderStatus.OUT_FOR_DELIVERY: {
            OrderStatus.DELIVERED,
        },
        OrderStatus.DELIVERED: set(),
        OrderStatus.CANCELLED: set(),
    }

    current_status = order.status

    if current_status not in allowed_transitions:
        raise ValueError("Invalid current order status")

    if status not in allowed_transitions[current_status]:
        raise ValueError(
            f"Cannot change order status "
            f"from {current_status.value} to {status.value}"
        )

    order.status = status

    try:
        db.commit()
        db.refresh(order)

    except Exception:
        db.rollback()
        raise

    updated_order = order

    return updated_order


#-------------Assigned delivery_boy---------------------------#

def assign_delivery_boy(db: Session, order_id: int, delivery_boy_id: int | None):
    
    order = (db.query(Order).filter(Order.id == order_id).first())

    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    # Delivered and cancelled orders cannot be assigned or reassigned
    if order.status in (
        OrderStatus.DELIVERED,
        OrderStatus.CANCELLED,
    ):
        raise HTTPException(
            status_code=400,
            detail="Cannot assign delivery boy to a delivered or cancelled order",
        )

    # Unassign delivery boy
    if delivery_boy_id is None:
        order.delivery_boy_id = None

        try:
            db.commit()
            db.refresh(order)

        except Exception:
            db.rollback()
            raise

        updated_order = order

        return updated_order

    # Find delivery boy
    delivery_boy = (db.query(User).filter(User.id == delivery_boy_id).first())

    if not delivery_boy:
        raise HTTPException(status_code=404, detail="Delivery boy not found")

    # Validate user role
    if delivery_boy.role != UserRole.DELIVERY_BOY:
        raise HTTPException(status_code=400, detail="Selected user is not a delivery boy")

    # Validate account status
    if not delivery_boy.is_active:
        raise HTTPException(status_code=400, detail="Delivery boy account is inactive")

    # Assign or reassign delivery boy
    order.delivery_boy_id = delivery_boy.id

    try:
        db.commit()
        db.refresh(order)

    except Exception:
        db.rollback()
        raise

    assigned_order = order

    return assigned_order



def get_delivery_boy_orders(db: Session, delivery_boy_id: int):
    orders = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(
            Order.delivery_boy_id == delivery_boy_id,
            Order.status.notin_(
                [
                    OrderStatus.DELIVERED,
                    OrderStatus.CANCELLED,
                ]
            ),
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    delivery_boy_orders = orders

    return delivery_boy_orders


def get_delivery_boy_order_history(db: Session, delivery_boy_id: int):
    orders = (
        db.query(Order)
        .options(selectinload(Order.items))
        .filter(
            Order.delivery_boy_id == delivery_boy_id,
            Order.status.in_(
                [
                    OrderStatus.DELIVERED,
                    OrderStatus.CANCELLED,
                ]
            ),
        )
        .order_by(Order.created_at.desc())
        .all()
    )

    delivery_boy_order_history = orders

    return delivery_boy_order_history


def update_delivery_order_status(
    db: Session,
    order_id: int,
    delivery_boy_id: int,
    status: OrderStatus,
):
    order = (
        db.query(Order)
        .filter(
            Order.id == order_id,
            Order.delivery_boy_id == delivery_boy_id,
        )
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Assigned order not found",
        )

    allowed_transitions = {
        OrderStatus.PREPARING: {
            OrderStatus.OUT_FOR_DELIVERY,
        },
        OrderStatus.OUT_FOR_DELIVERY: {
            OrderStatus.DELIVERED,
        },
    }

    current_status = order.status

    if current_status not in allowed_transitions:
        raise HTTPException(
            status_code=400,
            detail="Delivery boy cannot update this order status",
        )

    if status not in allowed_transitions[current_status]:
        raise HTTPException(
            status_code=400,
            detail=(
                f"Cannot change order status "
                f"from {current_status.value} to {status.value}"
            ),
        )

    order.status = status

    try:
        db.commit()
        db.refresh(order)

    except Exception:
        db.rollback()
        raise

    updated_order = order

    return updated_order