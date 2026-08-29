from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CollectionCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    cover_photo_id: Optional[str] = None


class CollectionUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=50)
    cover_photo_id: Optional[str] = None


class CollectionOut(BaseModel):
    id: str
    name: str
    cover_photo_url: Optional[str] = None
    photo_count: int = 0
    created_at: datetime

    class Config:
        from_attributes = True
