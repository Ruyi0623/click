from datetime import date
from typing import Optional
from pydantic import BaseModel


class MoodCreate(BaseModel):
    emoji: str
    mood_date: date
    content: Optional[str] = None


class MoodOut(BaseModel):
    id: str
    user_id: str
    emoji: str
    content: Optional[str]
    mood_date: date

    class Config:
        from_attributes = True
