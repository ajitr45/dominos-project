from datetime import datetime, timedelta
import hashlib
import secrets

from sqlalchemy.orm import Session

from app.core.security import hash_password, verify_password
from app.models import PasswordResetToken, User
from app.schemas import UserCreate
from app.services.email_service import send_password_reset_email


def register_user(db: Session, user_data: UserCreate) -> User:

    # Check whether email is already registered
    existing_email = (
        db.query(User)
        .filter(User.email == user_data.email)
        .first()
    )

    if existing_email:
        raise ValueError("Email already registered")

    # Check whether phone number is already registered
    existing_phone = (
        db.query(User)
        .filter(User.phone == user_data.phone)
        .first()
    )

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


def authenticate_user(
    db: Session,
    identifier: str,
    password: str,
) -> User | None:

    # Find user using either email or phone number
    user = (
        db.query(User)
        .filter(
            (User.email == identifier)
            | (User.phone == identifier)
        )
        .first()
    )

    if not user:
        return None

    # Inactive users are not allowed to login
    if not user.is_active:
        return None

    # Compare entered password with the stored password hash
    if not verify_password(password, user.password_hash):
        return None

    return user


def change_password(
    db: Session,
    user: User,
    current_password: str,
    new_password: str,
):
    # Verify the current password
    password_is_valid = verify_password(
        current_password,
        user.password_hash,
    )

    if not password_is_valid:
        raise ValueError("Current password is incorrect")

    # Prevent using the same password again
    if verify_password(new_password, user.password_hash):
        raise ValueError(
            "New password must be different from current password"
        )

    # Hash the new password before storing it
    user.password_hash = hash_password(new_password)

    db.commit()
    db.refresh(user)

    updated_user = user

    return updated_user


def create_password_reset_token(db: Session, email: str):
    # Find user by email
    user = (db.query(User).filter(User.email == email).first())

    # Do not reveal whether the email exists
    if not user:
        return None

    # Generate a secure random token
    reset_token = secrets.token_urlsafe(32)

    # Hash the token before storing it
    token_hash = hashlib.sha256(reset_token.encode()).hexdigest()

    # Set token expiry time
    expires_at = datetime.utcnow() + timedelta(minutes=15)

    # Create reset token record
    reset_token_record = PasswordResetToken(
        user_id=user.id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    db.add(reset_token_record)
    db.commit()
    db.refresh(reset_token_record)

    # Send the original token through email
    try:
        email_sent = send_password_reset_email(recipient_email=user.email, reset_token=reset_token)

    except Exception as exc:
        # Remove the unused reset token if email sending fails
        db.delete(reset_token_record)
        db.commit()

        raise ValueError("Unable to send password reset email") from exc

    if not email_sent:
        # Remove the unused reset token if email was not sent
        db.delete(reset_token_record)
        db.commit()

        raise ValueError("Unable to send password reset email")

    created_token = reset_token_record

    return created_token


def reset_password(
    db: Session,
    token: str,
    new_password: str,
):
    # Hash the received reset token
    token_hash = hashlib.sha256(
        token.encode()
    ).hexdigest()

    # Find the reset token record
    reset_token_record = (
        db.query(PasswordResetToken)
        .filter(
            PasswordResetToken.token_hash == token_hash
        )
        .first()
    )

    if not reset_token_record:
        raise ValueError("Invalid password reset token")

    # Check whether the token has already been used
    if reset_token_record.used_at is not None:
        raise ValueError("Password reset token has already been used")

    # Check whether the token has expired
    if reset_token_record.expires_at < datetime.utcnow():
        raise ValueError("Password reset token has expired")

    # Find the associated user
    user = (
        db.query(User)
        .filter(User.id == reset_token_record.user_id)
        .first()
    )

    if not user:
        raise ValueError("User not found")

    # Prevent using the same password again
    if verify_password(new_password, user.password_hash):
        raise ValueError(
            "New password must be different from current password"
        )

    # Hash and update the new password
    user.password_hash = hash_password(new_password)

    # Mark the reset token as used
    reset_token_record.used_at = datetime.utcnow()

    db.commit()

    db.refresh(user)

    updated_user = user

    return updated_user