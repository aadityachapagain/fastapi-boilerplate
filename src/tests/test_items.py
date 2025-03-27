import pytest
from bson import ObjectId
import datetime
from fastapi.testclient import TestClient

from src.db.models.items import Item


def test_get_items(test_client: TestClient, auth_headers, sample_item):
    """Test getting all items."""
    response = test_client.get("/api/v1/items", headers=auth_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0
    assert response.json()[0]["id"] == str(sample_item.id)
    assert response.json()[0]["name"] == sample_item.name
    # Check that the keys are in camelCase
    assert "directionFromNewYork" in response.json()[0]
    assert "direction_from_new_york" not in response.json()[0]


def test_get_items_empty(test_client: TestClient, auth_headers):
    """Test getting all items when no items exist."""
    # Delete all items first to ensure empty list
    Item.objects.delete()
    
    response = test_client.get("/api/v1/items", headers=auth_headers)
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) == 0


def test_get_item_by_id(test_client: TestClient, auth_headers, sample_item):
    """Test getting a specific item by ID."""
    response = test_client.get(f"/api/v1/items/{sample_item.id}", headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json()["id"] == str(sample_item.id)
    assert response.json()["name"] == sample_item.name
    assert response.json()["postcode"] == sample_item.postcode
    assert "directionFromNewYork" in response.json()


def test_get_item_by_id_not_found(test_client: TestClient, auth_headers):
    """Test getting a non-existent item."""
    fake_id = str(ObjectId())
    response = test_client.get(f"/api/v1/items/{fake_id}", headers=auth_headers)
    
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]


def test_get_item_by_id_invalid_id(test_client: TestClient, auth_headers):
    """Test getting an item with invalid ID format."""
    invalid_id = "not-a-valid-objectid"
    response = test_client.get(f"/api/v1/items/{invalid_id}", headers=auth_headers)
    
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]


def test_update_item(test_client: TestClient, auth_headers, sample_item):
    """Test updating an existing item."""
    
    update_data = {
        "name": "Updated Sample Item",
        "title": "Updated Title",
        "users": ["Updated Sample Item", "Another User"]
    }
    
    response = test_client.patch(
        f"/api/v1/items/{sample_item.id}", 
        headers=auth_headers, 
        json=update_data
    )
    
    assert response.status_code == 200
    assert "message" in response.json()


def test_update_item_no_fields(test_client: TestClient, auth_headers, sample_item):
    """Test updating an item with no fields to update."""
    response = test_client.patch(
        f"/api/v1/items/{sample_item.id}", 
        headers=auth_headers, 
        json={}
    )
    
    assert response.status_code == 400
    assert "detail" in response.json()
    assert "_" in response.json()["detail"]
    assert "No valid fields to update" in response.json()["detail"]["_"]


def test_update_item_not_found(test_client: TestClient, auth_headers):
    """Test updating a non-existent item."""
    fake_id = str(ObjectId())
    update_data = {"title": "Updated Title"}
    
    response = test_client.patch(
        f"/api/v1/items/{fake_id}", 
        headers=auth_headers, 
        json=update_data
    )
    
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]


def test_delete_item(test_client: TestClient, auth_headers, sample_item):
    """Test deleting an item."""
    response = test_client.delete(
        f"/api/v1/items/{sample_item.id}", 
        headers=auth_headers
    )
    
    assert response.status_code == 200
    assert "message" in response.json()
    assert "deleted successfully" in response.json()["message"]
    
    # Verify the item was actually deleted
    deleted_item = Item.objects(id=sample_item.id).first()
    assert deleted_item is None


def test_delete_item_not_found(test_client: TestClient, auth_headers):
    """Test deleting a non-existent item."""
    fake_id = str(ObjectId())
    
    response = test_client.delete(
        f"/api/v1/items/{fake_id}", 
        headers=auth_headers
    )
    
    assert response.status_code == 404
    assert "Item not found" in response.json()["detail"]


def test_missing_auth(test_client: TestClient):
    """Test accessing an endpoint without authentication."""
    response = test_client.get("/api/v1/items")
    
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Missing Authorization header" in response.json()["detail"]


def test_invalid_auth_format(test_client: TestClient):
    """Test accessing an endpoint with invalid auth format."""
    headers = {"Authorization": "InvalidFormat token123"}
    response = test_client.get("/api/v1/items", headers=headers)
    
    assert response.status_code == 401
    assert "detail" in response.json()
    assert "Invalid Authorization header format" in response.json()["detail"]


def test_empty_token(test_client: TestClient):
    """Test accessing an endpoint with empty token."""
    headers = {"Authorization": "Bearer "}
    response = test_client.get("/api/v1/items", headers=headers)
    
    assert response.status_code == 401
    assert "detail" in response.json()
    # Updated to match the actual error message
    assert "Invalid Authorization header format" in response.json()["detail"]