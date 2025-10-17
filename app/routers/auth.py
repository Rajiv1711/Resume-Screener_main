# app/routers/auth.py
import os
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt  # PyJWT
from app.services.guest_auth import guest_session_manager

# Secret for signing tokens (in production use a secure secret or Key Vault)
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret_for_dev")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24  # 1 day

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int


class GuestTokenResponse(BaseModel):
    access_token: str
    token_type: str = "guest"
    expires_at: str  # ISO format datetime string
    remaining_seconds: int
    session_type: str = "guest"


class GuestSessionInfo(BaseModel):
    ip_address: str
    created_at: str
    expires_at: str
    remaining_seconds: int
    is_active: bool


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Mock login endpoint (dev). Accepts username/password, returns signed JWT.
    Replace this with Microsoft Entra ID / OAuth2 in production.
    """

    # >>> MOCK AUTH: Accept any username/password for dev.
    # Add real credential checking here / integration with Entra in prod.
    username = form_data.username
    if not username:
        raise HTTPException(status_code=400, detail="Missing username")

    now = int(time.time())
    expires = now + ACCESS_TOKEN_EXPIRE_SECONDS

    payload = {
        "sub": username,
        "iat": now,
        "exp": expires,
        "roles": ["recruiter"]  # example claim
    }

    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

    return TokenResponse(access_token=token, expires_at=expires)


@router.post("/session-login")
def session_login(request: Request, form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Session-based login: sets server-side session instead of returning JWT.
    """
    username = form_data.username
    if not username:
        raise HTTPException(status_code=400, detail="Missing username")

    # Mock password check; replace with real auth in production
    user = {
        "username": username,
        "auth_type": "password",
        "roles": ["recruiter"],
        "login_time": int(time.time()),
    }
    request.session["authenticated"] = True
    request.session["user"] = user

    return {"message": "Logged in", "user": user}


def verify_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


# Dependency to use in routers that need authentication
def get_current_user(authorization: Optional[str] = None):
    """
    Use as Depends(get_current_user) in protected endpoints.
    FastAPI will inject header values if you declare parameter name `authorization`.
    """
    # If header is provided as "Bearer <token>"
    if authorization is None:
        # Try fastapi to extract from header via special name
        raise HTTPException(status_code=401, detail="Missing Authorization header")

    if authorization.startswith("Bearer "):
        token = authorization.split(" ", 1)[1]
    else:
        token = authorization

    return verify_token(token)


# Helper function to get client IP
def get_client_ip(request: Request) -> str:
    """
    Extract the real client IP address from the request.
    Checks X-Forwarded-For header first (for reverse proxies), then falls back to client host.
    """
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # X-Forwarded-For can contain multiple IPs, take the first one
        return forwarded_for.split(",")[0].strip()
    
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip.strip()
    
    # Fallback to client host
    client_host = request.client.host if request.client else "unknown"
    return client_host


@router.post("/guest-login", response_model=GuestTokenResponse)
def guest_login(request: Request):
    """
    Create a guest session for the client's IP address.
    Allows 3-minute access without authentication.
    """
    client_ip = get_client_ip(request)
    
    if not client_ip or client_ip == "unknown":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to determine client IP address"
        )
    
    try:
        token, expires_at = guest_session_manager.create_guest_session(client_ip)
        
        # Calculate remaining seconds
        remaining_seconds = int((expires_at.timestamp() - time.time()))
        
        return GuestTokenResponse(
            access_token=token,
            expires_at=expires_at.isoformat(),
            remaining_seconds=remaining_seconds
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create guest session: {str(e)}"
        )


@router.get("/guest-status", response_model=GuestSessionInfo)
def get_guest_status(request: Request):
    """
    Check the status of the current guest session for this IP address.
    """
    client_ip = get_client_ip(request)
    
    if not client_ip or client_ip == "unknown":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to determine client IP address"
        )
    
    # We need to get the token from the Authorization header to validate
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ", 1)[1]
    session_info = guest_session_manager.validate_guest_token(token, client_ip)
    
    if not session_info:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired guest session"
        )
    
    return GuestSessionInfo(
        ip_address=session_info["ip_address"],
        created_at=session_info["created_at"].isoformat(),
        expires_at=session_info["expires_at"].isoformat(),
        remaining_seconds=session_info["remaining_seconds"],
        is_active=True
    )


@router.post("/guest-logout")
def guest_logout(request: Request):
    """
    Revoke/logout from the guest session for this IP address.
    """
    client_ip = get_client_ip(request)
    
    if not client_ip or client_ip == "unknown":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unable to determine client IP address"
        )
    
    guest_session_manager.revoke_guest_session(client_ip)
    return {"message": "Guest session revoked successfully"}


@router.post("/logout")
def logout(request: Request):
    """Clear the server-side session."""
    request.session.clear()
    return {"message": "Logged out"}
