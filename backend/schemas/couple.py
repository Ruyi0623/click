from pydantic import BaseModel, Field
from datetime import date as Date
from typing import Optional


class GenerateCodeResponse(BaseModel):
    code: str
    expires_in: int = 300


class ConfirmPairRequest(BaseModel):
    code: str = Field(..., min_length=6, max_length=6)
    start_date: Optional[Date] = None


class CoupleInfo(BaseModel):
    id: str
    partner_id: str
    partner_nickname: str
    partner_username: Optional[str]
    partner_avatar: Optional[str]
    partner_birthday: Optional[Date]
    partner_gender: Optional[str]
    start_date: Date
    days_together: int
    monthly_budget: Optional[float] = None


class BudgetUpdate(BaseModel):
    monthly_budget: float = Field(..., gt=0)
    month: Optional[str] = None  # 格式 "2026-06"，不传则设置全局默认
