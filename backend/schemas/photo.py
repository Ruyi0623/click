from pydantic import BaseModel
from datetime import datetime
from typing import Optional


class PhotoOut(BaseModel):
    id: str
    uploader_id: str
    url: str
    thumbnail_url: Optional[str]
    caption: Optional[str]
    width: Optional[int]
    height: Optional[int]
    taken_at: Optional[datetime]
    created_at: datetime
