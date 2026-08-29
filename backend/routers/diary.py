import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.diary import Diary, DiaryPhoto, DiaryLike, DiaryComment
from models.photo import Photo
from schemas.diary import (
    DiaryCreate, DiaryUpdate, DiaryOut, DiaryAuthorOut,
    DiaryPhotoOut, DiaryLikeOut, DiaryCommentOut, DiaryCommentCreate,
)
from auth import get_current_user
from services.storage import delete_file

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/diaries", tags=["情侣日记"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


def get_author_info(user_id: str, db: Session) -> DiaryAuthorOut:
    """获取用户基本信息。"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return DiaryAuthorOut(id=user_id, nickname="未知用户")
    return DiaryAuthorOut(id=user.id, nickname=user.nickname, avatar_url=user.avatar_url)


def build_diary_out(diary: Diary, current_user_id: str, db: Session) -> DiaryOut:
    """构建日记输出，包含作者、照片、点赞、评论。"""
    base_url = os.getenv("UPLOAD_BASE_URL", "")

    # 照片列表
    diary_photos = db.query(DiaryPhoto).filter(DiaryPhoto.diary_id == diary.id).all()
    photos = []
    for dp in diary_photos:
        photos.append(DiaryPhotoOut(
            id=dp.id,
            url=f"{base_url}/{dp.file_key}",
            thumbnail_url=f"{base_url}/{dp.thumbnail_key}" if dp.thumbnail_key else None,
        ))

    # 点赞
    likes = db.query(DiaryLike).filter(DiaryLike.diary_id == diary.id).all()
    like_count = len(likes)
    liked_by_me = any(l.user_id == current_user_id for l in likes)

    # 点赞者信息
    like_users = []
    for l in likes:
        user = db.query(User).filter(User.id == l.user_id).first()
        if user:
            like_users.append(DiaryAuthorOut(id=user.id, nickname=user.nickname, avatar_url=user.avatar_url))

    # 评论
    comment_records = db.query(DiaryComment).filter(DiaryComment.diary_id == diary.id).order_by(DiaryComment.created_at).all()
    comments = []
    for c in comment_records:
        comments.append(DiaryCommentOut(
            id=c.id,
            user_id=c.user_id,
            author=get_author_info(c.user_id, db),
            content=c.content,
            created_at=c.created_at,
        ))

    return DiaryOut(
        id=diary.id,
        created_by=diary.created_by,
        author=get_author_info(diary.created_by, db),
        title=diary.title,
        content=diary.content,
        photos=photos,
        like_count=like_count,
        liked_by_me=liked_by_me,
        comments=comments,
        created_at=diary.created_at,
        updated_at=diary.updated_at,
    )


@router.get("", response_model=list[DiaryOut])
def list_diaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取日记列表。"""
    couple = get_couple(current_user.id, db)
    diaries = db.query(Diary).filter(
        Diary.couple_id == couple.id
    ).order_by(Diary.created_at.desc()).all()
    return [build_diary_out(d, current_user.id, db) for d in diaries]


@router.post("", response_model=DiaryOut)
def create_diary(
    body: DiaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """写日记。"""
    couple = get_couple(current_user.id, db)
    diary = Diary(
        couple_id=couple.id,
        created_by=current_user.id,
        title=body.title,
        content=body.content,
    )
    db.add(diary)
    db.flush()

    # 关联照片
    if body.photo_ids:
        photos = db.query(Photo).filter(
            Photo.id.in_(body.photo_ids),
            Photo.couple_id == couple.id,
        ).all()
        for photo in photos:
            dp = DiaryPhoto(
                diary_id=diary.id,
                file_key=photo.file_key,
                thumbnail_key=photo.thumbnail_key,
            )
            db.add(dp)

    db.commit()
    db.refresh(diary)
    return build_diary_out(diary, current_user.id, db)


@router.put("/{diary_id}", response_model=DiaryOut)
def update_diary(
    diary_id: str,
    body: DiaryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """编辑日记。"""
    couple = get_couple(current_user.id, db)
    diary = db.query(Diary).filter(
        Diary.id == diary_id,
        Diary.couple_id == couple.id,
    ).first()
    if not diary:
        raise HTTPException(404, "日记不存在")

    if body.title is not None:
        diary.title = body.title
    if body.content is not None:
        diary.content = body.content

    # 更新照片关联
    if body.photo_ids is not None:
        # 删除旧的日记照片记录
        old_photos = db.query(DiaryPhoto).filter(DiaryPhoto.diary_id == diary.id).all()
        for op in old_photos:
            db.delete(op)
        # 添加新的
        if body.photo_ids:
            photos = db.query(Photo).filter(
                Photo.id.in_(body.photo_ids),
                Photo.couple_id == couple.id,
            ).all()
            for photo in photos:
                dp = DiaryPhoto(
                    diary_id=diary.id,
                    file_key=photo.file_key,
                    thumbnail_key=photo.thumbnail_key,
                )
                db.add(dp)

    db.commit()
    db.refresh(diary)
    return build_diary_out(diary, current_user.id, db)


@router.delete("/{diary_id}")
def delete_diary(
    diary_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除日记。"""
    couple = get_couple(current_user.id, db)
    diary = db.query(Diary).filter(
        Diary.id == diary_id,
        Diary.couple_id == couple.id,
    ).first()
    if not diary:
        raise HTTPException(404, "日记不存在")

    # 删除日记照片（diary_photos 记录 + 对应的 photos 记录 + 文件）
    diary_photos = db.query(DiaryPhoto).filter(DiaryPhoto.diary_id == diary.id).all()
    for dp in diary_photos:
        # 删除 photos 表中的原始记录（通过 file_key 匹配）
        original_photo = db.query(Photo).filter(Photo.file_key == dp.file_key).first()
        if original_photo:
            db.delete(original_photo)
        # 删除文件
        try:
            delete_file(dp.file_key)
            if dp.thumbnail_key:
                delete_file(dp.thumbnail_key)
        except Exception as e:
            logger.warning(f"Failed to delete diary photo file: {e}")
        db.delete(dp)

    # 删除点赞和评论
    db.query(DiaryLike).filter(DiaryLike.diary_id == diary.id).delete()
    db.query(DiaryComment).filter(DiaryComment.diary_id == diary.id).delete()

    db.delete(diary)
    db.commit()
    return {"message": "已删除"}


@router.post("/{diary_id}/like", response_model=DiaryLikeOut)
def toggle_like(
    diary_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """点赞/取消点赞。"""
    couple = get_couple(current_user.id, db)
    diary = db.query(Diary).filter(
        Diary.id == diary_id,
        Diary.couple_id == couple.id,
    ).first()
    if not diary:
        raise HTTPException(404, "日记不存在")

    existing = db.query(DiaryLike).filter(
        DiaryLike.diary_id == diary_id,
        DiaryLike.user_id == current_user.id,
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        liked = False
    else:
        like = DiaryLike(diary_id=diary_id, user_id=current_user.id)
        db.add(like)
        db.commit()
        liked = True

    like_count = db.query(DiaryLike).filter(DiaryLike.diary_id == diary_id).count()
    return DiaryLikeOut(liked=liked, like_count=like_count)


@router.post("/{diary_id}/comments", response_model=DiaryCommentOut)
def add_comment(
    diary_id: str,
    body: DiaryCommentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加评论。"""
    couple = get_couple(current_user.id, db)
    diary = db.query(Diary).filter(
        Diary.id == diary_id,
        Diary.couple_id == couple.id,
    ).first()
    if not diary:
        raise HTTPException(404, "日记不存在")

    comment = DiaryComment(
        diary_id=diary_id,
        user_id=current_user.id,
        content=body.content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return DiaryCommentOut(
        id=comment.id,
        user_id=comment.user_id,
        author=get_author_info(comment.user_id, db),
        content=comment.content,
        created_at=comment.created_at,
    )


@router.delete("/{diary_id}/comments/{comment_id}")
def delete_comment(
    diary_id: str,
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除自己的评论。"""
    comment = db.query(DiaryComment).filter(
        DiaryComment.id == comment_id,
        DiaryComment.diary_id == diary_id,
        DiaryComment.user_id == current_user.id,
    ).first()
    if not comment:
        raise HTTPException(404, "评论不存在")

    db.delete(comment)
    db.commit()
    return {"message": "已删除"}
