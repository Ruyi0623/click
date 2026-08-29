from datetime import datetime
from pydantic import BaseModel


class MagazineGenerate(BaseModel):
    year: str
    month: str


class MagazineOut(BaseModel):
    id: str
    year: str
    month: str
    content: str
    generate_count: int = 1
    status: str = "success"
    created_at: datetime

    class Config:
        from_attributes = True
