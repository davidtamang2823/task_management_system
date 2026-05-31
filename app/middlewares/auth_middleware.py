import typing
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from jwt.exceptions import ExpiredSignatureError, InvalidTokenError

from settings import settings
from security import AuthHandler


EXEMPT_PATHS = [
    "/users/login",
    "/users/register",
    "/docs",
    "/redoc",
    "/openapi.json",
]


class JWTAuthMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: ASGIApp, exempt_paths: list[str] = EXEMPT_PATHS):
        super().__init__(app)
        self.exempt_paths = exempt_paths
        self.auth_handler = AuthHandler(
            secret_key=settings.secret_key,
            algorithm=settings.jwt_algorithm,
        )

    async def dispatch(self, request: Request, call_next: typing.Callable):
        if self._is_exempt(request.url.path):
            return await call_next(request)

        token = self._extract_token(request)
        if token is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Authorization header missing or invalid."},
            )

        payload = self._decode_token(token)
        if payload is None:
            return JSONResponse(
                status_code=status.HTTP_401_UNAUTHORIZED,
                content={"detail": "Token is invalid or expired."},
            )

        request.state.user_id = payload.get("user_id")
        request.state.role = payload.get("role")
        request.state.email = payload.get("email")

        return await call_next(request)

    def _is_exempt(self, path: str) -> bool:
        return any(path.startswith(exempt) for exempt in self.exempt_paths)

    def _extract_token(self, request: Request) -> str | None:
        authorization: str = request.headers.get("Authorization")
        if not authorization or not authorization.startswith("Bearer "):
            return None
        return authorization.removeprefix("Bearer ").strip()

    def _decode_token(self, token: str) -> dict | None:
        try:
            return self.auth_handler.decode_access_token(token)
        except ExpiredSignatureError:
            return None
        except InvalidTokenError:
            return None