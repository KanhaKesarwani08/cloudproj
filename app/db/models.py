from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, func, Boolean
from sqlalchemy.orm import relationship

from app.db.session import Base # Import Base from our session.py

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True, nullable=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    expenses = relationship("Expense", back_populates="owner")

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}')>"

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, index=True, nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String, index=True, nullable=False)
    expense_date = Column(Date, nullable=False, default=func.current_date())
    
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    owner = relationship("User", back_populates="expenses")

    def __repr__(self):
        return f"<Expense(id={self.id}, description='{self.description}', amount={self.amount})>"

# Note: We added created_at and updated_at timestamps to both models.
# For User model, email is used for authentication.
# For Expense model, owner_id links to the User table's primary key (Integer id).
# Using an auto-incrementing integer PK (users.id) is a common pattern. 