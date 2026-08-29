from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class TransactionCreate(BaseModel):
    amount: float = Field(..., gt=0)
    category: str
    description: Optional[str] = None
    split_type: str = "equal"
    custom_amount: Optional[float] = Field(None, ge=0)
    photo_url: Optional[str] = None
    mood: Optional[str] = None
    happened_at: Optional[datetime] = None


class TransactionUpdate(BaseModel):
    amount: Optional[float] = Field(None, gt=0)
    category: Optional[str] = None
    description: Optional[str] = None
    split_type: Optional[str] = None
    custom_amount: Optional[float] = Field(None, ge=0)
    happened_at: Optional[datetime] = None


class TransactionOut(BaseModel):
    id: str
    paid_by: str
    amount: float
    category: str
    description: Optional[str]
    split_type: str
    custom_amount: Optional[float]
    photo_url: Optional[str]
    mood: Optional[str]
    happened_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class BalanceInfo(BaseModel):
    user1_id: str
    user1_nickname: str
    user1_paid: float
    user2_id: str
    user2_nickname: str
    user2_paid: float
    balance: float
    who_owes: str


class CategoryStat(BaseModel):
    category: str
    amount: float
    percentage: float


class UserSpending(BaseModel):
    user_id: str
    nickname: str
    amount: float


class MonthlyStats(BaseModel):
    month: str
    total: float
    budget: Optional[float] = None
    budget_remaining: Optional[float] = None
    categories: list[CategoryStat]
    users: list[UserSpending] = []
