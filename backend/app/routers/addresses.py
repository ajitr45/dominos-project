from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas import AddressCreate, AddressResponse, AddressUpdate
from app.services.address_service import create_address, get_user_addresses, get_user_address, update_address, deactivate_address



router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post("/", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def add_address(
    address_data: AddressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

   address = create_address(db=db, user_id=current_user.id, address_data=address_data,)
   
   return address


@router.get("/", response_model=list[AddressResponse])
def list_addresses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    addresses = get_user_addresses(db=db, user_id=current_user.id)

    return addresses


@router.get("/{address_id}", response_model=AddressResponse)
def get_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = get_user_address(db=db, user_id=current_user.id, address_id=address_id)

    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    return address


@router.patch("/{address_id}", response_model=AddressResponse,)
def edit_address(
    address_id: int,
    address_data: AddressUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = update_address(db=db, user_id=current_user.id, address_id=address_id, address_data=address_data)

    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    return address


@router.delete("/{address_id}", response_model=AddressResponse)
def delete_address(
    address_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    address = deactivate_address(db=db, user_id=current_user.id, address_id=address_id)

    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")

    return address