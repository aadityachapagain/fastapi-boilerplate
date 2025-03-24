import logging
import time
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging request and response information."""
    
    async def dispatch(self, request: Request, call_next):
        """Process request and response for logging.
        
        Args:
            request: The incoming request
            call_next: Function to call the next middleware/handler
            
        Returns:
            Response: The response from the handler
        """
        # unique request ID
        request_id = str(time.time())
        
        logger.info(
            f"Request [{request_id}]: {request.method} {request.url.path} "
            f"(Client: {request.client.host if request.client else 'Unknown'})"
        )
        
        # Start timer
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            logger.info(
                f"Response [{request_id}]: {response.status_code} "
                f"(Processed in {process_time:.4f}s)"
            )
            response.headers["X-Process-Time"] = f"{process_time:.4f}"
            
            return response
            
        except Exception as e:
            logger.error(
                f"Error [{request_id}]: {str(e)} "
                f"(Processed in {time.time() - start_time:.4f}s)"
            )
            raise