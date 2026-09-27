import time
from typing import Dict, Tuple
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from app.logging.logger import logger

class RateLimitMiddleware(BaseHTTPMiddleware):
    """In-memory Token-Bucket Rate Limiter protecting Auth Endpoints"""

    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.client_records: Dict[str, Tuple[int, float]] = {}

    async def dispatch(self, request: Request, call_next):
        path = request.url.path
        # Apply rate limiting to sensitive authentication endpoints
        if path in ["/api/v1/auth/login", "/api/v1/auth/register", "/api/v1/auth/forgot-password"]:
            client_ip = request.client.host if request.client else "127.0.0.1"
            now = time.time()
            
            count, reset_at = self.client_records.get(client_ip, (0, now + 60.0))
            if now > reset_at:
                count = 0
                reset_at = now + 60.0
            
            if count >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for IP: {client_ip} on endpoint {path}")
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Too many authentication attempts. Please wait 1 minute before retrying."
                )

            self.client_records[client_ip] = (count + 1, reset_at)

        return await call_next(request)
