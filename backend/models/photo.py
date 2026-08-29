import uuid
from datetime import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from database import Base


class Photo(Base):
    __tablename__ = "photos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    uploader_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    file_key = Column(String(500), nullable=False)
    thumbnail_key = Column(String(500), nullable=True)
    caption = Column(String(200), nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    taken_at = Column(DateTime, nullable=True)
    collection_id = Column(String(36), ForeignKey("collections.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
