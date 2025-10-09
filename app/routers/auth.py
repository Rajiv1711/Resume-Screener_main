# app/routers/auth.py
import os
import time
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
import jwt  # PyJWT

# Secret for signing tokens (in production use a secure secret or Key Vault)
JWT_SECRET = os.getenv("JWT_SECRET", "change_this_secret_for_dev")
JWT_ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_SECONDS = 60 * 60 * 24  # 1 day

router = APIRouter(prefix="/api/auth", tags=["auth"])


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_at: int


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
