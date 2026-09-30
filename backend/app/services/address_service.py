from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.models import Address
from app.schemas import AddressCreate, AddressUpdate


def create_address(db: Session, user_id: int, address_data: AddressCreate) -> Address:

    try:
        # Remove the existing default address before creating a new default address.
        if address_data.is_default:
            db.query(Address).filter(
                Address.user_id == user_id,
                Address.is_default.is_(True),
                Address.is_active.is_(True),
            ).update(
                {
                    Address.is_default: False,
                },
                synchronize_session=False,
            )

        address = Address(
            user_id=user_id,
            label=address_data.label,
            recipient_name=address_data.recipient_name,
            phone=address_data.phone,
            address_line1=address_data.address_line1,
            address_line2=address_data.address_line2,
            landmark=address_data.landmark,
            city=address_data.city,
            state=address_data.state,
            postal_code=address_data.postal_code,
            is_default=address_data.is_default,
        )

        db.add(address)
        db.commit()
        db.refresh(address)

        created_address = address
        return created_address

    except IntegrityError:
        db.rollback()
        raise ValueError("Address could not be created")


def get_user_addresses(db: Session, user_id: int) -> list[Address]:

    addresses = (
        db.query(Address)
        .filter(
            Address.user_id == user_id,
            Address.is_active.is_(True),
        )
        .order_by(
            Address.is_default.desc(),
            Address.created_at.desc(),
        )
        .all()
    )

    return addresses


def get_user_address(db: Session, user_id: int, address_id: int) -> Address | None:

    address = (
        db.query(Address)
        .filter(
            Address.id == address_id,
            Address.user_id == user_id,
            Address.is_active.is_(True),
        )
        .first()
    )

    return address


def update_address(
    db: Session,
    user_id: int,
    address_id: int,
    address_data: AddressUpdate,
) -> Address | None:

    address = get_user_address(
        db=db,
        user_id=user_id,
        address_id=address_id,
    )

    if not address:
        return None

    update_data = address_data.model_dump(exclude_unset=True)

    try:
        # Remove the existing default address if this address is being changed to the default address.
        if update_data.get("is_default") is True:
            db.query(Address).filter(
                Address.user_id == user_id,
                Address.id != address_id,
                Address.is_default.is_(True),
                Address.is_active.is_(True),
            ).update(
                {
                    Address.is_default: False,
                },
                synchronize_session=False,
            )

        for field, value in update_data.items():
            setattr(address, field, value)

        db.commit()
        db.refresh(address)

        updated_address = address
        return updated_address

    except IntegrityError:
        db.rollback()
        raise ValueError("Address could not be updated")


def deactivate_address(db: Session, user_id: int, address_id: int) -> Address | None:

    address = get_user_address(
        db=db,
        user_id=user_id,
        address_id=address_id,
    )

    if not address:
        return None

    try:
        # A deactivated address cannot remain the default address.
        address.is_active = False
        address.is_default = False

        db.commit()
        db.refresh(address)

        deactivated_address = address
        return deactivated_address

    except IntegrityError:
        db.rollback()
        raise ValueError("Address could not be deactivated")
    

def activate_address(db: Session, user_id: int, address_id: int) -> Address | None:

    address = (
        db.query(Address)
        .filter(
            Address.id == address_id,
            Address.user_id == user_id,
            Address.is_active.is_(False),
        )
        .first()
    )

    if not address:
        return None

    try:
        address.is_active = True

        db.commit()
        db.refresh(address)

        activated_address = address
        return activated_address

    except IntegrityError:
        db.rollback()
        raise ValueError("Address could not be activated")