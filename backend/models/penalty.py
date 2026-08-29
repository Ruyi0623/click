import uuid
from datetime import datetime
from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Boolean
from database import Base


class Penalty(Base):
    """恋爱罚单"""
    __tablename__ = "penalties"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    issuer_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    offender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    reason = Column(String(200), nullable=False)
    penalty_type = Column(
        String(20),
        nullable=False,
        default="money"
    )
    amount = Column(Float, nullable=True)
    action = Column(String(200), nullable=True)
    photo_url = Column(String(500), nullable=True)
    note = Column(String(500), nullable=True)
    is_done = Column(Boolean, default=False)
    done_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
