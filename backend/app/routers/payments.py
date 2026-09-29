from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import (require_admin_or_manager, require_customer, require_delivery_boy)
from app.models import User
from app.schemas import (PaymentCreate, PaymentResponse, PaymentUpdate, RazorpayPaymentResponse, RazorpayPaymentVerify)
from app.services.payment_service import (create_payment, get_payment, get_user_payments, mark_cod_payment_paid, process_razorpay_webhook, update_payment_status, verify_razorpay_payment)


router = APIRouter(prefix="/payments", tags=["Payments"])


# --------------------------------------------------
# Customer: Create payment
# --------------------------------------------------

@router.post("/", response_model=PaymentResponse | RazorpayPaymentResponse)
def create_payment_api(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        payment_response = create_payment(
            db=db,
            user_id=current_user.id,
            payment_data=payment_data,
        )

        return payment_response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# --------------------------------------------------
# Customer: Get own payments
# --------------------------------------------------

@router.get("/", response_model=list[PaymentResponse])
def get_payments(db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    
    payments = get_user_payments(db=db, user_id=current_user.id)

    return payments


# --------------------------------------------------
# Customer: Get own payment
# --------------------------------------------------

@router.get("/{payment_id}", response_model=PaymentResponse,)
def get_payment_by_id(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_customer)):
    
    payment = get_payment(db=db, user_id=current_user.id, payment_id=payment_id)

    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

    return payment


# --------------------------------------------------
# Customer: Verify own Razorpay payment
# --------------------------------------------------

@router.post("/{payment_id}/verify", response_model=PaymentResponse)
def verify_payment(
    payment_id: int,
    payment_data: RazorpayPaymentVerify,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_customer),
):
    try:
        verified_payment = verify_razorpay_payment(
            db=db,
            user_id=current_user.id,
            payment_id=payment_id,
            razorpay_payment_id=payment_data.razorpay_payment_id,
            razorpay_order_id=payment_data.razorpay_order_id,
            razorpay_signature=payment_data.razorpay_signature,
        )

        return verified_payment

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# --------------------------------------------------
# Delivery Boy: Mark COD payment as paid
# --------------------------------------------------

@router.patch("/{payment_id}/cod-paid", response_model=PaymentResponse)
def mark_cod_paid(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_boy),
):
    try:
        paid_payment = mark_cod_payment_paid(
            db=db,
            payment_id=payment_id,
            delivery_boy_id=current_user.id,
        )

        return paid_payment

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# --------------------------------------------------
# Admin/Manager: Update payment status
# --------------------------------------------------

@router.patch("/{payment_id}/status", response_model=PaymentResponse,)
def update_status(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    try:
        updated_payment = update_payment_status(
            db=db,
            payment_id=payment_id,
            payment_data=payment_data,
        )

        if not updated_payment:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

        return updated_payment

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# --------------------------------------------------
# Razorpay: Webhook
# --------------------------------------------------

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def razorpay_webhook(request: Request, db: Session = Depends(get_db)):
    payload = await request.body()

    webhook_signature = request.headers.get("X-Razorpay-Signature")

    if not webhook_signature:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing Razorpay webhook signature")

    try:
        payload_text = payload.decode("utf-8")

        processed_payment = process_razorpay_webhook(db=db, payload=payload_text, webhook_signature=webhook_signature)

        response = {
            "message": "Webhook processed successfully",
            "payment_id": processed_payment.id,
        }

        return response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))