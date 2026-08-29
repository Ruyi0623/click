from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional


class WishCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=200)


class WishUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=200)
    is_done: Optional[bool] = None


class WishOut(BaseModel):
    id: str
    created_by: str
    creator_nickname: str = ""
    content: str
    is_done: bool
    done_at: Optional[datetime]
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
