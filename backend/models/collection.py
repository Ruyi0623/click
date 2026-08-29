import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey
from database import Base


class Collection(Base):
    __tablename__ = "collections"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    name = Column(String(50), nullable=False)
    cover_photo_id = Column(String(36), ForeignKey("photos.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
