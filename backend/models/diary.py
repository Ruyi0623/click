import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, UniqueConstraint
from database import Base


class Diary(Base):
    """情侣日记"""
    __tablename__ = "diaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(100), nullable=True)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class DiaryPhoto(Base):
    """日记照片"""
    __tablename__ = "diary_photos"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    diary_id = Column(String(36), ForeignKey("diaries.id", ondelete="CASCADE"), nullable=False)
    file_key = Column(String(500), nullable=False)
    thumbnail_key = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class DiaryLike(Base):
    """日记点赞"""
    __tablename__ = "diary_likes"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    diary_id = Column(String(36), ForeignKey("diaries.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (UniqueConstraint('diary_id', 'user_id'),)


class DiaryComment(Base):
    """日记评论"""
    __tablename__ = "diary_comments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    diary_id = Column(String(36), ForeignKey("diaries.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    content = Column(String(500), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
