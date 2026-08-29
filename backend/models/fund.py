import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey
from database import Base


class Fund(Base):
    """心愿基金"""
    __tablename__ = "funds"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    name = Column(String(100), nullable=False)
    target_amount = Column(Float, nullable=False)
    current_amount = Column(Float, default=0)
    icon = Column(String(50), default="tabler:target")
    created_at = Column(DateTime, default=datetime.utcnow)


class FundContribution(Base):
    """基金投入/取出记录"""
    __tablename__ = "fund_contributions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fund_id = Column(String(36), ForeignKey("funds.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String(10), default="deposit")  # deposit / withdraw
    note = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
