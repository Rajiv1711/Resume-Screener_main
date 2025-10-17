from typing import Callable, List

from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Authentication middleware to protect routes and return 401 for unauthenticated API calls.
    """

    def __init__(
        self,
        app: ASGIApp,
        protected_paths: List[str] | None = None,
        login_path: str = "/api/auth/session-login",
    ):
        super().__init__(app)
        self.protected_paths = protected_paths or [
            "/api/",
        ]
        self.login_path = login_path

    async def dispatch(self, request: Request, call_next: Callable):
        path = request.url.path

        # Skip auth check for auth-related paths and static/docs
        if (
            path.startswith("/api/auth/")
            or path in ["/", "/docs", "/openapi.json", "/redoc"]
            or path.startswith("/static/")
        ):
            # Still populate request.state.user if session exists
            try:
                user = request.session.get("user") if hasattr(request, "session") else None
                auth = request.session.get("authenticated") if hasattr(request, "session") else False
                if auth and user:
                    request.state.user = user
            except Exception:
                pass
            return await call_next(request)

        # Attach user info to request.state when available
        try:
            user = request.session.get("user") if hasattr(request, "session") else None
            auth = request.session.get("authenticated") if hasattr(request, "session") else False
            if auth and user:
                request.state.user = user
        except Exception:
            # Session middleware not available; continue without state
            pass

        # Check if path requires authentication
        requires_auth = any(path.startswith(p) for p in self.protected_paths)

        if requires_auth:
            try:
                if (not hasattr(request, "session") or
                    "user" not in request.session or
                    not request.session.get("authenticated")):
                    return JSONResponse(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        content={"detail": "Authentication required"},
                    )
            except (AssertionError, AttributeError):
                # Session middleware not available, skip auth check
                return await call_next(request)

        return await call_next(request)