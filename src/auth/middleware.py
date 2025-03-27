import logging
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

logger = logging.getLogger(__name__)

# Security scheme for OpenAPI documentation
auth_scheme = HTTPBearer()


class AuthMiddleware:
    """Authentication middleware to validate bearer tokens."""
    
    async def __call__(self, request: Request):
        """Validate the authorization header.
        
        Args:
            request: The incoming request
            
        Raises:
            HTTPException: If no valid token is provided
            
        Returns:
            dict: Empty dict to satisfy dependency requirements
        """
        # Extract the Authorization header
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning("Missing Authorization header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header"
            )
        
        # Check if it's a valid Bearer token format
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("Invalid Authorization header format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format. Use 'Bearer your_token'"
            )
        
        # Get the token
        token = parts[1]
        
        if not token:
            logger.warning("Empty token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty token provided"
            )
        
        # For this task, we accept any non-empty token as valid
        # In a real application, this would validate the token against
        # a JWT secret, user database, etc.
        logger.info(f"Request authenticated with token: {token[:5]}...")
        
        # Return an empty dict to satisfy dependency requirements
        return {}