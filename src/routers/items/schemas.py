from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from src.utils.validators import validate_postcode, validate_start_date


class ItemBase(BaseModel):
    """Base schema for Item operations."""
    class Config:
        """Pydantic configuration for handling ORM models."""
        arbitrary_types_allowed = True
        populate_by_name = True
        from_attributes = True


class ItemCreate(ItemBase):
    """Schema for creating a new item."""
    name: str = Field(..., max_length=50, description="Item name (required)")
    postcode: str = Field(..., description="US postcode (required)")
    title: Optional[str] = Field(None, max_length=100, description="Optional title")
    users: List[str] = Field(..., description="List of users (each name < 50 chars)")
    startDate: datetime = Field(..., description="Start date (at least 1 week from creation)")
    
    @field_validator('name')
    def name_must_be_valid(cls, v):
        """Validate name length."""
        if len(v) > 50:
            raise ValueError('Name must be less than 50 characters')
        return v
    
    @field_validator('postcode')
    def postcode_must_be_valid(cls, v):
        """Validate US postcode format."""
        if not validate_postcode(v):
            raise ValueError('Invalid US postcode format')
        return v
    
    @field_validator('users')
    def users_must_be_valid(cls, v):
        """Validate user names."""
        for user in v:
            if len(user) > 50:
                raise ValueError(f'User name "{user}" exceeds 50 characters')
        return v
    
    @field_validator('startDate')
    def start_date_must_be_valid(cls, v):
        """Validate start date is at least 1 week in future."""
        if not validate_start_date(v):
            raise ValueError('Start date must be at least 1 week after creation date')
        return v
    
    @model_validator(mode='after')
    def validate_name_in_users(self):
        """Validate name is in users list."""
        name = self.name
        users = self.users
        if name not in users:
            raise ValueError('Name must be included in the users list')
        return self


class ItemUpdate(ItemBase):
    """Schema for updating an existing item."""
    name: Optional[str] = Field(None, max_length=50, description="Item name")
    title: Optional[str] = Field(None, max_length=100, description="Optional title")
    users: Optional[List[str]] = Field(None, description="List of users (each name < 50 chars)")
    startDate: Optional[datetime] = Field(None, description="Start date (at least 1 week from creation)")
    
    @field_validator('name')
    def name_must_be_valid(cls, v):
        """Validate name length."""
        if v is not None and len(v) > 50:
            raise ValueError('Name must be less than 50 characters')
        return v
    
    @field_validator('users')
    def users_must_be_valid(cls, v):
        """Validate user names."""
        if v is not None:
            for user in v:
                if len(user) > 50:
                    raise ValueError(f'User name "{user}" exceeds 50 characters')
        return v
    
    @field_validator('startDate')
    def start_date_must_be_valid(cls, v):
        """Validate start date is at least 1 week in future."""
        if v is not None and not validate_start_date(v):
            raise ValueError('Start date must be at least 1 week after creation date')
        return v
    
    @model_validator(mode='after')
    def validate_name_in_users(self):
        """Validate name is in users list if both are present."""
        name = self.name
        users = self.users
        if name is not None and users is not None and name not in users:
            raise ValueError('Name must be included in the users list')
        return self


class ItemResponse(ItemBase):
    """Schema for item responses."""
    id: str
    name: str
    postcode: str
    latitude: float
    longitude: float
    directionFromNewYork: str
    title: Optional[str]
    users: List[str]
    startDate: datetime
    createdAt: datetime
    updatedAt: datetime


class ValidationError(BaseModel):
    """Schema for validation errors."""
    detail: dict


class ErrorResponse(BaseModel):
    """Schema for error responses."""
    detail: str