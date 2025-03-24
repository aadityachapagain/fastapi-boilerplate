import re
import logging
import datetime
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

# Regular expression for US postal codes
# Basic format: 5 digits or 5 digits + dash + 4 digits
US_POSTCODE_REGEX = r"^\d{5}(-\d{4})?$"


def validate_postcode(postcode: str) -> bool:
    """Validate if a string is a valid US postal code.
    
    Args:
        postcode: The postal code to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not postcode:
        return False
    
    return bool(re.match(US_POSTCODE_REGEX, postcode))


def validate_name_in_users(name: str, users: List[str]) -> bool:
    """Validate that the name field is included in the users list.
    
    Args:
        name: The name to check
        users: List of users
        
    Returns:
        bool: True if name is in users list, False otherwise
    """
    return name in users


def validate_start_date(start_date: datetime.datetime) -> bool:
    """Validate start date is at least 1 week after current date.
    
    Args:
        start_date: The start date to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    one_week_from_now = datetime.datetime.utcnow() + datetime.timedelta(weeks=1)
    return start_date >= one_week_from_now


def convert_keys_to_snake_case(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert camelCase keys to snake_case.
    
    Args:
        data: Dictionary with camelCase keys
        
    Returns:
        dict: Dictionary with snake_case keys
    """
    if not data:
        return {}
    
    result = {}
    for key, value in data.items():
        snake_key = ''.join(['_' + c.lower() if c.isupper() else c for c in key]).lstrip('_')
        
        if isinstance(value, dict):
            result[snake_key] = convert_keys_to_snake_case(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            result[snake_key] = [convert_keys_to_snake_case(item) for item in value]
        else:
            result[snake_key] = value
    
    return result


def convert_keys_to_camel_case(data: Dict[str, Any]) -> Dict[str, Any]:
    """Convert snake_case keys to camelCase.
    
    Args:
        data: Dictionary with snake_case keys
        
    Returns:
        dict: Dictionary with camelCase keys
    """
    if not data:
        return {}
    
    result = {}
    for key, value in data.items():
        components = key.split('_')
        camel_key = components[0] + ''.join(x.title() for x in components[1:])
        
        if isinstance(value, dict):
            result[camel_key] = convert_keys_to_camel_case(value)
        elif isinstance(value, list) and value and isinstance(value[0], dict):
            result[camel_key] = [convert_keys_to_camel_case(item) for item in value]
        else:
            result[camel_key] = value
    
    return result


def validate_item_data(data: Dict[str, Any]) -> Tuple[bool, Optional[Dict[str, str]]]:
    """Validate item data against requirements.
    
    Args:
        data: The item data to validate
        
    Returns:
        tuple: (is_valid, errors)
            - is_valid: True if data is valid, False otherwise
            - errors: Dictionary with field names as keys and error messages as values
    """
    errors = {}
    
    if "name" not in data:
        errors["name"] = "Name is required"
    elif len(data["name"]) > 50:
        errors["name"] = "Name must be less than 50 characters"
    
    if "postcode" not in data:
        errors["postcode"] = "Postcode is required"
    elif not validate_postcode(data["postcode"]):
        errors["postcode"] = "Invalid US postcode format"
    
    if "users" not in data:
        errors["users"] = "Users list is required"
    elif not isinstance(data["users"], list):
        errors["users"] = "Users must be a list"
    else:
        for i, user in enumerate(data["users"]):
            if len(user) > 50:
                errors[f"users[{i}]"] = f"User name '{user}' exceeds 50 characters"

    if "start_date" not in data:
        errors["start_date"] = "Start date is required"
    elif not validate_start_date(data["start_date"]):
        errors["start_date"] = "Start date must be at least 1 week after the item creation date"
    
    # Validate that name is in users list
    if "name" in data and "users" in data and isinstance(data["users"], list):
        if not validate_name_in_users(data["name"], data["users"]):
            errors["name"] = "Name must be included in the users list"
    
    # Title validation (optional field)
    if "title" in data and data["title"] is not None and len(data["title"]) > 100:
        errors["title"] = "Title must be less than 100 characters"
    
    return len(errors) == 0, errors