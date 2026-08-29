import os
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.collection import Collection
from models.photo import Photo
from schemas.collection import CollectionCreate, CollectionUpdate, CollectionOut
from auth import get_current_user

router = APIRouter(prefix="/collections", tags=["合集"])


def get_couple_by_user(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


def build_collection_out(collection: Collection, db: Session) -> CollectionOut:
    """构建合集输出，包含封面 URL 和照片数量。"""
    cover_photo_url = None
    if collection.cover_photo_id:
        photo = db.query(Photo).filter(Photo.id == collection.cover_photo_id).first()
        if photo:
            base_url = os.getenv("UPLOAD_BASE_URL", "")
            cover_photo_url = f"{base_url}/{photo.thumbnail_key}" if photo.thumbnail_key else f"{base_url}/{photo.file_key}"

    photo_count_query = db.query(Photo).filter(Photo.collection_id == collection.id)
    if collection.cover_photo_id:
        photo_count_query = photo_count_query.filter(Photo.id != collection.cover_photo_id)
    photo_count = photo_count_query.count()

    return CollectionOut(
        id=collection.id,
        name=collection.name,
        cover_photo_url=cover_photo_url,
        photo_count=photo_count,
        created_at=collection.created_at,
    )


@router.get("", response_model=list[CollectionOut])
def list_collections(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取当前情侣的所有合集。"""
    couple = get_couple_by_user(current_user.id, db)
    collections = db.query(Collection).filter(
        Collection.couple_id == couple.id
    ).order_by(Collection.created_at.desc()).all()
    return [build_collection_out(c, db) for c in collections]


@router.post("", response_model=CollectionOut)
def create_collection(
    body: CollectionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建新合集。"""
    couple = get_couple_by_user(current_user.id, db)
    collection = Collection(
        couple_id=couple.id,
        name=body.name,
        cover_photo_id=body.cover_photo_id,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return build_collection_out(collection, db)


@router.put("/{collection_id}", response_model=CollectionOut)
def update_collection(
    collection_id: str,
    body: CollectionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新合集（名称、封面）。"""
    couple = get_couple_by_user(current_user.id, db)
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.couple_id == couple.id,
    ).first()
    if not collection:
        raise HTTPException(404, "合集不存在")

    if body.name is not None:
        collection.name = body.name
    if body.cover_photo_id is not None:
        # 清除旧封面照片的合集关联，使其回到未分组
        if collection.cover_photo_id and collection.cover_photo_id != body.cover_photo_id:
            old_cover = db.query(Photo).filter(Photo.id == collection.cover_photo_id).first()
            if old_cover:
                old_cover.collection_id = None
        collection.cover_photo_id = body.cover_photo_id
    db.commit()
    db.refresh(collection)
    return build_collection_out(collection, db)


@router.delete("/{collection_id}")
def delete_collection(
    collection_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除合集及其中的所有照片。"""
    import logging
    from services.storage import delete_file

    logger = logging.getLogger(__name__)

    couple = get_couple_by_user(current_user.id, db)
    collection = db.query(Collection).filter(
        Collection.id == collection_id,
        Collection.couple_id == couple.id,
    ).first()
    if not collection:
        raise HTTPException(404, "合集不存在")

    try:
        from sqlalchemy import text

        # 查询合集内所有照片
        photos = db.query(Photo).filter(Photo.collection_id == collection_id).all()

        # 查询封面照片（可能不属于这个合集）
        cover_photo = None
        if collection.cover_photo_id:
            cover_photo = db.query(Photo).filter(Photo.id == collection.cover_photo_id).first()
            # 如果封面照片不在合集照片列表中，单独加入
            if cover_photo and cover_photo not in photos:
                photos.append(cover_photo)

        logger.info(f"Deleting collection {collection_id}, found {len(photos)} photos")

        # 删除照片文件
        for photo in photos:
            try:
                delete_file(photo.file_key)
                if photo.thumbnail_key:
                    delete_file(photo.thumbnail_key)
            except Exception as e:
                logger.warning(f"Failed to delete file for photo {photo.id}: {e}")

        # 收集所有要删除的照片 ID
        photo_ids = [p.id for p in photos]

        # 1. 清除合集的封面引用（解除 collections → photos FK）
        db.execute(text("UPDATE collections SET cover_photo_id = NULL WHERE id = :cid"), {"cid": collection_id})
        # 2. 删除所有相关照片（包括封面照片）
        if photo_ids:
            db.execute(text("DELETE FROM photos WHERE id IN :ids"), {"ids": tuple(photo_ids)})
        # 3. 删除合集
        db.execute(text("DELETE FROM collections WHERE id = :cid"), {"cid": collection_id})
        db.commit()
    except Exception as e:
        logger.error(f"Delete collection failed: {e}", exc_info=True)
        db.rollback()
        raise HTTPException(500, f"删除失败: {e}")
    return {"message": "已删除"}
