from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import date
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services import budget_service as expense_service
# from app.services import user_service # Not directly needed here if using get_current_active_user
from app.models import expense as expense_schema
from app.db import models as db_models
from app.routers.auth import get_current_active_user # Import the dependency

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    # dependencies=[Depends(get_current_active_user)], # REMOVED from router level
    responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard(request: Request):
    """Serves the dashboard HTML page. Authentication is checked client-side."""
    # Removed Depends(get_current_active_user) and db session dependency
    # The template will be rendered, and JS will handle fetching data if logged in.
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.post("/add", response_class=RedirectResponse)
async def add_expense(
    request: Request,
    description: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    expense_date_str: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user) # Added dependency here
):
    try:
        parsed_date = date.fromisoformat(expense_date_str) if expense_date_str else date.today()
    except (ValueError, TypeError):
        parsed_date = date.today()

    expense_data = expense_schema.ExpenseCreate(
        description=description, 
        amount=amount, 
        category=category, 
        expense_date=parsed_date
    )
    created_expense = expense_service.create_expense(db=db, expense=expense_data, user_id=current_user.id)
    return RedirectResponse(url="/expenses/dashboard", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/", response_model=List[expense_schema.ExpenseInDB])
async def api_read_expenses(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user) # Added dependency here
):
    db_expenses = expense_service.get_expenses_for_user(db, user_id=current_user.id, skip=skip, limit=limit)
    return [expense_schema.ExpenseInDB.model_validate(exp) for exp in db_expenses]

@router.get("/{expense_id}", response_model=expense_schema.ExpenseInDB)
async def api_read_expense(
    expense_id: int, 
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user) # Added dependency here
):
    db_expense = expense_service.get_expense_by_id(db, expense_id=expense_id, user_id=current_user.id)
    if db_expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found")
    return expense_schema.ExpenseInDB.model_validate(db_expense)

@router.put("/{expense_id}", response_model=expense_schema.ExpenseInDB)
async def api_update_expense(
    expense_id: int, 
    expense_update: expense_schema.ExpenseUpdate, 
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user) # Added dependency here
):
    updated_expense = expense_service.update_expense(
        db, expense_id=expense_id, expense_update_data=expense_update, user_id=current_user.id
    )
    if updated_expense is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found or not authorized to update")
    return expense_schema.ExpenseInDB.model_validate(updated_expense)

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def api_delete_expense(
    expense_id: int, 
    db: Session = Depends(get_db),
    current_user: db_models.User = Depends(get_current_active_user) # Added dependency here
):
    success = expense_service.delete_expense(db, expense_id=expense_id, user_id=current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found or not authorized to delete")
    return 