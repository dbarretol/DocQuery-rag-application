import uuid
from contextvars import ContextVar
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request

# ContextVar to store the request ID for the current task/request
request_id_ctx: ContextVar[str] = ContextVar("request_id", default="unknown")

class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get ID from header or generate new
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        
        # Set the context variable
        token = request_id_ctx.set(request_id)
        
        try:
            response = await call_next(request)
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            # Reset context
            request_id_ctx.reset(token)
