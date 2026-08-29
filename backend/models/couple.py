import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, Date, ForeignKey, UniqueConstraint
from database import Base


class Couple(Base):
    __tablename__ = "couples"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user1_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    user2_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    start_date = Column(Date, nullable=False)
    monthly_budget = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user1_id", "user2_id", name="uq_couple"),
    )


class MonthlyBudget(Base):
    """每月预算"""
    __tablename__ = "monthly_budgets"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id", ondelete="CASCADE"), nullable=False)
    month = Column(String(7), nullable=False)  # 格式: "2026-06"
    amount = Column(Float, nullable=False)

    __table_args__ = (
        UniqueConstraint("couple_id", "month", name="uq_couple_month"),
    )
