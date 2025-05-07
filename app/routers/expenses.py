from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import List, Optional
from datetime import date

# Placeholder for actual service and models
# from ...models import expense as expense_model
# from ...services import budget_service
# from ..auth import get_current_active_user # Assuming you have this for authentication

router = APIRouter(
    prefix="/expenses",
    tags=["expenses"],
    # dependencies=[Depends(get_current_active_user)], # Protect all expense routes
    responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory="app/templates")

# In-memory placeholder for expenses (replace with DB interaction)
fake_expenses_db = []
expense_id_counter = 0

@router.get("/dashboard", response_class=HTMLResponse)
async def view_dashboard(request: Request):
    """Serves the main dashboard page where users can see and add expenses."""
    # In a real app, fetch user-specific expenses
    # current_user = Depends(get_current_active_user) # Get current user
    # user_expenses = budget_service.get_expenses_for_user(user_id=current_user.id)
    return templates.TemplateResponse("dashboard.html", {"request": request, "expenses": fake_expenses_db})

@router.post("/add", response_class=RedirectResponse) # Or return JSON and handle with JS
async def add_expense(
    request: Request, # Needed if you render a template on error or for context
    description: str = Form(...),
    amount: float = Form(...),
    category: str = Form(...),
    expense_date_str: Optional[str] = Form(None) # Keep as string for now
    # current_user: user_model.UserInDB = Depends(get_current_active_user)
):
    """Handles the submission of a new expense."""
    global expense_id_counter
    expense_id_counter += 1
    
    try:
        parsed_date = date.fromisoformat(expense_date_str) if expense_date_str else date.today()
    except ValueError:
        # Handle invalid date format, perhaps redirect with error or return an error response
        # For now, just default to today
        parsed_date = date.today()
        print(f"Invalid date format for {expense_date_str}, defaulting to today.")

    new_expense = {
        "id": expense_id_counter,
        "description": description,
        "amount": amount,
        "category": category,
        "expense_date": parsed_date,
        # "owner_id": current_user.id
    }
    fake_expenses_db.append(new_expense)
    print(f"Added expense: {new_expense}") # Log added expense
    
    # Redirect to dashboard to see the new expense
    # In a more JS-heavy frontend, you might return JSON and update the page dynamically.
    return RedirectResponse(url="/dashboard", status_code=status.HTTP_303_SEE_OTHER) # 303 for POST-redirect-GET


# Placeholder API endpoints (would be used by JS or other clients)

# @router.get("/", response_model=List[expense_model.ExpenseInDB])
# async def read_expenses(
#     skip: int = 0, 
#     limit: int = 100, 
#     # current_user: user_model.UserInDB = Depends(get_current_active_user)
# ):
#     # expenses = budget_service.get_expenses(user_id=current_user.id, skip=skip, limit=limit)
#     # return expenses
#     return fake_expenses_db[skip : skip + limit]

# @router.get("/{expense_id}", response_model=expense_model.ExpenseInDB)
# async def read_expense(
#     expense_id: int, 
#     # current_user: user_model.UserInDB = Depends(get_current_active_user)
# ):
#     # db_expense = budget_service.get_expense(expense_id=expense_id, user_id=current_user.id)
#     # if db_expense is None:
#     #     raise HTTPException(status_code=404, detail="Expense not found")
#     # return db_expense
#     for expense in fake_expenses_db:
#         if expense["id"] == expense_id:
#             return expense
#     raise HTTPException(status_code=404, detail="Expense not found")

# @router.put("/{expense_id}", response_model=expense_model.ExpenseInDB)
# async def update_expense_item(
#     expense_id: int, 
#     expense: expense_model.ExpenseUpdate, 
#     # current_user: user_model.UserInDB = Depends(get_current_active_user)
# ):
#     # updated_expense = budget_service.update_expense(expense_id=expense_id, expense_update=expense, user_id=current_user.id)
#     # if updated_expense is None:
#     #     raise HTTPException(status_code=404, detail="Expense not found or not owned by user")
#     # return updated_expense
#     raise HTTPException(status_code=501, detail="Update not implemented yet.")

# @router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_expense_item(
#     expense_id: int, 
#     # current_user: user_model.UserInDB = Depends(get_current_active_user)
# ):
#     # success = budget_service.delete_expense(expense_id=expense_id, user_id=current_user.id)
#     # if not success:
#     #     raise HTTPException(status_code=404, detail="Expense not found or not owned by user")
#     # return
#     raise HTTPException(status_code=501, detail="Delete not implemented yet.") 