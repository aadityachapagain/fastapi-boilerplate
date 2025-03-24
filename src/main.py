import logging
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from src.config import settings
from src.db.connection import connect_to_database, disconnect_from_database
from src.events import init_event_listeners
from src.routers.items.routes import router as items_router
from src.routers.items.events import register_item_events

from contextlib import asynccontextmanager

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize application on startup."""

    logger.info("Application starting up")
    connect_to_database()
    init_event_listeners()
    register_item_events()
    logger.info("Application started successfully")

    yield
    
    logger.info("Application shutting down")
    disconnect_from_database()   
    logger.info("Application shutdown complete")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="A scalable and testable REST API for managing Items",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler for unhandled exceptions."""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )

# usually when we deploy apps to k8s or ecs
# they need endpoint to check if container is healthy or not
@app.get("/", tags=["Health"])
async def read_root():
    """Root endpoint for health checks."""
    return {"status": "ok", "version": settings.APP_VERSION}


# include all the router here
app.include_router(items_router, prefix="/api/v1")



if __name__ == "__main__":
    uvicorn.run("src.main:app", host="0.0.0.0", port=8000, reload=True)