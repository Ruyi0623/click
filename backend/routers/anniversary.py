from datetime import date
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db
from models.user import User
from models.couple import Couple
from models.anniversary import Anniversary
from schemas.anniversary import AnniversaryCreate, AnniversaryUpdate, AnniversaryOut
from auth import get_current_user

router = APIRouter(prefix="/anniversaries", tags=["纪念日"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


def calc_days_until(ann: Anniversary) -> Optional[int]:
    today = date.today()
    if ann.repeat_type == "yearly":
        this_year = ann.date.replace(year=today.year)
        if this_year < today:
            this_year = ann.date.replace(year=today.year + 1)
        return (this_year - today).days
    else:
        diff = (ann.date - today).days
        return diff if diff >= 0 else None


@router.get("", response_model=list[AnniversaryOut])
def list_anniversaries(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取纪念日列表。"""
    couple = get_couple(current_user.id, db)
    items = db.query(Anniversary).filter(Anniversary.couple_id == couple.id).all()
    result = []
    for ann in items:
        out = AnniversaryOut(
            id=ann.id, title=ann.title, date=ann.date,
            repeat_type=ann.repeat_type, days_until=calc_days_until(ann),
        )
        result.append(out)
    return sorted(result, key=lambda x: x.days_until if x.days_until is not None else 9999)


@router.post("", response_model=AnniversaryOut)
def create_anniversary(
    body: AnniversaryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建纪念日。"""
    couple = get_couple(current_user.id, db)
    ann = Anniversary(
        couple_id=couple.id,
        title=body.title,
        date=body.date,
        repeat_type=body.repeat_type,
    )
    db.add(ann)
    db.commit()
    db.refresh(ann)
    return AnniversaryOut(
        id=ann.id, title=ann.title, date=ann.date,
        repeat_type=ann.repeat_type, days_until=calc_days_until(ann),
    )


@router.put("/{anniversary_id}", response_model=AnniversaryOut)
def update_anniversary(
    anniversary_id: str,
    body: AnniversaryUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新纪念日。"""
    couple = get_couple(current_user.id, db)
    ann = db.query(Anniversary).filter(
        Anniversary.id == anniversary_id,
        Anniversary.couple_id == couple.id,
    ).first()
    if not ann:
        raise HTTPException(404, "纪念日不存在")

    if body.title is not None:
        ann.title = body.title
    if body.date is not None:
        ann.date = body.date
    if body.repeat_type is not None:
        ann.repeat_type = body.repeat_type

    db.commit()
    db.refresh(ann)
    return AnniversaryOut(
        id=ann.id, title=ann.title, date=ann.date,
        repeat_type=ann.repeat_type, days_until=calc_days_until(ann),
    )


@router.delete("/{anniversary_id}")
def delete_anniversary(
    anniversary_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除纪念日。"""
    couple = get_couple(current_user.id, db)
    ann = db.query(Anniversary).filter(
        Anniversary.id == anniversary_id,
        Anniversary.couple_id == couple.id,
    ).first()
    if not ann:
        raise HTTPException(404, "纪念日不存在")

    db.delete(ann)
    db.commit()
    return {"message": "已删除"}
