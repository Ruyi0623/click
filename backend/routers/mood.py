from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.mood import Mood
from schemas.mood import MoodCreate, MoodOut
from auth import get_current_user

router = APIRouter(prefix="/moods", tags=["心情"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[MoodOut])
def list_moods(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取心情列表（自己和伴侣的）。"""
    couple = get_couple(current_user.id, db)
    moods = db.query(Mood).filter(Mood.couple_id == couple.id).all()
    return [MoodOut.model_validate(m) for m in moods]


@router.post("", response_model=MoodOut)
def create_mood(
    body: MoodCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """记录今天的心情。"""
    couple = get_couple(current_user.id, db)

    existing = db.query(Mood).filter(
        Mood.user_id == current_user.id,
        Mood.mood_date == body.mood_date,
    ).first()
    if existing:
        existing.emoji = body.emoji
        existing.content = body.content
        db.commit()
        db.refresh(existing)
        return MoodOut.model_validate(existing)

    mood = Mood(
        couple_id=couple.id,
        user_id=current_user.id,
        emoji=body.emoji,
        content=body.content,
        mood_date=body.mood_date,
    )
    db.add(mood)
    db.commit()
    db.refresh(mood)
    return MoodOut.model_validate(mood)


@router.delete("/{mood_id}")
def delete_mood(
    mood_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除心情记录。"""
    mood = db.query(Mood).filter(
        Mood.id == mood_id,
        Mood.user_id == current_user.id,
    ).first()
    if not mood:
        raise HTTPException(404, "心情记录不存在")

    db.delete(mood)
    db.commit()
    return {"message": "已删除"}
