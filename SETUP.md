# Setup Guide

This document provides a step-by-step setup for both backend (FastAPI) and frontend (React), including environment, authentication, storage, and common tasks.

## 1) Prerequisites
- Python 3.10+
- Node.js 16+ and npm
- Azure Storage account (connection string)
- Optional: Azure OpenAI resource

## 2) Clone and prepare
```
git clone https://github.com/<ORG_NAME>/<REPO_NAME>.git
cd <REPO_NAME>
python -m venv venv
# PowerShell
venv\Scripts\Activate.ps1
# cmd
venv\Scripts\activate.bat
pip install -r requirements.txt
```

## 3) Environment variables (.env)
Create .env in project root:
```
# Azure Blob Storage
BLOB_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=<AZURE_STORAGE_ACCOUNT_NAME>;AccountKey=<SECRET>;EndpointSuffix=core.windows.net
BLOB_CONTAINER_NAME=resumes

# Session cookies
SESSION_SECRET=<STRONG_RANDOM_SECRET>

# Optional Azure OpenAI
AZURE_OPENAI_API_KEY=<KEY>
AZURE_OPENAI_ENDPOINT=https://<AZURE_OPENAI_RESOURCE>.openai.azure.com/
```

## 4) Backend (FastAPI)
```
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
Open API docs at http://127.0.0.1:8000/docs

## 5) Frontend (React)
```
cd frontend
npm install
# Dev
npm start
# Prod build
# REACT_APP_API_BASE_URL should point to deployed backend, e.g. https://api.<ORG_DOMAIN>/api
set REACT_APP_API_BASE_URL=https://<BACKEND_DOMAIN>/api && npm run build
```
Open http://localhost:3000

## 6) Authentication
- Azure AD: configure msalConfig (frontend/src/msalConfig.js) for tenant <TENANT_ID> and client <APP_CLIENT_ID>
- Guest: time-limited token; usable for quick trials
- Protected routes: /upload, /dashboard, /sessions

## 7) Sessions & Uploads
- Create sessions in the UI; uploads go to the active session
- Stored in Azure Blob at {user}/{session_id}/
- Delete session removes files, preserves metadata and analytics summary

## 8) Ranking, Insights, Reports
- Dashboard ranks resumes vs job description
- Insights sourced from latest non-deleted session results
- Reports generated to reports/ and uploaded to blob (xlsx/csv/pdf)

## 9) Useful scripts
```
pytest
black .
isort .
flake8
```

## 10) Troubleshooting
- Port in use: change backend port or stop process
- CORS: in production set allow_origins=["https://<FRONTEND_DOMAIN>"] in app/main.py
- Missing Azure env: set BLOB_CONNECTION_STRING and BLOB_CONTAINER_NAME
- No insights: run ranking first, or verify reports/ranked_resumes.json exists (latest non-deleted session)

## 11) Project structure (high-level)
```
app/            # FastAPI backend (routers, services)
frontend/       # React app (pages, components)
ml/             # Ranking helpers
reports/        # Generated reports (local; also uploaded)
```

## 12) Organization placeholders to replace
- <ORG_NAME>, <REPO_NAME>
- <FRONTEND_DOMAIN>, <BACKEND_DOMAIN>
- <TENANT_ID>, <APP_CLIENT_ID>
- <AZURE_STORAGE_ACCOUNT_NAME>
