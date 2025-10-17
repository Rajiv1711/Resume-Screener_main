import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from app.middleware.authentication import AuthenticationMiddleware
from app.routers import resumes, ranking, reporting, auth, sessions
from app.routers import insights

app = FastAPI(title="Resume Screener API")

# CORS for frontend (React)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your React app domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Sessions must come before auth middleware
SESSION_SECRET = os.getenv("SESSION_SECRET", "change_this_secret_for_dev")
app.add_middleware(
    SessionMiddleware,
    secret_key=SESSION_SECRET,
    max_age=60 * 60 * 24 * 7,  # 7 days
    same_site="lax",
)

# Protect API routes using session-based auth
app.add_middleware(
    AuthenticationMiddleware,
    protected_paths=["/api/"],
    login_path="/api/auth/session-login",
)

# Include routers
app.include_router(resumes.router)
app.include_router(ranking.router)
app.include_router(reporting.router)
app.include_router(auth.router)
app.include_router(insights.router)
app.include_router(sessions.router)

@app.get("/")
def root():
    return {"message": "Resume Screener API is running"}
