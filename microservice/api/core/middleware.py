from datetime import datetime, timezone, timedelta
from typing import Any, Callable

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, Response, status
from starlette.middleware.base import BaseHTTPMiddleware

from core.config import settings


class RateLimiter:
    def __init__(self):
        self.ip_cache: dict[str, list[datetime]] = {}
        self.token_cache: dict[str, list[datetime]] = {}
        self.cleanup_counter = 0

    @staticmethod
    def _cleanup_old_requests(cache: dict[str, list[datetime]]) -> None:
        now = datetime.now(timezone.utc)
        window_time = now - timedelta(seconds=settings.RATE_LIMIT_WINDOW_SECONDS)

        for key in cache.keys():
            cache[key] = [ts for ts in cache[key] if ts > window_time]

            if not cache[key]:
                del cache[key]

    def is_rate_limited(self, ip: str, token: str | None = None) -> tuple[bool, dict[str, Any]]:
        now = datetime.now(timezone.utc)

        self.cleanup_counter += 1

        if self.cleanup_counter > 100:
            self._cleanup_old_requests(self.ip_cache)
            self._cleanup_old_requests(self.token_cache)
            self.cleanup_counter = 0

        # IP-based rate limiting
        ip_requests = self.ip_cache.get(ip, [])
        window_time = now - timedelta(seconds=settings.RATE_LIMIT_WINDOW_SECONDS)
        ip_requests = [ts for ts in ip_requests if ts > window_time]

        # Token-based rate limiting
        token_requests = []
        if token:
            token_requests = self.token_cache.get(token, [])
            token_requests = [ts for ts in token_requests if ts > window_time]

        if token and len(token_requests) >= settings.RATE_LIMIT_AUTH_REQUESTS:
            remaining = 0
            limit = settings.RATE_LIMIT_AUTH_REQUESTS
            is_limited = True
        elif not token and len(ip_requests) >= settings.RATE_LIMIT_ANON_REQUESTS:
            remaining = 0
            limit = settings.RATE_LIMIT_ANON_REQUESTS
            is_limited = True
        else:
            if token:
                remaining = settings.RATE_LIMIT_AUTH_REQUESTS - len(token_requests)
                limit = settings.RATE_LIMIT_AUTH_REQUESTS
            else:
                remaining = settings.RATE_LIMIT_ANON_REQUESTS - len(ip_requests)
                limit = settings.RATE_LIMIT_ANON_REQUESTS

            if token:
                if token not in self.token_cache:
                    self.token_cache[token] = []
                self.token_cache[token].append(now)

            if ip not in self.ip_cache:
                self.ip_cache[ip] = []
            self.ip_cache[ip].append(now)

            is_limited = False

        headers = {
            "X-RateLimit-Limit": str(limit),
            "X-RateLimit-Remaining": str(max(0, remaining)),
            "X-RateLimit-Reset": str(
                int((window_time + timedelta(seconds=settings.RATE_LIMIT_WINDOW_SECONDS)).timestamp()))
        }

        return is_limited, headers


class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app: FastAPI) -> None:
        super().__init__(app)
        self.limiter = RateLimiter()

    async def dispatch(self, request: Request, call_next: Callable):

        ip = request.client.host

        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header[7:]

        is_limited, headers = self.limiter.is_rate_limited(ip, token)

        if is_limited:
            return Response(
                content='{"detail": "Too many requests"}',
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                media_type="application/json",
                headers=headers
            )

        response = await call_next(request)

        for key, value in headers.items():
            response.headers[key] = value

        return response


def add_middleware(app: FastAPI) -> None:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ALLOW_ORIGINS,
        allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
        allow_methods=settings.CORS_ALLOW_METHODS,
        allow_headers=settings.CORS_ALLOW_HEADERS,
        max_age=settings.CORS_MAX_AGE,
    )

    app.add_middleware(RateLimitMiddleware)
