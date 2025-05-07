from fastapi import APIRouter, Depends, HTTPException, status, Request, Header
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates

# Import the Firebase token verification logic
from app.core.firebase_auth import verify_firebase_token, get_current_user
# from ..models import user as user_model # Keep for potential future use (e.g. storing user profiles)

router = APIRouter(
    prefix="/auth",
    tags=["authentication"],
    responses={404: {"description": "Not found"}}
)

templates = Jinja2Templates(directory="app/templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serves the HTML page where FirebaseUI or custom Firebase JS will handle login."""
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@router.post("/token")
async def backend_token_verification(id_token: str = Header(None, alias="Authorization")):
    """
    Receives a Firebase ID token from the client (in Authorization header), 
    verifies it, and can be used to establish a backend session or confirm authentication.
    The client should send the token as "Bearer <FIREBASE_ID_TOKEN>".
    """
    if id_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization token not provided",
        )
    
    if id_token.startswith("Bearer "):
        token = id_token.split("Bearer ")[1]
    else:
        token = id_token # Assume token is passed directly if no Bearer prefix
        # raise HTTPException(
        #     status_code=status.HTTP_401_UNAUTHORIZED,
        #     detail="Invalid token format. Must be Bearer token.",
        # )

    try:
        decoded_token = await verify_firebase_token(token=token) # Manually pass token here
        # At this point, token is verified.
        # You could create a session, or look up/create a user in your own DB.
        # For now, just return the decoded claims (like UID, email).
        return {
            "message": "Token verified successfully", 
            "uid": decoded_token.get("uid"), 
            "email": decoded_token.get("email")
        }
    except HTTPException as e:
        # Re-raise HTTPException from verify_firebase_token
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred during token verification: {str(e)}"
        )

@router.get("/logout") # This will be largely a client-side concern with Firebase
async def logout_page(request: Request):
    """
    Firebase handles logout primarily on the client-side.
    This endpoint could clear any backend session cookies if they were set.
    For now, it just redirects to home.
    """
    response = RedirectResponse(url="/", status_code=status.HTTP_302_FOUND)
    # If you were setting a backend session cookie, delete it here:
    # response.delete_cookie("backend_session_id")
    return response

# Example of a protected route that uses the Firebase token for authentication
@router.get("/users/me")
async def read_current_user_from_firebase(current_user_claims: dict = Depends(get_current_user)):
    """
    Protected endpoint. Requires a valid Firebase ID token in the Authorization header.
    The `get_current_user` dependency will verify the token and return its claims.
    """
    # `current_user_claims` will be the dictionary of claims from the verified Firebase ID token (uid, email, etc.)
    # You might want to fetch more user details from your database using current_user_claims['uid']
    return {"message": "You are authenticated!", "user_info": current_user_claims}

# Registration is now handled by FirebaseUI on the client-side.
# The /register GET and POST endpoints can be removed or commented out.

# @router.get("/register", response_class=HTMLResponse)
# async def register_page(request: Request):
#     # return templates.TemplateResponse("register.html", {"request": request})
#     raise HTTPException(status_code=501, detail="Registration handled by Firebase on client-side.")

# @router.post("/register")
# async def register_user(username: str = Form(...), email: str = Form(...), password: str = Form(...)):
#     raise HTTPException(status_code=501, detail="Registration handled by Firebase on client-side.") 