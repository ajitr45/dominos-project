from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas import AddressCreate, AddressResponse, AddressUpdate
from app.services.address_service import (activate_address, create_address, get_user_addresses, get_user_address, update_address, deactivate_address)


router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def add_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        address = create_address(
            db=db,
            user_id=current_user.id,
            address_data=address_data,
        )

        return address

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.get("/", response_model=list[AddressResponse])
def list_addresses(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    addresses = get_user_addresses(db=db, user_id=current_user.id)

    return addresses


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = get_user_address(
        db=db,
        user_id=current_user.id,
        address_id=address_id,
    )

    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    return address


@router.patch("/{address_id}", response_model=AddressResponse)
def edit_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        address = update_address(
            db=db,
            user_id=current_user.id,
            address_id=address_id,
            address_data=address_data,
        )

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Address not found",
            )

        return address

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))


@router.delete("/{address_id}", response_model=AddressResponse)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        address = deactivate_address(
            db=db,
            user_id=current_user.id,
            address_id=address_id,
        )

        if not address:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

        return address

    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    
    

@router.patch("/{address_id}/activate", response_model=AddressResponse)
def activate_address_endpoint(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        address = activate_address(
            db=db,
            user_id=current_user.id,
            address_id=address_id,
        )

        if not address:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Inactive address not found",
            )

        return address

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )