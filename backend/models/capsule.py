import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Boolean, ForeignKey
from database import Base


class Capsule(Base):
    __tablename__ = "capsules"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    open_at = Column(DateTime, nullable=False)
    is_opened = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
