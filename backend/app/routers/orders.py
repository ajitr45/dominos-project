from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import (get_current_user, require_admin,)
from app.schemas import (OrderCreate, OrderResponse, OrderStatusUpdate)
from app.services.order_service import (create_order, get_user_orders, get_user_order, update_order_status)


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order_api(order_data: OrderCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    try:
        created_order = create_order(db=db, user_id=current_user.id, order_data=order_data)

        return created_order

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/", response_model=list[OrderResponse],)
def get_orders(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    
    orders = get_user_orders(db=db, user_id=current_user.id,)

    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    
    order = get_user_order(db=db, user_id=current_user.id, order_id=order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order


@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        updated_order = update_order_status(db=db, order_id=order_id, status=status_data.status)

        if not updated_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        return updated_order

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))