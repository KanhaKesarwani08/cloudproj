from pydantic import BaseModel, EmailStr
from typing import Optional

# Schema for user creation (input)
class UserCreate(BaseModel):
    email: EmailStr
    password: str # Plain password for creation
    full_name: Optional[str] = None

# Schema for user login (input)
class UserLogin(BaseModel):
    email: EmailStr # Using email as username
    password: str

# Base schema for user data (output, doesn't include password)
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    is_active: Optional[bool] = True # Default to True if not specified by DB

# Schema for user data stored in DB (used for reading, includes id)
class UserInDB(UserBase):
    id: int

    class Config:
        from_attributes = True

# Schema for representing a user in responses (could be same as UserInDB or tailored)
class User(UserBase):
    id: int

    class Config:
        from_attributes = True

# Token schemas for JWT authentication
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[EmailStr] = None # Subject of the token (e.g., user's email or ID)
    # You could add other claims like user_id here if needed 