from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
