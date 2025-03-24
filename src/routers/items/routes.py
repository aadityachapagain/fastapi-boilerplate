import logging
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Path, Body, status
from fastapi.responses import JSONResponse

from src.auth.dependencies import authenticated
from src.db.connection import get_db
from src.routers.items.schemas import (
    ItemCreate, 
    ItemUpdate, 
    ItemResponse,
    ValidationError, 
    ErrorResponse
)
from src.routers.items.service import ItemService

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/items",
    tags=["items"],
    dependencies=[Depends(get_db), authenticated],
    responses={
        status.HTTP_401_UNAUTHORIZED: {"model": ErrorResponse},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"model": ErrorResponse}
    }
)


@router.post(
    "",
    response_model=Dict[str, str],
    responses={
        status.HTTP_201_CREATED: {"description": "Item created successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ValidationError},
    },
    status_code=status.HTTP_201_CREATED
)
async def create_item(item: ItemCreate):
    """Create a new item."""
    logger.info("Request to create new item")
    
    item_id, errors = await ItemService.create_item(item.model_dump())
    
    if errors:
        logger.warning(f"Item creation failed due to validation errors: {errors}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": errors}
        )
    
    return {"id": item_id}


@router.get(
    "",
    response_model=List[ItemResponse],
    responses={
        status.HTTP_200_OK: {"description": "List of items"}
    }
)
def get_items():
    """Get all items."""
    logger.info("Request to list all items")
    
    items = ItemService.get_all_items()
    
    return items


@router.get(
    "/{item_id}",
    response_model=ItemResponse,
    responses={
        status.HTTP_200_OK: {"description": "Item details"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    }
)
def get_item(item_id: str = Path(..., description="The ID of the item to retrieve")):
    """Get a specific item by ID."""
    logger.info(f"Request to get item with ID: {item_id}")
    
    item = ItemService.get_item_by_id(item_id)
    
    if not item:
        logger.warning(f"Item not found: {item_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item not found with ID: {item_id}"
        )
    
    return item


@router.patch(
    "/{item_id}",
    response_model=Dict[str, str],
    responses={
        status.HTTP_200_OK: {"description": "Item updated successfully"},
        status.HTTP_400_BAD_REQUEST: {"model": ValidationError},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    }
)
async def update_item(
    item: ItemUpdate,
    item_id: str = Path(..., description="The ID of the item to update")
):
    """Update an existing item."""
    logger.info(f"Request to update item with ID: {item_id}")
    update_data = {k: v for k, v in item.model_dump().items() if v is not None}
    
    if not update_data:
        logger.warning("No valid fields to update")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": {"_": "No valid fields to update"}}
        )
    
    # Update item using service
    success, errors = await ItemService.update_item(item_id, update_data)
    
    if not success:
        if "id" in errors and "not found" in errors["id"]:
            logger.warning(f"Item not found for update: {item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found with ID: {item_id}"
            )
        
        logger.warning(f"Item update failed due to validation errors: {errors}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": errors}
        )
    
    return {"message": "Item updated successfully"}


@router.delete(
    "/{item_id}",
    response_model=Dict[str, str],
    responses={
        status.HTTP_200_OK: {"description": "Item deleted successfully"},
        status.HTTP_404_NOT_FOUND: {"model": ErrorResponse},
    }
)
def delete_item(item_id: str = Path(..., description="The ID of the item to delete")):
    """Delete an item."""
    logger.info(f"Request to delete item with ID: {item_id}")
    
    success, error = ItemService.delete_item(item_id)
    
    if not success:
        if error and "not found" in error:
            logger.warning(f"Item not found for deletion: {item_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Item not found with ID: {item_id}"
            )
        
        logger.error(f"Item deletion failed: {error}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete item: {error}"
        )
    
    return {"message": "Item deleted successfully"}