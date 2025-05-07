from sqlalchemy.orm import Session
from typing import Optional

from app.db import models as db_models # Renamed to avoid clash with pydantic models
from app.models import user as user_schema # Pydantic schemas
from app.core.security import get_password_hash, verify_password

def get_user_by_email(db: Session, email: str) -> Optional[db_models.User]:
    """Fetch a user from the database by their email."""
    return db.query(db_models.User).filter(db_models.User.email == email).first()

def get_user_by_id(db: Session, user_id: int) -> Optional[db_models.User]:
    return db.query(db_models.User).filter(db_models.User.id == user_id).first()

def create_user(db: Session, user: user_schema.UserCreate) -> db_models.User:
    hashed_password = get_password_hash(user.password)
    db_user = db_models.User(
        email=user.email,
        full_name=user.full_name,
        hashed_password=hashed_password,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def authenticate_user(db: Session, email: str, password: str) -> Optional[db_models.User]:
    """
    Authenticate a user by email and password.
    Returns the user object if authentication is successful, otherwise None.
    """
    user = get_user_by_email(db, email=email)
    if not user:
        return None # User not found
    if not user.is_active:
        return None # User is inactive
    if not verify_password(password, user.hashed_password):
        return None # Incorrect password
    return user

# We can add other user-related service functions here as needed,
# e.g., update_user, deactivate_user, etc. 