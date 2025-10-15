"""
Session Management API Router
Handles creation, listing, and deletion of user upload sessions
"""
from fastapi import APIRouter, HTTPException, Request, Body
from fastapi.responses import JSONResponse
from typing import Optional
from pydantic import BaseModel
from app.services.blob_storage import blob_storage


class CreateSessionRequest(BaseModel):
    name: Optional[str] = None


class UpdateSessionRequest(BaseModel):
    name: str

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/create")
async def create_new_session(
    body: CreateSessionRequest = Body(default=CreateSessionRequest()),
    request: Request = None
):
    """
    Create a new session for the current user with optional custom name.
    
    Request Body:
        name: Optional custom name for the session
    
    Returns:
        Session ID, name, and session path
    """
    try:
        # Get user ID from headers
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header
        
        # Create new session with optional name
        session_id = blob_storage.create_session(user_id, body.name)
        session_path = blob_storage.get_session_path(user_id, session_id)
        
        # Get metadata to return the assigned name
        sessions = blob_storage.list_user_sessions(user_id)
        session_info = next((s for s in sessions if s['session_id'] == session_id), {})
        
        return JSONResponse(content={
            "status": "success",
            "session_id": session_id,
            "name": session_info.get('name', body.name),
            "session_path": session_path,
            "user_id": user_id
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/current")
async def get_current_session(request: Request = None):
    """
    Get the current active session for the user.
    
    Returns:
        Current session ID and path
    """
    try:
        # Get user ID
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header
        
        session_id = blob_storage.get_current_session(user_id)
        session_path = blob_storage.get_session_path(user_id, session_id)
        
        return JSONResponse(content={
            "status": "success",
            "session_id": session_id,
            "session_path": session_path,
            "user_id": user_id
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list")
async def list_sessions(request: Request = None):
    """
    List all sessions for the current user.
    
    Returns:
        Array of session info with session_id, created timestamp, and blob count
    """
    try:
        # Get user ID
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header
        
        sessions = blob_storage.list_user_sessions(user_id)
        
        return JSONResponse(content={
            "status": "success",
            "user_id": user_id,
            "sessions": sessions,
            "total": len(sessions)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}/name")
async def update_session_name(
    session_id: str,
    body: UpdateSessionRequest,
    request: Request = None
):
    """
    Update the name of a session.
    
    Args:
        session_id: The session ID to update
        body: Request body with new name
        
    Returns:
        Updated session info
    """
    try:
        # Get user ID
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header
        
        # Update session name
        success = blob_storage.update_session_name(user_id, session_id, body.name)
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to update session name")
        
        return JSONResponse(content={
            "status": "success",
            "session_id": session_id,
            "name": body.name
        })
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{session_id}/set-active")
async def set_active_session(session_id: str, request: Request = None):
    """
    Set a specific session as the active session for the user.
    
    Args:
        session_id: The session ID to set as active
        
    Returns:
        Success status and session info
    """
    try:
        # Get user ID
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header
        
        # Set active session (store in the internal dict)
        blob_storage._user_sessions[user_id] = session_id
        session_path = blob_storage.get_session_path(user_id, session_id)
        
        return JSONResponse(content={
            "status": "success",
            "message": "Active session updated",
            "session_id": session_id,
            "session_path": session_path
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}")
async def delete_session(session_id: str, request: Request = None):
    """
    Delete a specific session and all its blobs.
    
    Args:
        session_id: The session ID to delete
        
    Returns:
        Number of blobs deleted
    """
    try:
        # Get user ID
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header
        
        # Delete session
        deleted_count = blob_storage.delete_session(user_id, session_id)
        
        return JSONResponse(content={
            "status": "success",
            "session_id": session_id,
            "deleted_blobs": deleted_count
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}/files")
async def list_session_files(session_id: str, prefix: str = "", request: Request = None):
    """
    List all files in a specific session.
    
    Args:
        session_id: The session ID
        prefix: Optional prefix to filter files (e.g., 'raw_resumes/')
        
    Returns:
        List of file names in the session
    """
    try:
        # Get user ID
        user_id = "guest"
        if request is not None:
            auth_header = request.headers.get("X-User-Id") or request.headers.get("x-user-id")
            if auth_header:
                user_id = auth_header
        
        # List files
        files = blob_storage.list_blobs_session(user_id, session_id, prefix)
        
        return JSONResponse(content={
            "status": "success",
            "session_id": session_id,
            "files": files,
            "total": len(files)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
