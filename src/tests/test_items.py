import pytest
from bson import ObjectId
import datetime
from fastapi.testclient import TestClient

from src.db.models import Item


def test_get_items(test_client: TestClient, auth_headers, sample_item):
    """Test getting all items."""
    response = test_client.get("/items", headers=auth_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == str(sample_item.id)
    assert response.json()[0]["name"] == sample_item.name
    # Check that the keys are in camelCase
    assert "directionFromNewYork" in response.json()[0]
    assert "direction_from_new_york" not in response.json()[0]


def test_get_item_by_id(test_client: TestClient, auth_headers, sample_item):
    """Test getting a specific item by ID."""
    response = test_client.get(f"/items/{sample_item.id}", headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json()["id"] == str(sample_item.id)
    assert response.json()["name"] == sample_item.name
    assert response.json()["postcode"] == sample_item.postcode
    assert "directionFromNewYork" in response.json()


def test_get_item_by_id_not_found(test_client: TestClient, auth_headers):
    """Test getting a non-existent item."""
    fake_id = str(ObjectId())
    response = test_client.get(f"/items/{fake_id}", headers=auth_headers)
    
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]


def test_get_item_by_id_invalid_id(test_client: TestClient, auth_headers):
    """Test getting an item with invalid ID format."""
    # TODO
    pass


def test_create_item(test_client: TestClient, auth_headers, valid_item_data, mock_zipcode_api):
    """Test creating a new item."""
    # TODO 
    pass


def test_create_item_validation_error(test_client: TestClient, auth_headers, invalid_item_data):
    """Test creating an item with invalid data."""
    # TODO
    pass



def test_update_item_not_found(test_client: TestClient, auth_headers):
    """Test updating a non-existent item."""
    # TODO
    pass


def test_delete_item(test_client: TestClient, auth_headers, sample_item):
    """Test deleting an item."""
    # TODO
    pass
    


def test_delete_item_not_found(test_client: TestClient, auth_headers):
    """Test deleting a non-existent item."""
    # TODO
    pass