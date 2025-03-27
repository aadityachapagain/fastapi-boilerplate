import pytest
import mongomock
import mongoengine
from fastapi.testclient import TestClient
from unittest.mock import patch, AsyncMock
import datetime

# Patch the main app to prevent connection issues during import
with patch('src.db.connection.connect_to_database'):
    from src.main import app

from src.db.models.items import Item


@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    # Disable app startup/shutdown events to prevent MongoDB connection issues
    app.router.on_startup = []
    app.router.on_shutdown = []
    
    with TestClient(app) as client:
        yield client


@pytest.fixture(autouse=True)
def mock_mongo():
    """Mock MongoDB connection for tests."""
    # Disconnect any existing connections
    mongoengine.disconnect_all()
    
    # Connect to MongoMock
    mongoengine.connect(
        db='mongoenginetest',
        host='mongodb://localhost',
        alias='default',
        mongo_client_class=mongomock.MongoClient
    )
    
    yield
    
    # Clean up
    mongoengine.disconnect_all()


@pytest.fixture
def mock_zipcode_api():
    """Mock the external zipcode API."""
    mock_response = {
        "latitude": 40.7128,
        "longitude": -74.0060,
        "place_name": "New York",
        "state": "New York",
        "state_abbreviation": "NY"
    }
    
    with patch('src.utils.geo.fetch_zipcode_data', new_callable=AsyncMock) as mock:
        mock.return_value = mock_response
        yield mock


@pytest.fixture
def mock_failed_zipcode_api():
    """Mock a failed zipcode API response."""
    with patch('src.utils.geo.fetch_zipcode_data', new_callable=AsyncMock) as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def valid_item_data():
    """Valid item data for testing."""
    # One week from now for start date
    start_date = datetime.datetime.now(datetime.UTC) + datetime.timedelta(weeks=1, days=1)
    
    return {
        "name": "Test Item",
        "postcode": "10001",
        "title": "Test Title",
        "users": ["Test Item", "User Two", "User Three"],
        "startDate": start_date.isoformat()
    }


@pytest.fixture
def invalid_item_data():
    """Invalid item data for testing."""
    return {
        "name": "Test Item",
        "postcode": "invalid",  # Invalid postcode
        "title": "Test Title",
        "users": ["User One", "User Two"],  # Name not in users
        "startDate": datetime.datetime.now(datetime.UTC).isoformat()  # Invalid start date (too soon)
    }


@pytest.fixture
def sample_item():
    """Create a sample item in the database."""
    start_date = datetime.datetime.now(datetime.UTC) + datetime.timedelta(weeks=1, days=1)
    
    item = Item(
        name="Sample Item",
        postcode="10001",
        latitude=40.7128,
        longitude=-74.0060,
        direction_from_new_york="NE",
        title="Sample Title",
        users=["Sample Item", "User Two", "User Three"],
        start_date=start_date
    )
    item.save()
    
    yield item
    
    # Clean up
    try:
        Item.objects(id=item.id).delete()
    except:
        pass


@pytest.fixture
def auth_headers():
    """Authentication headers for testing."""
    return {"Authorization": "Bearer test-token"}