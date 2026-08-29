from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class FundCreate(BaseModel):
    name: str
    target_amount: float = Field(..., gt=0)
    icon: str = "tabler:target"


class FundOut(BaseModel):
    id: str
    name: str
    target_amount: float
    current_amount: float
    icon: str
    progress: float = 0
    created_at: datetime

    class Config:
        from_attributes = True


class FundContributionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    type: str = "deposit"
    note: Optional[str] = None


class FundContributionOut(BaseModel):
    id: str
    fund_id: str
    user_id: str
    amount: float
    type: Optional[str] = "deposit"
    note: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True
