import uuid
from datetime import datetime
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from database import Base


class Wish(Base):
    __tablename__ = "wishes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(String(200), nullable=False)
    is_done = Column(Boolean, default=False)
    done_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
