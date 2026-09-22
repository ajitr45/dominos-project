from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.models import User
from app.schemas import UserCreate


def register_user(db: Session, user_data: UserCreate) -> User:

    existing_email = (db.query(User).filter(User.email == user_data.email).first())

    if existing_email:
        raise ValueError("Email already registered")

    if user_data.phone:
        existing_phone = (db.query(User).filter(User.phone == user_data.phone).first())

        if existing_phone:
            raise ValueError("Phone already registered")

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