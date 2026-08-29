import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    phone = Column(String(20), unique=True, nullable=True, index=True)
    wx_openid = Column(String(64), unique=True, nullable=True, index=True)
    username = Column(String(50), unique=True, nullable=True)
    password_hash = Column(String(128), nullable=True)
    email = Column(String(100), unique=True, nullable=True)
    nickname = Column(String(50), nullable=False)
    avatar_url = Column(String(500), nullable=True)
    birthday = Column(String(10), nullable=True)  # YYYY-MM-DD
    gender = Column(String(10), nullable=True)  # male/female/null
    created_at = Column(DateTime, default=datetime.utcnow)
