import uuid
from sqlalchemy import Column, String, Date, Enum, ForeignKey
from database import Base


class Anniversary(Base):
    __tablename__ = "anniversaries"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    couple_id = Column(String(36), ForeignKey("couples.id"), nullable=False)
    title = Column(String(100), nullable=False)
    date = Column(Date, nullable=False)
    repeat_type = Column(Enum("none", "yearly", name="repeat_type_enum"), default="yearly")
