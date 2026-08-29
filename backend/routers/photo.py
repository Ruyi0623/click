from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models.user import User
from models.couple import Couple
from models.photo import Photo
from schemas.photo import PhotoOut
from services.storage import save_upload_file, delete_file
from auth import get_current_user


class MovePhotoRequest(BaseModel):
    collection_id: Optional[str] = None

router = APIRouter(prefix="/photos", tags=["相册"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[PhotoOut])
def list_photos(
    collection_id: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取共享相册列表（按时间倒序）。可选按合集过滤。"""
    from models.collection import Collection

    couple = get_couple(current_user.id, db)
    query = db.query(Photo).filter(Photo.couple_id == couple.id)
    if collection_id is not None:
        if collection_id == "ungrouped":
            query = query.filter(Photo.collection_id.is_(None))
        else:
            query = query.filter(Photo.collection_id == collection_id)
            # 排除封面照片
            collection = db.query(Collection).filter(Collection.id == collection_id).first()
            if collection and collection.cover_photo_id:
                query = query.filter(Photo.id != collection.cover_photo_id)
    photos = query.order_by(Photo.created_at.desc()).all()

    from services.storage import UPLOAD_BASE_URL
    return [
        PhotoOut(
            id=p.id,
            uploader_id=p.uploader_id,
            url=f"{UPLOAD_BASE_URL}/{p.file_key}",
            thumbnail_url=f"{UPLOAD_BASE_URL}/{p.thumbnail_key}" if p.thumbnail_key else None,
            caption=p.caption,
            width=p.width,
            height=p.height,
            taken_at=p.taken_at,
            created_at=p.created_at,
        )
        for p in photos
    ]


@router.post("", response_model=PhotoOut)
async def upload_photo(
    file: UploadFile = File(...),
    caption: Optional[str] = Form(None),
    collection_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传照片到共享相册。可选指定合集。"""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(400, "只支持图片文件")

    couple = get_couple(current_user.id, db)
    try:
        info = await save_upload_file(file, couple.id)
    except ValueError as e:
        raise HTTPException(400, str(e))

    photo = Photo(
        couple_id=couple.id,
        uploader_id=current_user.id,
        file_key=info["file_key"],
        thumbnail_key=info.get("thumbnail_key"),
        caption=caption,
        width=info.get("width"),
        height=info.get("height"),
        collection_id=collection_id,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)

    from services.storage import UPLOAD_BASE_URL
    return PhotoOut(
        id=photo.id,
        uploader_id=photo.uploader_id,
        url=f"{UPLOAD_BASE_URL}/{photo.file_key}",
        thumbnail_url=f"{UPLOAD_BASE_URL}/{photo.thumbnail_key}" if photo.thumbnail_key else None,
        caption=photo.caption,
        width=photo.width,
        height=photo.height,
        taken_at=photo.taken_at,
        created_at=photo.created_at,
    )


@router.delete("/{photo_id}")
def delete_photo(
    photo_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除照片（仅上传者可删除）。"""
    couple = get_couple(current_user.id, db)
    photo = db.query(Photo).filter(
        Photo.id == photo_id,
        Photo.couple_id == couple.id,
    ).first()
    if not photo:
        raise HTTPException(404, "照片不存在")
    if photo.uploader_id != current_user.id:
        raise HTTPException(403, "只能删除自己上传的照片")

    delete_file(photo.file_key)
    if photo.thumbnail_key:
        delete_file(photo.thumbnail_key)

    db.delete(photo)
    db.commit()
    return {"message": "已删除"}


@router.put("/{photo_id}/move")
def move_photo(
    photo_id: str,
    body: MovePhotoRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """移动照片到合集（或移出合集）。"""
    couple = get_couple(current_user.id, db)
    photo = db.query(Photo).filter(
        Photo.id == photo_id,
        Photo.couple_id == couple.id,
    ).first()
    if not photo:
        raise HTTPException(404, "照片不存在")

    photo.collection_id = body.collection_id
    db.commit()
    return {"message": "已移动"}
