from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas import (CartItemCreate, CartItemUpdate, CartResponse)
from app.services.cart_service import (get_cart, add_item_to_cart, update_cart_item, remove_cart_item)


router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("/", response_model=CartResponse)
def get_my_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
   
    cart_response = get_cart(db=db, user_id=current_user.id)

    return cart_response


@router.post("/items", response_model=CartResponse, status_code=status.HTTP_200_OK,)
def add_cart_item(item_data: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    try:
        cart_response = add_item_to_cart(db=db, user_id=current_user.id, item_data=item_data)

        return cart_response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.patch("/items/{cart_item_id}", response_model=CartResponse)
def update_cart_item_quantity(
    cart_item_id: int,
    item_data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    
    try:
        cart_response = update_cart_item(
            db=db,
            user_id=current_user.id,
            cart_item_id=cart_item_id,
            item_data=item_data,
        )

        return cart_response

    except ValueError as exc:
        error_message = str(exc)

        if error_message == "Cart item not found":
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error_message)

        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=error_message)


@router.delete("/items/{cart_item_id}", response_model=CartResponse,)
def delete_cart_item(
    cart_item_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        cart_response = remove_cart_item(
            db=db,
            user_id=current_user.id,
            cart_item_id=cart_item_id,
        )

        return cart_response

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc),)