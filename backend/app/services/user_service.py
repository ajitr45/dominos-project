from sqlalchemy.orm import Session

from app.models import User, UserRole
from app.core.security import hash_password


def get_all_users(db: Session):
    
    users = (db.query(User).order_by(User.id.desc()).all())

    return users

def update_user_status(
    db: Session,
    user_id: int,
    is_active: bool,
    current_admin: User,
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    # Admin cannot deactivate himself
    if user.id == current_admin.id and not is_active:
        raise ValueError("Admin cannot deactivate himself")

    user.is_active = is_active

    db.commit()
    db.refresh(user)

    updated_user = user

    return updated_user


def create_user_by_admin(
    db: Session,
    username: str,
    email: str,
    phone: str | None,
    password: str,
    role: UserRole,
):
    existing_email = db.query(User).filter(User.email == email).first()

    if existing_email:
        raise ValueError("Email already registered")

    if phone:
        existing_phone = db.query(User).filter(User.phone == phone).first()

        if existing_phone:
            raise ValueError("Phone already registered")

    hashed_password = hash_password(password)

    user = User(
        username=username,
        email=email,
        phone=phone,
        password_hash=hashed_password,
        role=role,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    created_user = user

    return created_user


def update_user_role(
    db: Session,
    user_id: int,
    role: UserRole,
    current_admin: User,
):
    user = db.query(User).filter(User.id == user_id).first()

    if not user:
        raise ValueError("User not found")

    # Admin cannot change his own role
    if user.id == current_admin.id:
        raise ValueError("Admin cannot change his own role")

    user.role = role

    db.commit()
    db.refresh(user)

    updated_user = user

    return updated_user