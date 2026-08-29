import uuid
from datetime import datetime
from sqlalchemy import Column, String, Date, DateTime, Numeric, Text, ForeignKey
from database import Base


class Footprint(Base):
    __tablename__ = "footprints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    name = Column(String(100), nullable=False)
    latitude = Column(Numeric(10, 7), nullable=False)
    longitude = Column(Numeric(10, 7), nullable=False)
    visited_at = Column(Date, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
