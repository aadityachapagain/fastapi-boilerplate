from fastapi import Depends, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.auth.middleware import AuthMiddleware


auth_middleware = AuthMiddleware()

security = HTTPBearer()


def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """Dependency for authenticated endpoints.
    
    Args:
        credentials: The credentials extracted from the request by FastAPI
        
    Returns:
        dict: Empty dict to satisfy dependency requirements
    """
    # usually returns actual authenticated user data
    # but for now lets just return empty
    return {}


authenticated = Depends(auth_middleware)