from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class PenaltyCreate(BaseModel):
    offender_id: str
    reason: str
    penalty_type: str = "money"
    amount: Optional[float] = Field(None, ge=0)
    action: Optional[str] = None
    photo_url: Optional[str] = None
    note: Optional[str] = None


class PenaltyOut(BaseModel):
    id: str
    issuer_id: str
    offender_id: str
    reason: str
    penalty_type: str
    amount: Optional[float]
    action: Optional[str]
    photo_url: Optional[str]
    note: Optional[str]
    is_done: bool
    done_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True
