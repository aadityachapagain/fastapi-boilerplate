import logging
from mongoengine import connect, disconnect
from src.config import settings

logger = logging.getLogger(__name__)


def connect_to_database():
    """Connect to MongoDB database."""
    logger.info(f"Connecting to MongoDB database: {settings.MONGODB_DB_NAME}")
    try:
        connect(
            db=settings.MONGODB_DB_NAME,
            host=settings.MONGODB_URI,
            alias="default"
        )
        logger.info("Successfully connected to MongoDB")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise


def disconnect_from_database():
    """Disconnect from MongoDB database."""
    logger.info("Disconnecting from MongoDB")
    disconnect(alias="default")


def get_db():
    """Database dependency for FastAPI."""
    try:
        # This function will be used as a dependency in FastAPI
        # to ensure database connection for each request
        yield
    finally:
        # No need to do anything here as connection is established at app startup
        pass