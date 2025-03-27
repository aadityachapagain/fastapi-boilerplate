import datetime
from enum import Enum
from typing import List, Optional
from mongoengine import (
    Document, StringField, FloatField, ListField, 
    DateTimeField, EnumField
)


class Direction(str, Enum):
    """Enumeration of possible directions from New York."""
    NORTHEAST = "NE"
    NORTHWEST = "NW"
    SOUTHEAST = "SE"
    SOUTHWEST = "SW"


class Item(Document):
    """Item model as defined in requirements."""
    name = StringField(required=True, max_length=50)
    postcode = StringField(required=True)
    latitude = FloatField()
    longitude = FloatField()
    direction_from_new_york = StringField(choices=[d.value for d in Direction])
    title = StringField(max_length=100)
    users = ListField(StringField(max_length=50))
    start_date = DateTimeField(required=True)
    created_at = DateTimeField(default=datetime.datetime.utcnow)
    updated_at = DateTimeField(default=datetime.datetime.utcnow)
    
    meta = {
        'collection': 'items',
        'indexes': [
            'name',
            'postcode',
            'created_at'
        ]
    }
    
    def save(self, *args, **kwargs):
        """Override save method to update timestamps."""
        if not self.id:
            self.created_at = datetime.datetime.now(datetime.UTC)
        self.updated_at = datetime.datetime.now(datetime.UTC)
        return super(Item, self).save(*args, **kwargs)
    
    def to_dict(self):
        """Convert document to dictionary with snake_case keys."""
        return {
            "id": str(self.id),
            "name": self.name,
            "postcode": self.postcode,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "direction_from_new_york": self.direction_from_new_york,
            "title": self.title,
            "users": self.users,
            "start_date": self.start_date,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }