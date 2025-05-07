from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse, RedirectResponse # Removed JSONResponse for now, token endpoint returns Token model
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from typing import Any

from app.core import security # For create_access_token and verify_access_token
from app.core.config import settings
from app.services import user_service
from app.db.session import get_db
from app.db import models as db_models # SQLAlchemy models
from app.models import user as user_schema # Pydantic schemas

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory="app/templates")

# OAuth2PasswordBearer will look for the token in the Authorization header
# tokenUrl is the URL that the client will use to get the token (our /auth/token endpoint)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Register"})

@router.post("/register", response_model=user_schema.User)
async def process_registration(
    request: Request, # Added request for potential future use with templates
    user_in: user_schema.UserCreate, # Using Pydantic model for request body
    db: Session = Depends(get_db)
):
    db_user = user_service.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered."
        )
    created_user = user_service.create_user(db=db, user=user_in)
    # Consider automatically logging in the user here by creating a token,
    # or redirecting to login with a success message.
    # For now, returning the created user data (excluding password).
    return user_schema.User.model_validate(created_user)


@router.post("/token", response_model=user_schema.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    user = user_service.authenticate_user(
        db, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.email} # "sub" is a standard claim for the subject (user identifier)
    )
    return {"access_token": access_token, "token_type": "bearer"}


async def get_current_user_from_token(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> Optional[db_models.User]:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = security.verify_access_token(token, credentials_exception)
    if payload is None: # Should not happen if verify_access_token raises on failure
        raise credentials_exception
        
    email: Optional[str] = payload.get("sub")
    if email is None:
        raise credentials_exception # Subject claim (email) missing from token
    
    user = user_service.get_user_by_email(db, email=email)
    if user is None:
        raise credentials_exception # User not found in DB for the given email in token
    return user

async def get_current_active_user(current_user: db_models.User = Depends(get_current_user_from_token)) -> db_models.User:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user


@router.get("/users/me", response_model=user_schema.User)
async def read_current_user_profile(
    current_user: db_models.User = Depends(get_current_active_user)
):
    """
    Protected endpoint. Fetches the profile of the currently authenticated user.
    """
    return user_schema.User.model_validate(current_user)

@router.get("/logout") # This is mostly a client-side action for JWT
async def logout_route(request: Request):
    """
    For JWT, logout is primarily handled by the client deleting the token.
    This endpoint can exist for consistency or if server-side session revocation were added.
    Redirects to home page.
    """
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    # If using cookies for token (not recommended for Bearer tokens), delete here.
    # response.delete_cookie(key="access_token") 
    return response 