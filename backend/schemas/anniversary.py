from pydantic import BaseModel, Field
from datetime import date as Date
from typing import Optional


class AnniversaryCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    date: Date
    repeat_type: str = Field("yearly", pattern="^(none|yearly)$")


class AnniversaryUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    date: Optional[Date] = None
    repeat_type: Optional[str] = Field(None, pattern="^(none|yearly)$")


class AnniversaryOut(BaseModel):
    id: str
    title: str
    date: Date
    repeat_type: str
    days_until: Optional[int] = None
