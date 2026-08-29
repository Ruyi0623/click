from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class DiaryAuthorOut(BaseModel):
    id: str
    nickname: str
    avatar_url: Optional[str] = None


class DiaryPhotoOut(BaseModel):
    id: str
    url: str
    thumbnail_url: Optional[str] = None


class DiaryCommentOut(BaseModel):
    id: str
    user_id: str
    author: DiaryAuthorOut
    content: str
    created_at: datetime


class DiaryCreate(BaseModel):
    title: Optional[str] = None
    content: str
    photo_ids: list[str] = []


class DiaryUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    photo_ids: Optional[list[str]] = None


class DiaryOut(BaseModel):
    id: str
    created_by: str
    author: DiaryAuthorOut
    title: Optional[str]
    content: str
    photos: list[DiaryPhotoOut] = []
    like_count: int = 0
    liked_by_me: bool = False
    comments: list[DiaryCommentOut] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class DiaryLikeOut(BaseModel):
    liked: bool
    like_count: int


class DiaryCommentCreate(BaseModel):
    content: str
