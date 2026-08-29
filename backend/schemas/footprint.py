from datetime import date, datetime
from typing import Optional
from pydantic import BaseModel


class FootprintCreate(BaseModel):
    name: str
    latitude: float
    longitude: float
    visited_at: date
    note: Optional[str] = None


class FootprintUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    visited_at: Optional[date] = None
    note: Optional[str] = None


class FootprintOut(BaseModel):
    id: str
    created_by: str
    name: str
    latitude: float
    longitude: float
    visited_at: date
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
