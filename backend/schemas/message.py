from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class MessageCreate(BaseModel):
    content: str
    type: str = "text"


class MessageOut(BaseModel):
    id: str
    sender_id: str
    type: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True
