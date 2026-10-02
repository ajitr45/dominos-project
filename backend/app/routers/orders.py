from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import (require_customer, require_admin_or_manager, require_delivery_boy)
from app.schemas import (OrderCreate,  OrderResponse,  OrderStatusUpdate,  DeliveryBoyAssign,)
from app.services.order_service import (create_order, get_delivery_boy_order_history, get_user_orders, get_user_order, get_all_orders, get_order_by_id, update_order_status, assign_delivery_boy, get_delivery_boy_orders, update_delivery_order_status)
from app.models import User


router = APIRouter(prefix="/orders", tags=["Orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order_api(order_data: OrderCreate, db: Session = Depends(get_db), current_user=Depends(require_customer)):
    try:
        created_order = create_order(db=db, user_id=current_user.id, order_data=order_data)

        return created_order

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# Customer: Get own orders
@router.get("/", response_model=list[OrderResponse])
def get_orders(db: Session = Depends(get_db), current_user=Depends(require_customer)):
    
    orders = get_user_orders(db=db, user_id=current_user.id)

    return orders


# Delivery boy: Get assigned active orders
@router.get("/delivery/assigned", response_model=list[OrderResponse])
def get_assigned_orders(db: Session = Depends(get_db), current_user: User = Depends(require_delivery_boy)):
    
    orders = get_delivery_boy_orders(db=db, delivery_boy_id=current_user.id)

    return orders


# Delivery boy: Get order history
@router.get("/delivery/history", response_model=list[OrderResponse])
def get_delivery_order_history(db: Session = Depends(get_db), current_user: User = Depends(require_delivery_boy)):
    
    order_history = get_delivery_boy_order_history(db=db, delivery_boy_id=current_user.id)

    return order_history


# Admin/Manager: Get all orders
@router.get("/management/all", response_model=list[OrderResponse])
def get_all_orders_api(db: Session = Depends(get_db), current_user=Depends(require_admin_or_manager)):
    orders = get_all_orders(db=db)

    return orders


# Admin/Manager: Get any order by ID
@router.get("/management/{order_id}", response_model=OrderResponse)
def get_order_by_id_api(order_id: int, db: Session = Depends(get_db), current_user=Depends(require_admin_or_manager)):
    
    order = get_order_by_id(db=db, order_id=order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order


# Customer: Get own order
@router.get("/{order_id}", response_model=OrderResponse)
def get_order(order_id: int, db: Session = Depends(get_db), current_user=Depends(require_customer)):
    
    order = get_user_order(db=db, user_id=current_user.id, order_id=order_id)

    if not order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

    return order


# Admin/Manager: Assign delivery boy
@router.patch("/{order_id}/assign-delivery-boy", response_model=OrderResponse)
def assign_delivery_boy_api(
    order_id: int,
    data: DeliveryBoyAssign,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin_or_manager),
):
    try:
        assigned_order = assign_delivery_boy(
            db=db,
            order_id=order_id,
            delivery_boy_id=data.delivery_boy_id,
        )

        return assigned_order

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# Admin/Manager: Update order status
@router.patch("/{order_id}/status", response_model=OrderResponse)
def update_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_manager),
):
    try:
        updated_order = update_order_status(
            db=db,
            order_id=order_id,
            status=status_data.status,
        )

        if not updated_order:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Order not found")

        return updated_order

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


# Delivery boy: Update assigned order status
@router.patch("/{order_id}/delivery-status", response_model=OrderResponse)
def update_delivery_status(
    order_id: int,
    status_data: OrderStatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_delivery_boy),
):
    try:
        updated_order = update_delivery_order_status(
            db=db,
            order_id=order_id,
            delivery_boy_id=current_user.id,
            status=status_data.status,
        )

        return updated_order

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))