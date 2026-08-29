import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Integer
from database import Base


class Magazine(Base):
    __tablename__ = "magazines"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    year = Column(String(4), nullable=False)
    month = Column(String(2), nullable=False)
    content = Column(Text, nullable=False)
    generate_count = Column(Integer, default=1, nullable=False, server_default="1")
    status = Column(String(20), default="success", nullable=False, server_default="success")  # success / failed
    created_at = Column(DateTime, default=datetime.utcnow)
