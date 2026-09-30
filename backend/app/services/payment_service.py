import json

import razorpay
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import (
    RAZORPAY_KEY_ID,
    RAZORPAY_KEY_SECRET,
    RAZORPAY_WEBHOOK_SECRET,
)
from app.models import (
    Payment,
    PaymentMethod,
    PaymentStatus,
    Order,
    OrderStatus,
)
from app.schemas import PaymentCreate, PaymentUpdate


razorpay_client = razorpay.Client(
    auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET)
)


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

    # Payment cannot be created for cancelled orders
    if order.status == OrderStatus.CANCELLED:
        raise ValueError(
            "Cannot create payment for cancelled order"
        )

    # Payment cannot be created after delivery
    if order.status == OrderStatus.DELIVERED:
        raise ValueError(
            "Cannot create payment for delivered order"
        )

    # Get existing payment for this order
    existing_payment = (
        db.query(Payment)
        .filter(Payment.order_id == order.id)
        .first()
    )

    # --------------------------------------------------
    # COD PAYMENT
    # --------------------------------------------------

    if payment_data.method == PaymentMethod.COD:

        # COD payment already exists
        if existing_payment:
            raise ValueError(
                "Payment already exists for this order"
            )

        payment = Payment(
            order_id=order.id,
            user_id=user_id,
            amount=order.total_amount,
            method=PaymentMethod.COD,
            status=PaymentStatus.PENDING,
        )

        # COD order becomes confirmed after payment method selection
        order.status = OrderStatus.CONFIRMED

        try:
            db.add(payment)
            db.commit()
            db.refresh(payment)

        except IntegrityError as exc:
            db.rollback()
            raise ValueError(
                "Payment could not be created"
            ) from exc

        created_payment = payment

        return created_payment

    # --------------------------------------------------
    # ONLINE PAYMENT - RAZORPAY
    # --------------------------------------------------

    if payment_data.method == PaymentMethod.ONLINE:

        # Existing COD payment cannot be converted to online
        if (
            existing_payment
            and existing_payment.method == PaymentMethod.COD
        ):
            raise ValueError(
                "COD payment already exists for this order"
            )

        # Existing online payment
        if existing_payment:

            # Only FAILED online payments can be retried
            if existing_payment.status != PaymentStatus.FAILED:
                raise ValueError(
                    "Payment already exists for this order"
                )

            payment = existing_payment

        else:
            payment = None

        razorpay_order_data = {
            "amount": order.total_amount * 100,
            "currency": "INR",
            "receipt": f"order_{order.id}",
        }

        # Create a new Razorpay order
        try:
            razorpay_order = razorpay_client.order.create(
                data=razorpay_order_data
            )

        except Exception as exc:
            raise ValueError(
                "Unable to create Razorpay order"
            ) from exc

        # --------------------------------------------------
        # RETRY FAILED PAYMENT
        # --------------------------------------------------

        if payment:

            # Clear old failed transaction information
            payment.amount = order.total_amount
            payment.razorpay_order_id = razorpay_order["id"]
            payment.razorpay_payment_id = None
            payment.razorpay_signature = None
            payment.transaction_id = None
            payment.status = PaymentStatus.PENDING

        # --------------------------------------------------
        # FIRST ONLINE PAYMENT
        # --------------------------------------------------

        else:

            payment = Payment(
                order_id=order.id,
                user_id=user_id,
                amount=order.total_amount,
                method=PaymentMethod.ONLINE,
                status=PaymentStatus.PENDING,
                razorpay_order_id=razorpay_order["id"],
            )

            db.add(payment)

        try:
            db.commit()
            db.refresh(payment)

        except IntegrityError as exc:
            db.rollback()
            raise ValueError(
                "Payment could not be created"
            ) from exc

        payment_data_response = {
            "payment_id": payment.id,
            "order_id": order.id,
            "amount": payment.amount,
            "currency": "INR",
            "method": payment.method,
            "status": payment.status,
            "razorpay_key_id": RAZORPAY_KEY_ID,
            "razorpay_order_id": payment.razorpay_order_id,
        }

        return payment_data_response

    raise ValueError("Invalid payment method")


def verify_razorpay_payment(
    db: Session,
    user_id: int,
    payment_id: int,
    razorpay_payment_id: str,
    razorpay_order_id: str,
    razorpay_signature: str,
):
    payment = (
        db.query(Payment)
        .filter(
            Payment.id == payment_id,
            Payment.user_id == user_id,
            Payment.method == PaymentMethod.ONLINE,
        )
        .first()
    )

    if not payment:
        raise ValueError("Payment not found")

    if payment.status != PaymentStatus.PENDING:
        raise ValueError(
            "Payment is not in pending state"
        )

    if payment.razorpay_order_id != razorpay_order_id:
        raise ValueError(
            "Razorpay order ID does not match"
        )

    try:
        razorpay_client.utility.verify_payment_signature(
            {
                "razorpay_payment_id": razorpay_payment_id,
                "razorpay_order_id": razorpay_order_id,
                "razorpay_signature": razorpay_signature,
            }
        )

    except Exception as exc:
        raise ValueError(
            "Invalid Razorpay payment signature"
        ) from exc

    payment.razorpay_payment_id = razorpay_payment_id
    payment.razorpay_signature = razorpay_signature
    payment.transaction_id = razorpay_payment_id
    payment.status = PaymentStatus.PAID

    payment.order.status = OrderStatus.CONFIRMED

    try:
        db.commit()
        db.refresh(payment)

    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "Payment verification could not be completed"
        ) from exc

    verified_payment = payment

    return verified_payment


def get_user_payments(
    db: Session,
    user_id: int,
):
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == user_id)
        .order_by(Payment.created_at.desc())
        .all()
    )

    user_payments = payments

    return user_payments


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

    user_payment = payment

    return user_payment


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

    # Online payment cannot be manually marked as paid
    if (
        payment.method == PaymentMethod.ONLINE
        and payment_data.status == PaymentStatus.PAID
    ):
        raise ValueError(
            "Online payment must be verified through Razorpay"
        )

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
        raise ValueError(
            "Invalid current payment status"
        )

    if new_status not in allowed_transitions[current_status]:
        raise ValueError(
            f"Cannot change payment status "
            f"from {current_status.value} "
            f"to {new_status.value}"
        )

    payment.status = new_status

    try:
        db.commit()
        db.refresh(payment)

    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "Payment status could not be updated"
        ) from exc

    updated_payment = payment

    return updated_payment


def mark_cod_payment_paid(
    db: Session,
    payment_id: int,
    delivery_boy_id: int,
):
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id)
        .first()
    )

    if not payment:
        raise ValueError("Payment not found")

    if payment.method != PaymentMethod.COD:
        raise ValueError(
            "Only COD payment can be marked as paid"
        )

    if payment.status != PaymentStatus.PENDING:
        raise ValueError(
            "COD payment is not in pending state"
        )

    order = (
        db.query(Order)
        .filter(
            Order.id == payment.order_id,
            Order.delivery_boy_id == delivery_boy_id,
        )
        .first()
    )

    if not order:
        raise ValueError(
            "Order is not assigned to this delivery boy"
        )

    if order.status != OrderStatus.OUT_FOR_DELIVERY:
        raise ValueError(
            "COD payment can be marked as paid "
            "only when order is out for delivery"
        )

    payment.status = PaymentStatus.PAID

    try:
        db.commit()
        db.refresh(payment)

    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "COD payment could not be marked as paid"
        ) from exc

    paid_payment = payment

    return paid_payment


def process_razorpay_webhook(
    db: Session,
    payload: str,
    webhook_signature: str,
):
    # Verify webhook signature
    try:
        razorpay_client.utility.verify_webhook_signature(
            payload,
            webhook_signature,
            RAZORPAY_WEBHOOK_SECRET,
        )

    except Exception as exc:
        raise ValueError(
            "Invalid Razorpay webhook signature"
        ) from exc

    try:
        webhook_data = json.loads(payload)

    except json.JSONDecodeError as exc:
        raise ValueError(
            "Invalid webhook payload"
        ) from exc

    event = webhook_data.get("event")

    payment_entity = (
        webhook_data
        .get("payload", {})
        .get("payment", {})
        .get("entity", {})
    )

    razorpay_payment_id = payment_entity.get("id")
    razorpay_order_id = payment_entity.get("order_id")

    if not razorpay_payment_id or not razorpay_order_id:
        raise ValueError(
            "Invalid Razorpay webhook payload"
        )

    payment = (
        db.query(Payment)
        .filter(
            Payment.razorpay_order_id
            == razorpay_order_id
        )
        .first()
    )

    if not payment:
        raise ValueError("Payment not found")

    # Ignore duplicate successful webhook events
    if payment.status == PaymentStatus.PAID:
        existing_payment = payment
        return existing_payment

    if event == "payment.captured":

        payment.razorpay_payment_id = (
            razorpay_payment_id
        )
        payment.transaction_id = (
            razorpay_payment_id
        )
        payment.status = PaymentStatus.PAID

        payment.order.status = (
            OrderStatus.CONFIRMED
        )

    elif event == "payment.failed":

        payment.razorpay_payment_id = (
            razorpay_payment_id
        )
        payment.status = PaymentStatus.FAILED

    else:

        existing_payment = payment
        return existing_payment

    try:
        db.commit()
        db.refresh(payment)

    except IntegrityError as exc:
        db.rollback()
        raise ValueError(
            "Webhook payment update could not be completed"
        ) from exc

    processed_payment = payment

    return processed_payment