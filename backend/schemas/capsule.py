from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class CapsuleCreate(BaseModel):
    content: str
    open_at: datetime


class CapsuleOut(BaseModel):
    id: str
    created_by: str
    content: str
    open_at: datetime
    is_opened: bool
    created_at: datetime

    class Config:
        from_attributes = True
