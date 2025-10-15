# Quick Start Guide

## Prerequisites
- Python 3.8+ installed
- Node.js 14+ installed
- Azure Blob Storage account (connection string in `.env`)

## Step 1: Start Backend Server

Open a **PowerShell/CMD terminal** in the project root:

```powershell
# Navigate to project root
cd C:\Users\DhruvGupta\Resume_Screener\Resume-Screener_main

# Install Python dependencies (first time only)
pip install -r requirements.txt

# Start the FastAPI backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

**Test backend is running:**
Open browser to http://localhost:8000 - you should see:
```json
{"message": "Resume Screener API is running"}
```

## Step 2: Start Frontend Server

Open a **NEW PowerShell/CMD terminal** (keep backend running):

```powershell
# Navigate to frontend directory
cd C:\Users\DhruvGupta\Resume_Screener\Resume-Screener_main\frontend

# Install dependencies (first time only)
npm install

# Start React development server
npm start
```

You should see:
```
Compiled successfully!

You can now view resume-screener-frontend in the browser.

  Local:            http://localhost:3000
  On Your Network:  http://192.168.x.x:3000
```

Browser will automatically open to http://localhost:3000

## Step 3: Configure Frontend API Connection

The frontend needs to know where the backend API is. Add this to `frontend/package.json`:

```json
{
  "name": "resume-screener-frontend",
  "version": "1.0.0",
  "proxy": "http://localhost:8000",
  ...
}
```

OR create `frontend/src/services/api.js` with base URL configuration.

## Troubleshooting

### Backend Issues

**Error: "No module named 'app'"**
```powershell
# Make sure you're in the project root, not the frontend directory
cd C:\Users\DhruvGupta\Resume_Screener\Resume-Screener_main
```

**Error: "Address already in use"**
```powershell
# Kill process using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process -Force

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

**Error: "Azure connection failed"**
- Check `.env` file has correct `BLOB_CONNECTION_STRING`
- Verify Azure Storage account is accessible

### Frontend Issues

**Error: "Failed to load sessions: 404"**
- Backend server is not running
- Check backend is on http://localhost:8000
- Verify `package.json` has proxy configuration

**Error: "CORS error"**
- Backend CORS is already configured for `*` (all origins)
- If you changed CORS settings, add `http://localhost:3000` to allowed origins

**React compilation errors**
```powershell
# Clear cache and reinstall
rm -r node_modules
rm package-lock.json
npm install
```

## Verify Everything Works

1. **Backend health check:**
   ```powershell
   curl http://localhost:8000
   ```
   Should return: `{"message": "Resume Screener API is running"}`

2. **Sessions API check:**
   ```powershell
   curl http://localhost:8000/api/sessions/list -H "X-User-Id: test@example.com"
   ```
   Should return JSON with sessions array (may be empty initially)

3. **Frontend check:**
   - Open http://localhost:3000
   - Go to Upload page
   - You should see SessionManager on the left
   - Click "New Session" to create a session

## Quick Test

1. Create a session named "Test Session"
2. Upload a resume PDF
3. Go to Dashboard
4. Enter job description and click "Rank Resumes"
5. View results with skills displayed

## Environment Variables

Make sure you have `.env` file in project root:

```env
# Azure Blob Storage
BLOB_CONNECTION_STRING=your_connection_string_here
BLOB_CONTAINER_NAME=resumes

# Optional: Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
```

## Normal Development Workflow

```powershell
# Terminal 1: Backend
cd C:\Users\DhruvGupta\Resume_Screener\Resume-Screener_main
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd C:\Users\DhruvGupta\Resume_Screener\Resume-Screener_main\frontend
npm start
```

Keep both terminals open while developing!
