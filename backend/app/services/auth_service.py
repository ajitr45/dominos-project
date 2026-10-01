from datetime import datetime, timedelta
import hashlib
import secrets
from sqlalchemy.orm import Session
from app.core.config import JWT_REFRESH_TOKEN_EXPIRE_DAYS
from app.core.security import (create_refresh_token, hash_password, verify_password)
from app.models import (PasswordResetToken, RefreshToken, User)
from app.schemas import UserCreate
from app.services.email_service import send_password_reset_email


def register_user(db: Session, user_data: UserCreate) -> User:
    existing_email = (db.query(User).filter(User.email == user_data.email).first())

    if existing_email:
        raise ValueError("Email already registered")

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

    registered_user = user
    return registered_user


def authenticate_user(db: Session, identifier: str, password: str) -> User | None:
    
    user = (db.query(User).filter((User.email == identifier) | (User.phone == identifier)).first())

    if not user:
        return None

    if not user.is_active:
        return None

    password_is_valid = verify_password(password, user.password_hash)

    if not password_is_valid:
        return None

    authenticated_user = user
    
    return authenticated_user


def create_user_refresh_token(db: Session, user: User) -> str:
    
    refresh_token = create_refresh_token(user.id)

    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    expires_at = (datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS))

    refresh_token_record = RefreshToken(user_id=user.id, token_hash=token_hash, expires_at=expires_at)

    db.add(refresh_token_record)
    db.commit()
    db.refresh(refresh_token_record)

    created_token = refresh_token
    return created_token


def rotate_refresh_token(db: Session, refresh_token: str, user_id: int) -> str:
    
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    current_token = (db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first())

    if not current_token:
        raise ValueError("Invalid refresh token")

    if current_token.user_id != user_id:
        raise ValueError("Invalid refresh token")

    if current_token.revoked_at is not None:
        raise ValueError("Refresh token has been revoked")

    if current_token.expires_at < datetime.utcnow():
        raise ValueError("Refresh token has expired")

    user = (db.query(User).filter(User.id == current_token.user_id).first())

    if not user:
        raise ValueError("User not found")

    if not user.is_active:
        raise ValueError("User account is inactive")

    current_token.revoked_at = datetime.utcnow()

    new_refresh_token = create_refresh_token(user.id)

    new_token_hash = hashlib.sha256(new_refresh_token.encode()).hexdigest()

    new_expires_at = (datetime.utcnow() + timedelta(days=JWT_REFRESH_TOKEN_EXPIRE_DAYS))

    new_token_record = RefreshToken(
        user_id=user.id,
        token_hash=new_token_hash,
        expires_at=new_expires_at,
    )

    db.add(new_token_record)
    db.flush()

    current_token.replaced_by_token_id = new_token_record.id

    db.commit()

    rotated_token = new_refresh_token
    
    return rotated_token


def revoke_refresh_token(db: Session, refresh_token: str) -> None:
    
    token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    refresh_token_record = (db.query(RefreshToken).filter(RefreshToken.token_hash == token_hash).first())

    if not refresh_token_record:
        raise ValueError("Invalid refresh token")

    if refresh_token_record.revoked_at is not None:
        raise ValueError("Refresh token has already been revoked")

    refresh_token_record.revoked_at = datetime.utcnow()

    db.commit()


def change_password(db: Session, user: User, current_password: str, new_password: str):
    
    password_is_valid = verify_password(current_password, user.password_hash)

    if not password_is_valid:
        raise ValueError("Current password is incorrect")

    if verify_password(new_password, user.password_hash):
        raise ValueError("New password must be different from current password")

    user.password_hash = hash_password(new_password)

    (
        db.query(RefreshToken).filter(
            RefreshToken.user_id == user.id,
            RefreshToken.revoked_at.is_(None),
        )
        .update(
            {
                RefreshToken.revoked_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )
    )

    db.commit()
    db.refresh(user)

    updated_user = user
    return updated_user


def create_password_reset_token(db: Session, email: str):
    
    user = (db.query(User).filter(User.email == email).first())

    if not user:
        return None

    reset_token = secrets.token_urlsafe(32)
    token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
    expires_at = (datetime.utcnow() + timedelta(minutes=15))

    reset_token_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(reset_token_record)
    db.commit()
    db.refresh(reset_token_record)

    try:
        email_sent = send_password_reset_email(
            recipient_email=user.email,
            reset_token=reset_token,
        )
    except Exception as exc:
        db.delete(reset_token_record)
        db.commit()
        raise ValueError("Unable to send password reset email") from exc

    if not email_sent:
        db.delete(reset_token_record)
        db.commit()
        raise ValueError("Unable to send password reset email")

    created_token = reset_token_record
    
    return created_token


def reset_password(db: Session, token: str, new_password: str):
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()

    reset_token_record = (db.query(PasswordResetToken).filter(PasswordResetToken.token_hash == token_hash).first())

    if not reset_token_record:
        raise ValueError("Invalid password reset token")

    if reset_token_record.used_at is not None:
        raise ValueError("Password reset token has already been used")

    if reset_token_record.expires_at < datetime.utcnow():
        raise ValueError("Password reset token has expired")

    user = (db.query(User).filter(User.id == reset_token_record.user_id).first())

    if not user:
        raise ValueError("User not found")

    if verify_password(new_password, user.password_hash):
        raise ValueError("New password must be different from current password")

    user.password_hash = hash_password(new_password)
    reset_token_record.used_at = datetime.utcnow()

    (db.query(RefreshToken)
        .filter(RefreshToken.user_id == user.id, RefreshToken.revoked_at.is_(None))
        .update(
            {
                RefreshToken.revoked_at: datetime.utcnow(),
            },
            synchronize_session=False,
        )
    )

    db.commit()
    db.refresh(user)

    updated_user = user
    
    return updated_user