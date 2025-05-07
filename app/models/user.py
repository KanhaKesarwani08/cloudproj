from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserLogin(BaseModel):
    username: str # Or email
    password: str

class UserInDB(UserBase):
    id: int
    # hashed_password: str # Store hashed password in DB representation

    class Config:
        orm_mode = True # or from_attributes = True for Pydantic v2

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None 