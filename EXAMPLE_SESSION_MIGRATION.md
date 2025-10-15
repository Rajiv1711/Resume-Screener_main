# Example: Migrating Resume Upload to Session-Based Storage

## Current Upload Endpoint (Before)

```python
@router.post("/upload")
async def upload_resume(file: UploadFile, request: Request = None):
    user_id = request.headers.get("X-User-Id", "guest")
    
    # Read file
    content = await file.read()
    
    # Upload to blob storage (old method)
    blob_storage.upload_file_user(
        content,
        f"raw_resumes/{file.filename}",
        user_id
    )
    
    return {"status": "success"}
```

## Updated Upload Endpoint (After)

```python
@router.post("/upload")
async def upload_resume(file: UploadFile, request: Request = None):
    user_id = request.headers.get("X-User-Id", "guest")
    
    # Read file
    content = await file.read()
    
    # Upload to blob storage (session-based method)
    url = blob_storage.upload_file_session(
        content,
        f"raw_resumes/{file.filename}",
        user_id
        # session_id is optional - uses current session if not provided
    )
    
    # Get session info for response
    session_id = blob_storage.get_current_session(user_id)
    
    return {
        "status": "success",
        "url": url,
        "session_id": session_id,
        "file_path": f"{blob_storage.get_session_path(user_id)}{file.filename}"
    }
```

## Updated Ranking Endpoint

### Before
```python
@router.post("/rank")
async def rank_resumes(job_description: str, request: Request):
    user_id = request.headers.get("X-User-Id", "guest")
    
    # List uploaded resumes
    blob_names = blob_storage.list_blobs_user(
        prefix="raw_resumes/",
        user_id=user_id
    )
    
    # Process and rank...
```

### After (Session-Based)
```python
@router.post("/rank")
async def rank_resumes(job_description: str, request: Request):
    user_id = request.headers.get("X-User-Id", "guest")
    
    # List resumes in current session
    blob_names = blob_storage.list_blobs_session(
        user_id=user_id,
        prefix="raw_resumes/"
    )
    
    # Process resumes...
    resumes = []
    for blob_name in blob_names:
        # Download from session
        content = blob_storage.download_file_session(blob_name, user_id)
        # Parse and process...
    
    # Save results to session
    json_content = json.dumps(ranked_results).encode('utf-8')
    blob_storage.upload_file_session(
        json_content,
        "reports/ranked_resumes.json",
        user_id
    )
```

## Complete Example: Updated Resume Router

```python
from fastapi import APIRouter, UploadFile, File, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from app.services.blob_storage import blob_storage
from app.services.parser import parse_resume_from_blob
import os

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
    request: Request = None
):
    """Upload a resume to the current session."""
    try:
        # Get user ID
        user_id = "guest"
        if request:
            user_id = request.headers.get("X-User-Id", "guest")
        
        # Validate file type
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in [".pdf", ".docx", ".txt"]:
            raise HTTPException(400, "Invalid file type")
        
        # Read and upload to current session
        content = await file.read()
        url = blob_storage.upload_file_session(
            content,
            f"raw_resumes/{file.filename}",
            user_id
        )
        
        # Get session info
        session_id = blob_storage.get_current_session(user_id)
        session_path = blob_storage.get_session_path(user_id)
        
        return JSONResponse({
            "status": "success",
            "filename": file.filename,
            "url": url,
            "session_id": session_id,
            "session_path": session_path
        })
        
    except Exception as e:
        raise HTTPException(500, str(e))


@router.get("/list")
async def list_resumes(
    session_id: str = None,
    request: Request = None
):
    """List all resumes in current or specified session."""
    try:
        user_id = "guest"
        if request:
            user_id = request.headers.get("X-User-Id", "guest")
        
        # List resumes in session
        files = blob_storage.list_blobs_session(
            user_id=user_id,
            session_id=session_id,  # None = current session
            prefix="raw_resumes/"
        )
        
        return JSONResponse({
            "status": "success",
            "session_id": session_id or blob_storage.get_current_session(user_id),
            "files": files,
            "count": len(files)
        })
        
    except Exception as e:
        raise HTTPException(500, str(e))


@router.post("/new-session")
async def start_new_session(request: Request = None):
    """Create a new upload session."""
    try:
        user_id = "guest"
        if request:
            user_id = request.headers.get("X-User-Id", "guest")
        
        # Create new session
        session_id = blob_storage.create_session(user_id)
        session_path = blob_storage.get_session_path(user_id, session_id)
        
        return JSONResponse({
            "status": "success",
            "message": "New session created",
            "session_id": session_id,
            "session_path": session_path
        })
        
    except Exception as e:
        raise HTTPException(500, str(e))
```

## Benefits of Session-Based Storage

### 1. **Easy Cleanup**
```python
# Delete old session when starting new one
old_sessions = blob_storage.list_user_sessions(user_id)
if len(old_sessions) > 5:  # Keep only 5 most recent
    for session in old_sessions[5:]:
        blob_storage.delete_session(user_id, session['session_id'])
```

### 2. **Session History**
```python
# Show user their previous upload sessions
sessions = blob_storage.list_user_sessions(user_id)
for session in sessions:
    print(f"Session {session['session_id']}")
    print(f"  Uploaded: {session['created']}")
    print(f"  Files: {session['blob_count']}")
```

### 3. **Multiple Active Sessions**
```python
# Work with specific session
session1 = "session_20250115_103045"
session2 = "session_20250115_143020"

# Upload to different sessions
blob_storage.upload_file_session(content1, "file1.pdf", user_id, session1)
blob_storage.upload_file_session(content2, "file2.pdf", user_id, session2)

# List files from each
files1 = blob_storage.list_blobs_session(user_id, session1)
files2 = blob_storage.list_blobs_session(user_id, session2)
```

## Frontend Integration

```javascript
// Create new session on "New Upload" button
async function startNewSession() {
  const response = await fetch('/api/sessions/create', {
    method: 'POST',
    headers: {
      'X-User-Id': currentUser.email
    }
  });
  const data = await response.json();
  console.log('New session:', data.session_id);
}

// List previous sessions
async function loadSessionHistory() {
  const response = await fetch('/api/sessions/list', {
    headers: {
      'X-User-Id': currentUser.email
    }
  });
  const data = await response.json();
  
  // Display sessions in UI
  data.sessions.forEach(session => {
    displaySession(session.session_id, session.created, session.blob_count);
  });
}

// Load specific session
async function loadSession(sessionId) {
  const response = await fetch(`/api/sessions/${sessionId}/files`, {
    headers: {
      'X-User-Id': currentUser.email
    }
  });
  const data = await response.json();
  
  // Display files from this session
  displayFiles(data.files);
}
```

## Migration Checklist

- [ ] Update `resumes.py` router to use session methods
- [ ] Update `ranking.py` to read/write from sessions
- [ ] Update `reporting.py` to save reports to sessions
- [ ] Test session creation and file upload
- [ ] Test listing sessions and files
- [ ] Test session deletion
- [ ] Update frontend to show session selector
- [ ] Add "New Session" button in UI
- [ ] Test with multiple users
- [ ] Add session cleanup policy
