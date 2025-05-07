from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, Response
import uvicorn

# Import routers
from .routers import auth, expenses

# Import for table creation
from app.db.session import engine, Base #, SessionLocal (not needed for create_all directly)
from app.db import models # Ensure models are imported so Base knows about them

# Function to create DB tables
def create_db_tables():
    print("Attempting to create database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("Database tables created successfully (if they didn't already exist).")
    except Exception as e:
        print(f"Error creating database tables: {e}")

app = FastAPI(title="Budget Tracker API")

@app.on_event("startup")
async def on_startup():
    print("Application startup...")
    create_db_tables()
    # Initialize Firebase Admin SDK (already done in firebase_auth.py when it's imported)
    # if not firebase_admin._apps:
    #     try:
    #         firebase_admin.initialize_app()
    #         print("Firebase Admin SDK initialized on startup.")
    #     except Exception as e:
    #         print(f"Error initializing Firebase Admin SDK on startup: {e}")

# Mount static files (CSS, JS)
# Ensure the directory path is correct relative to where main.py is run from.
# If main.py is in 'app/', and static is 'app/static/', then 'static' is correct.
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup Jinja2 templates
# If main.py is in 'app/', and templates is 'app/templates/', then 'templates' is correct.
templates = Jinja2Templates(directory="app/templates")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """
    Serves the main landing page.
    """
    return templates.TemplateResponse("index.html", {"request": request, "title": "Budget Tracker"})

# Add route to handle favicon requests gracefully
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return Response(status_code=204) # Return No Content

# Redirects for convenience if user hits old paths
@app.get("/login", include_in_schema=False)
async def redirect_login():
    return RedirectResponse(url="/auth/login", status_code=status.HTTP_301_MOVED_PERMANENTLY)

@app.get("/dashboard", include_in_schema=False)
async def redirect_dashboard():
    # This dashboard is now served by the expenses router
    return RedirectResponse(url="/expenses/dashboard", status_code=status.HTTP_301_MOVED_PERMANENTLY)


# Include routers
app.include_router(auth.router)
app.include_router(expenses.router)

# Basic health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    # This is for local development.
    # For production, use a Gunicorn or Uvicorn process manager as specified in Dockerfile.
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True) 