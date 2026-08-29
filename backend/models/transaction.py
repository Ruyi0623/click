import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Enum
from database import Base


class Transaction(Base):
    """账单/交易记录"""
    __tablename__ = "transactions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    paid_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    category = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    split_type = Column(
        Enum("equal", "payer_full", "other_full", "custom", "fund", name="split_type_enum"),
        default="equal"
    )
    custom_amount = Column(Float, nullable=True)  # 自定义分摊时对方承担的金额
    photo_url = Column(String(500), nullable=True)
    mood = Column(String(100), nullable=True)
    happened_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
