"""
Logging and monitoring utilities
"""
import logging
import time
import json
from datetime import datetime
from typing import Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("qalytics")


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware to log all HTTP requests and responses"""
    
    async def dispatch(self, request: Request, call_next) -> Response:
        # Skip logging for health checks and static files
        if request.url.path in ["/api/health", "/docs", "/redoc", "/openapi.json"] or request.url.path.startswith("/reports"):
            return await call_next(request)
        
        start_time = time.time()
        
        try:
            # Process request (don't read body - let the app handle it)
            response = await call_next(request)
        except Exception as e:
            logger.error(json.dumps({
                "timestamp": datetime.utcnow().isoformat(),
                "method": request.method,
                "path": request.url.path,
                "error": str(e),
            }))
            raise
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log the request
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2),
        }
        
        # Add query params if present
        if request.query_params:
            log_data["query"] = dict(request.query_params)
        
        # Log at different levels based on status code
        if response.status_code >= 500:
            logger.error(json.dumps(log_data))
        elif response.status_code >= 400:
            logger.warning(json.dumps(log_data))
        else:
            logger.info(json.dumps(log_data))
        
        # Add timing header
        response.headers["X-Process-Time"] = str(duration)
        return response


def log_error(action: str, error: Exception, context: Optional[dict] = None):
    """Log an error with context"""
    error_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "error_type": type(error).__name__,
        "error_message": str(error),
        "context": context or {},
    }
    logger.error(json.dumps(error_data))


def log_info(action: str, message: str, context: Optional[dict] = None):
    """Log an info message with context"""
    info_data = {
        "timestamp": datetime.utcnow().isoformat(),
        "action": action,
        "message": message,
        "context": context or {},
    }
    logger.info(json.dumps(info_data))
