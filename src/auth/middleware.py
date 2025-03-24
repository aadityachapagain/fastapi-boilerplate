import logging
from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.requests import Request

logger = logging.getLogger(__name__)

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
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
            logger.warning("Missing Authorization header")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing Authorization header"
            )
        
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0].lower() != "bearer":
            logger.warning("Invalid Authorization header format")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Authorization header format. Use 'Bearer your_token'"
            )
        
        token = parts[1]
        
        if not token:
            logger.warning("Empty token provided")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty token provided"
            )
        
        # for now only accept non-empty token as valid
        # this would validate the token against
        # a JWT secret, user database, etc.
        logger.info(f"Request authenticated with token: {token[:5]}...")
        
        return {}