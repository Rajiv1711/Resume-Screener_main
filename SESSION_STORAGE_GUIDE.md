# Session-Based Blob Storage Guide

## Overview

The Resume Screener now supports **session-based storage** where each user's uploads are organized by user and timestamp-based sessions.

## Storage Structure

```
your-container-name/
├── user1@email.com/
│   ├── session_20250115_103045/
│   │   ├── raw_resumes/
│   │   │   ├── resume1.pdf
│   │   │   └── resume2.pdf
│   │   ├── processed/
│   │   │   ├── resume1.pdf.txt
│   │   │   └── resume2.pdf.txt
│   │   └── reports/
│   │       ├── ranked_resumes.json
│   │       ├── ranked_resumes.csv
│   │       └── ranked_resumes.xlsx
│   └── session_20250115_143020/
│       ├── raw_resumes/
│       └── reports/
├── user2@email.com/
│   └── session_20250115_110000/
│       └── raw_resumes/
└── guest/
    └── session_20250115_120000/
        └── raw_resumes/
```

## Key Features

### 1. **User Isolation**
- Each user gets their own folder based on their email/username
- Guest users use "guest" as their identifier

### 2. **Session Management**
- New session created automatically on first upload
- Sessions identified by timestamp: `session_YYYYMMDD_HHMMSS`
- All files in a session are grouped together

### 3. **Session Operations**
- Create new sessions manually
- List all sessions for a user
- Delete old sessions
- View files in specific sessions

## API Endpoints

### Session Management

#### Create New Session
```http
POST /api/sessions/create
Headers: X-User-Id: user@email.com
```

Response:
```json
{
  "status": "success",
  "session_id": "session_20250115_103045",
  "session_path": "user@email.com/session_20250115_103045/",
  "user_id": "user@email.com"
}
```

#### Get Current Session
```http
GET /api/sessions/current
Headers: X-User-Id: user@email.com
```

Response:
```json
{
  "status": "success",
  "session_id": "session_20250115_103045",
  "session_path": "user@email.com/session_20250115_103045/",
  "user_id": "user@email.com"
}
```

#### List All Sessions
```http
GET /api/sessions/list
Headers: X-User-Id: user@email.com
```

Response:
```json
{
  "status": "success",
  "user_id": "user@email.com",
  "sessions": [
    {
      "session_id": "session_20250115_143020",
      "created": "2025-01-15T14:30:20",
      "blob_count": 15
    },
    {
      "session_id": "session_20250115_103045",
      "created": "2025-01-15T10:30:45",
      "blob_count": 8
    }
  ],
  "total": 2
}
```

#### List Files in Session
```http
GET /api/sessions/session_20250115_103045/files?prefix=raw_resumes/
Headers: X-User-Id: user@email.com
```

Response:
```json
{
  "status": "success",
  "session_id": "session_20250115_103045",
  "files": [
    "raw_resumes/resume1.pdf",
    "raw_resumes/resume2.pdf"
  ],
  "total": 2
}
```

#### Delete Session
```http
DELETE /api/sessions/session_20250115_103045
Headers: X-User-Id: user@email.com
```

Response:
```json
{
  "status": "success",
  "session_id": "session_20250115_103045",
  "deleted_blobs": 15
}
```

## Python API Usage

### Using Session-Based Methods

```python
from app.services.blob_storage import blob_storage

# Get user ID from authentication
user_id = "user@email.com"

# Create a new session
session_id = blob_storage.create_session(user_id)
print(f"Created session: {session_id}")

# Upload file to current session
with open("resume.pdf", "rb") as f:
    url = blob_storage.upload_file_session(
        file_content=f.read(),
        blob_name="raw_resumes/resume.pdf",
        user_id=user_id
    )
print(f"Uploaded to: {url}")

# List files in current session
files = blob_storage.list_blobs_session(
    user_id=user_id,
    prefix="raw_resumes/"
)
print(f"Files: {files}")

# Download file from session
content = blob_storage.download_file_session(
    blob_name="raw_resumes/resume.pdf",
    user_id=user_id
)

# List all user's sessions
sessions = blob_storage.list_user_sessions(user_id)
for session in sessions:
    print(f"Session: {session['session_id']}")
    print(f"  Created: {session['created']}")
    print(f"  Files: {session['blob_count']}")

# Delete old session
deleted = blob_storage.delete_session(user_id, "session_20250115_103045")
print(f"Deleted {deleted} files")
```

### Using Specific Session

```python
# Upload to a specific session
url = blob_storage.upload_file_session(
    file_content=content,
    blob_name="raw_resumes/resume.pdf",
    user_id=user_id,
    session_id="session_20250115_103045"  # Specific session
)

# List files from specific session
files = blob_storage.list_blobs_session(
    user_id=user_id,
    session_id="session_20250115_103045",
    prefix="reports/"
)
```

## Updating Existing Code

### Before (Old Method)
```python
# Old per-user method
blob_storage.upload_file_user(content, "raw_resumes/file.pdf", user_id)
```

### After (Session-Based)
```python
# New session-based method
blob_storage.upload_file_session(content, "raw_resumes/file.pdf", user_id)
# Automatically uses current session
```

## Migration Strategy

You have two options:

### Option 1: Keep Both (Recommended)
- Keep existing `upload_file_user()` methods for backward compatibility
- Add new `upload_file_session()` methods for new features
- Gradually migrate endpoints to use session-based methods

### Option 2: Full Migration
- Update all upload/download calls to use session methods
- Test thoroughly before deploying
- Old data remains accessible but won't be session-organized

## Benefits

1. **Organization**: Files grouped by upload session
2. **Cleanup**: Easy to delete old upload batches
3. **Tracking**: Know when files were uploaded
4. **Isolation**: Complete separation between users
5. **History**: View previous upload sessions

## Testing

```bash
# Start the server
uvicorn app.main:app --reload

# Create a session
curl -X POST http://localhost:8000/api/sessions/create \
  -H "X-User-Id: test@example.com"

# List sessions
curl http://localhost:8000/api/sessions/list \
  -H "X-User-Id: test@example.com"

# Get current session
curl http://localhost:8000/api/sessions/current \
  -H "X-User-Id: test@example.com"
```

## Security Considerations

1. **User ID from Authentication**: Always get `user_id` from authenticated session, not from user input
2. **Session Validation**: Verify user owns the session before allowing access
3. **Access Control**: Only allow users to access their own sessions
4. **Sanitization**: User IDs are sanitized to prevent path traversal

## Future Enhancements

Possible additions:
- Session metadata (job description, number of resumes, etc.)
- Session sharing between users
- Session expiration policies
- Session analytics
- Batch operations on sessions
