import logging
from typing import Dict, List, Optional, Tuple, Any
from bson import ObjectId
from datetime import datetime

from src.db.models.items import Item
from src.events import emit_event
from src.utils.geo import fetch_zipcode_data, calculate_direction
from src.utils.validators import (
    convert_keys_to_snake_case, 
    convert_keys_to_camel_case,
    validate_item_data,
    validate_start_date
)

logger = logging.getLogger(__name__)


class ItemService:
    """Service for managing items."""
    
    @staticmethod
    async def create_item(data: Dict[str, Any]) -> Tuple[Optional[str], Optional[Dict[str, str]]]:
        """Create a new item.
        
        Args:
            data: Item data in camelCase
            
        Returns:
            tuple: (item_id, errors)
                - item_id: ID of created item if successful, None otherwise
                - errors: Dictionary with field names as keys and error messages as values
        """
        snake_data = convert_keys_to_snake_case(data)
        
        # Validate data
        is_valid, errors = validate_item_data(snake_data)
        if not is_valid:
            logger.warning(f"Item validation failed: {errors}")
            return None, errors
        
        try:
            location_data = await fetch_zipcode_data(snake_data["postcode"])
            if not location_data:
                logger.error(f"Failed to fetch location data for postcode: {snake_data['postcode']}")
                return None, {"postcode": "Invalid or unrecognized postcode"}
            
            # Set latitude and longitude
            snake_data["latitude"] = location_data["latitude"]
            snake_data["longitude"] = location_data["longitude"]
            
            # Calculate direction from New York
            snake_data["direction_from_new_york"] = calculate_direction(
                snake_data["latitude"], 
                snake_data["longitude"]
            )
            
            item = Item(**snake_data)
            item.save()
            
            emit_event("item_created", {"item_id": str(item.id)})
            
            logger.info(f"Item created with ID: {item.id}")
            return str(item.id), None
            
        except Exception as e:
            logger.error(f"Error creating item: {str(e)}")
            return None, {"server": f"Internal error: {str(e)}"}
    
    @staticmethod
    def get_all_items() -> List[Dict[str, Any]]:
        """Get all items.
        
        Returns:
            list: List of items in dict format with camelCase keys
        """
        logger.info("Fetching all items")
        try:
            items = Item.objects.all()
            return [convert_keys_to_camel_case(item.to_dict()) for item in items]
        except Exception as e:
            logger.error(f"Error fetching items: {str(e)}")
            return []
    
    @staticmethod
    def get_item_by_id(item_id: str) -> Optional[Dict[str, Any]]:
        """Get item by ID.
        
        Args:
            item_id: The ID of the item to fetch
            
        Returns:
            dict: Item data with camelCase keys if found, None otherwise
        """
        logger.info(f"Fetching item with ID: {item_id}")
        try:
            if not ObjectId.is_valid(item_id):
                logger.warning(f"Invalid item ID format: {item_id}")
                return None
            
            item = Item.objects(id=item_id).first()
            if not item:
                logger.warning(f"Item not found with ID: {item_id}")
                return None
            
            return convert_keys_to_camel_case(item.to_dict())
        except Exception as e:
            logger.error(f"Error fetching item: {str(e)}")
            return None
    
    @staticmethod
    async def update_item(item_id: str, data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
        """Update an existing item.
        
        Args:
            item_id: The ID of the item to update
            data: Item data in camelCase (only mutable fields)
            
        Returns:
            tuple: (success, errors)
                - success: True if update was successful, False otherwise
                - errors: Dictionary with field names as keys and error messages as values
        """
        logger.info(f"Updating item with ID: {item_id}")
        
        # Convert camelCase to snake_case
        snake_data = convert_keys_to_snake_case(data)
        
        try:
            # Validate ObjectId format
            if not ObjectId.is_valid(item_id):
                logger.warning(f"Invalid item ID format: {item_id}")
                return False, {"id": "Invalid item ID format"}
            
            # Get existing item
            item = Item.objects(id=item_id).first()
            if not item:
                logger.warning(f"Item not found with ID: {item_id}")
                return False, {"id": "Item not found"}
            
            # Only allow updating mutable fields
            mutable_fields = ["name", "title", "users", "start_date"]
            update_data = {k: v for k, v in snake_data.items() if k in mutable_fields}
            
            if "name" in update_data and "users" not in update_data:
                if update_data["name"] not in item.users:
                    # Check against existing users if users not updated
                    logger.warning(f"Name '{update_data['name']}' not in users list")
                    return False, {"name": "Name must be included in the users list"}
            elif "name" in update_data and "users" in update_data:
                # Check against new users if both updated
                if update_data["name"] not in update_data["users"]:
                    logger.warning(f"Name '{update_data['name']}' not in updated users list")
                    return False, {"name": "Name must be included in the users list"}
            elif "users" in update_data and "name" not in update_data:
                # Check existing name against new users
                if item.name not in update_data["users"]:
                    logger.warning(f"Existing name '{item.name}' not in updated users list")
                    return False, {"users": "Users list must include the item name"}
            
            # Validate start_date if provided
            if "start_date" in update_data and not validate_start_date(update_data["start_date"]):
                logger.warning("Invalid start date")
                return False, {"start_date": "Start date must be at least 1 week after creation date"}
            
            for field, value in update_data.items():
                setattr(item, field, value)
            
            item.updated_at = datetime.utcnow()
            item.save()
            
            emit_event("item_updated", {"item_id": str(item.id)})
            
            logger.info(f"Item updated: {item_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error updating item: {str(e)}")
            return False, {"server": f"Internal error: {str(e)}"}
    
    @staticmethod
    def delete_item(item_id: str) -> Tuple[bool, Optional[str]]:
        """Delete an item.
        
        Args:
            item_id: The ID of the item to delete
            
        Returns:
            tuple: (success, error)
                - success: True if deletion was successful, False otherwise
                - error: Error message if deletion failed, None otherwise
        """
        logger.info(f"Deleting item with ID: {item_id}")
        
        try:
            if not ObjectId.is_valid(item_id):
                logger.warning(f"Invalid item ID format: {item_id}")
                return False, "Invalid item ID format"
            
            # Get item to check if it exists
            item = Item.objects(id=item_id).first()
            if not item:
                logger.warning(f"Item not found with ID: {item_id}")
                return False, "Item not found"
            
            item.delete()
            
            emit_event("item_deleted", {"item_id": item_id})
            
            logger.info(f"Item deleted: {item_id}")
            return True, None
            
        except Exception as e:
            logger.error(f"Error deleting item: {str(e)}")
            return False, f"Internal error: {str(e)}"