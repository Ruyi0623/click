import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Enum, ForeignKey
from database import Base


class Message(Base):
    __tablename__ = "messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    sender_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    type = Column(Enum("text", "image", name="message_type_enum"), default="text")
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
