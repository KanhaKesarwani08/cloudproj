# Placeholder for budget_service.py
# This service will handle the business logic for expenses and users.

from sqlalchemy.orm import Session
from app.db import models as db_models
from app.models import expense as expense_schema # Pydantic schemas
from datetime import date
from typing import List, Optional

# Example User functions (if not in a dedicated user_service.py)
# def get_user_by_email(db: Session, email: str):
#     return db.query(user_model.User).filter(user_model.User.email == email).first()

# def create_user(db: Session, user: user_model.UserCreate):
#     hashed_password = security.get_password_hash(user.password)
#     db_user = user_model.User(email=user.email, hashed_password=hashed_password, username=user.username)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     return db_user

# Example Expense functions
# def get_expenses_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100):
#     return db.query(expense_model.Expense).filter(expense_model.Expense.owner_id == user_id).offset(skip).limit(limit).all()

# def create_user_expense(db: Session, expense: expense_model.ExpenseCreate, user_id: int):
#     db_expense = expense_model.Expense(**expense.dict(), owner_id=user_id)
#     db.add(db_expense)
#     db.commit()
#     db.refresh(db_expense)
#     return db_expense

# def get_expense(db: Session, expense_id: int, user_id: int):
#     return db.query(expense_model.Expense).filter(expense_model.Expense.id == expense_id, expense_model.Expense.owner_id == user_id).first()

# def update_expense(db: Session, expense_id: int, expense_update: expense_model.ExpenseUpdate, user_id: int):
#     db_expense = get_expense(db, expense_id, user_id)
#     if not db_expense:
#         return None
#     update_data = expense_update.dict(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_expense, key, value)
#     db.add(db_expense)
#     db.commit()
#     db.refresh(db_expense)
#     return db_expense

# def delete_expense(db: Session, expense_id: int, user_id: int):
#     db_expense = get_expense(db, expense_id, user_id)
#     if not db_expense:
#         return False
#     db.delete(db_expense)
#     db.commit()
#     return True

def get_expense_by_id(db: Session, expense_id: int, user_id: int) -> Optional[db_models.Expense]:
    """Fetch a specific expense by its ID, ensuring it belongs to the user."""
    return db.query(db_models.Expense).filter(db_models.Expense.id == expense_id, db_models.Expense.owner_id == user_id).first()

def get_expenses_for_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[db_models.Expense]:
    """Fetch all expenses for a specific user with pagination."""
    return db.query(db_models.Expense).filter(db_models.Expense.owner_id == user_id).order_by(db_models.Expense.expense_date.desc(), db_models.Expense.created_at.desc()).offset(skip).limit(limit).all()

def create_expense(db: Session, expense: expense_schema.ExpenseCreate, user_id: int) -> db_models.Expense:
    """Create a new expense for a user."""
    db_expense = db_models.Expense(
        **expense.model_dump(), # Use model_dump() for Pydantic v2
        owner_id=user_id,
        # expense_date will use default from model or value from schema
    )
    if expense.expense_date is None: # Ensure model default is used if not provided
        db_expense.expense_date = date.today()
        
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    print(f"Created expense '{db_expense.description}' for user_id {user_id}")
    return db_expense

def update_expense(
    db: Session, 
    expense_id: int, 
    expense_update_data: expense_schema.ExpenseUpdate, 
    user_id: int
) -> Optional[db_models.Expense]:
    """Update an existing expense for a user."""
    db_expense = get_expense_by_id(db=db, expense_id=expense_id, user_id=user_id)
    if not db_expense:
        return None
    
    update_data = expense_update_data.model_dump(exclude_unset=True) # Pydantic v2
    for key, value in update_data.items():
        setattr(db_expense, key, value)
    
    db.add(db_expense) # or db.commit() if only this change
    db.commit()
    db.refresh(db_expense)
    print(f"Updated expense id {expense_id} for user_id {user_id}")
    return db_expense

def delete_expense(db: Session, expense_id: int, user_id: int) -> bool:
    """Delete an expense for a user."""
    db_expense = get_expense_by_id(db=db, expense_id=expense_id, user_id=user_id)
    if not db_expense:
        return False
    
    db.delete(db_expense)
    db.commit()
    print(f"Deleted expense id {expense_id} for user_id {user_id}")
    return True

# print("budget_service.py loaded (placeholder)") # Removed this line 