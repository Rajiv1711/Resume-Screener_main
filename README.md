# Resume Screener

AI-powered resume screening platform with session-based uploads, ranking, insights, and reporting. Backend is FastAPI; frontend is React. Storage uses Azure Blob with per-user, per-session organization. Auth supports Azure AD and time-limited Guest access.

## Features
- Upload PDF/DOCX/TXT/ZIP into named sessions
- LLM-augmented ranking + hybrid fallback; insights dashboard
- Reports: Excel, CSV, and enhanced PDF
- Session management: create, switch active, rename, delete
- Auth: Azure AD (MSAL) and Guest token

## Architecture
- Frontend: React (MSAL), routes protected via ProtectedRoute
- Backend: FastAPI with routers for resumes, ranking, sessions, reporting, insights
- Storage: Azure Blob per user/session; local fallback for some artifacts

## Prerequisites
- Python 3.10+ (tested on 3.13)
- Node.js 16+ and npm
- Azure Storage account and connection string
- (Optional) Azure OpenAI for LLM ranking

## Environment
Create a .env in project root:

```
BLOB_CONNECTION_STRING=YourAzureBlobConnectionString
BLOB_CONTAINER_NAME=resumes
# Optional Azure OpenAI
AZURE_OPENAI_API_KEY=your-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
SESSION_SECRET=change_this_secret_for_dev
```

## Quick Start
1) Backend
```
python -m venv venv
venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
2) Frontend
```
cd frontend
npm install
npm start
```
Open http://localhost:3000 (frontend) and http://127.0.0.1:8000/docs (API docs).

## Auth
- Sign in via Microsoft (Azure AD), or use Guest login (time-limited). Protected pages: /upload, /dashboard, /sessions.

## Sessions
- API prefix: /api/sessions
- Stores files under {user}/{session_id}/ in Azure Blob; metadata in .metadata.json
- Deleting a session removes files but keeps metadata and analytics archive

## Insights & Reports
- Insights computed from reports/ranked_resumes.json (per latest non-deleted session)
- Reports generated to reports/ as xlsx/csv/pdf and uploaded to blob

## Testing & Linting
```
pytest
black . && isort . && flake8
```

## Directory Structure
```
app/            # FastAPI backend
frontend/       # React app
ml/             # Ranking helpers
reports/        # Generated reports (also uploaded to blob)
```

## Deployment
- Frontend
  - Dev: npm start
  - Prod: npm run build and host build/ on your static host (set REACT_APP_API_BASE_URL)
- Backend
  - Run behind a reverse proxy (e.g., nginx). Set CORS allow_origins to your frontend domain.
  - Example env: SESSION_SECRET, BLOB_CONNECTION_STRING, BLOB_CONTAINER_NAME, AZURE_OPENAI_* (optional)
- Config
  - Frontend .env: REACT_APP_API_BASE_URL=https://<BACKEND_DOMAIN>/api
  - Backend CORS: allow_origins=["https://<FRONTEND_DOMAIN>"]

## Repository & Maintainers
- Org: <ORG_NAME>
- Repo: <REPO_NAME>
- URL: https://github.com/<ORG_NAME>/<REPO_NAME>
- Primary contact: <TEAM_OR_OWNER_EMAIL>

## More Docs
- SETUP.md – step-by-step setup (org-specific details below)
- QUICK_START.md – detailed quick start
- SESSION_UI_GUIDE.md – Session UI details
- azure_blob_integration.md – Storage design

## Org-specific Notes (replace placeholders)
- Azure Storage Account: <AZURE_STORAGE_ACCOUNT_NAME>
- Default Container: resumes (override with BLOB_CONTAINER_NAME)
- Frontend URL: https://<FRONTEND_DOMAIN>
- Backend URL: https://<BACKEND_DOMAIN>
- Authentication Provider: Azure AD tenant <TENANT_NAME>/<TENANT_ID>
