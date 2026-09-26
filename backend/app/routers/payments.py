from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user, require_admin
from app.schemas import (
    PaymentCreate,
    PaymentResponse,
    PaymentUpdate,
)
from app.services.payment_service import (
    create_payment,
    get_payment,
    get_user_payments,
    update_payment_status,
)

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post("/", response_model=PaymentResponse, status_code=201)
def create_payment_api(
    payment_data: PaymentCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    try:
        payment = create_payment(
            db=db,
            user_id=current_user.id,
            payment_data=payment_data,
        )

        return payment

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )
        
@router.get("/", response_model=list[PaymentResponse])
def get_payments(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    payments = get_user_payments(
        db=db,
        user_id=current_user.id,
    )

    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_api(
    payment_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    payment = get_payment(
        db=db,
        user_id=current_user.id,
        payment_id=payment_id,
    )

    if not payment:
        raise HTTPException(
            status_code=404,
            detail="Payment not found",
        )

    return payment


@router.patch(
    "/{payment_id}/status",
    response_model=PaymentResponse,
)
def update_payment_status_api(
    payment_id: int,
    payment_data: PaymentUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        payment = update_payment_status(
            db=db,
            payment_id=payment_id,
            payment_data=payment_data,
        )

        if not payment:
            raise HTTPException(
                status_code=404,
                detail="Payment not found",
            )

        return payment

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )