from sqlalchemy.orm import Session

from app.models import Payment, PaymentStatus, Order
from app.schemas import PaymentCreate, PaymentUpdate


def create_payment(
    db: Session,
    user_id: int,
    payment_data: PaymentCreate,
):
    # Get user's order
    order = (
        db.query(Order)
        .filter(
            Order.id == payment_data.order_id,
            Order.user_id == user_id,
        )
        .first()
    )

    if not order:
        raise ValueError("Order not found")

    # Prevent payment for cancelled orders
    if order.status == "cancelled":
        raise ValueError(
            "Cannot create payment for cancelled order"
        )

    # Prevent duplicate payment
    existing_payment = (
        db.query(Payment)
        .filter(
            Payment.order_id == order.id,
        )
        .first()
    )

    if existing_payment:
        raise ValueError(
            "Payment already exists for this order"
        )

    # Create payment
    payment = Payment(
        order_id=order.id,
        user_id=user_id,
        amount=order.total_amount,
        method=payment_data.method,
        status=PaymentStatus.PENDING,
    )

    try:
        db.add(payment)
        db.commit()
        db.refresh(payment)

    except Exception:
        db.rollback()
        raise

    return payment


def get_user_payments(db: Session, user_id: int):
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .all()
    )

    return payments

def get_payment(
    db: Session,
    user_id: int,
    payment_id: int,
):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.user_id == user_id,
        )
        .first()
    )

    return payment


def update_payment_status(
    db: Session,
    payment_id: int,
    payment_data: PaymentUpdate,
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        return None

    current_status = payment.status
    new_status = payment_data.status

    allowed_transitions = {
        PaymentStatus.PENDING: {
            PaymentStatus.PAID,
            PaymentStatus.FAILED,
        },
        PaymentStatus.PAID: {
            PaymentStatus.REFUNDED,
        },
        PaymentStatus.FAILED: set(),
        PaymentStatus.REFUNDED: set(),
    }

    if current_status not in allowed_transitions:
        raise ValueError("Invalid current payment status")

    if new_status not in allowed_transitions[current_status]:
        raise ValueError(
            f"Cannot change payment status from "
            f"{current_status.value} to {new_status.value}"
        )

    payment.status = new_status

    try:
        db.commit()
        db.refresh(payment)
    except Exception:
        db.rollback()
        raise

    return payment