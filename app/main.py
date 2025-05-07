from fastapi import FastAPI, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
import uvicorn

# Import routers
from .routers import auth, expenses

app = FastAPI(title="Budget Tracker API")

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