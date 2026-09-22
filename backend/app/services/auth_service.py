from sqlalchemy.orm import Session
from app.core.security import hash_password, verify_password
from app.models import User
from app.schemas import UserCreate


def register_user(db: Session, user_data: UserCreate) -> User:

    # Check whether email is already registered
    existing_email = (db.query(User).filter(User.email == user_data.email).first())

    if existing_email:
        raise ValueError("Email already registered")

    # Check whether phone number is already registered
    existing_phone = (db.query(User).filter(User.phone == user_data.phone).first())

    if existing_phone:
        raise ValueError("Phone already registered")

    # Never store the user's plain password in the database
    hashed_password = hash_password(user_data.password)

    user = User(
        username=user_data.username,
        email=user_data.email,
        phone=user_data.phone,
        password_hash=hashed_password,
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return user


def authenticate_user( db: Session, identifier: str, password: str) -> User | None:

    # Find user using either email or phone number
    user = (db.query(User).filter((User.email == identifier) | (User.phone == identifier)).first())

    if not user:
        return None

    # Inactive users are not allowed to login
    if not user.is_active:
        return None

    # Compare entered password with the stored password hash
    if not verify_password(password, user.password_hash):
        return None

    return user