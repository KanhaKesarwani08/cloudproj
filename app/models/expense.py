from pydantic import BaseModel
from datetime import date, datetime # Changed from datetime to date for expense_date
from typing import Optional

class ExpenseBase(BaseModel):
    description: str
    amount: float
    category: str
    expense_date: Optional[date] = None # Make date optional, default to today or provided

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(ExpenseBase):
    # All fields optional for update
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    expense_date: Optional[date] = None

class ExpenseInDB(ExpenseBase):
    id: int
    owner_id: int # To link expense to a user
    created_at: datetime # To track when the record was created

    class Config:
        orm_mode = True # or from_attributes = True for Pydantic v2 