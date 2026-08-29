import uuid
from sqlalchemy import Column, String, Text, Date, ForeignKey, UniqueConstraint
from database import Base


class Mood(Base):
    __tablename__ = "moods"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    emoji = Column(String(10), nullable=False)
    content = Column(Text, nullable=True)
    mood_date = Column(Date, nullable=False)

    __table_args__ = (
        UniqueConstraint("user_id", "mood_date", name="uq_mood"),
    )
