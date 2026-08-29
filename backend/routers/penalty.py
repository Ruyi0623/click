from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.penalty import Penalty
from schemas.penalty import PenaltyCreate, PenaltyOut
from auth import get_current_user

router = APIRouter(prefix="/penalties", tags=["恋爱罚单"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[PenaltyOut])
def list_penalties(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取罚单列表。"""
    couple = get_couple(current_user.id, db)
    penalties = db.query(Penalty).filter(
        Penalty.couple_id == couple.id
    ).order_by(Penalty.created_at.desc()).all()

    return [PenaltyOut.model_validate(p) for p in penalties]


@router.post("", response_model=PenaltyOut)
def create_penalty(
    body: PenaltyCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """开具恋爱罚单。"""
    couple = get_couple(current_user.id, db)

    # 验证 offender 是伴侣
    if body.offender_id not in [couple.user1_id, couple.user2_id]:
        raise HTTPException(400, "只能对伴侣开罚单")

    if body.penalty_type == "money" and not body.amount:
        raise HTTPException(400, "罚款类型需要指定金额")
    if body.penalty_type == "action" and not body.action:
        raise HTTPException(400, "行动类型需要指定行动内容")

    penalty = Penalty(
        couple_id=couple.id,
        issuer_id=current_user.id,
        offender_id=body.offender_id,
        reason=body.reason,
        penalty_type=body.penalty_type,
        amount=body.amount,
        action=body.action,
        photo_url=body.photo_url,
        note=body.note,
    )
    db.add(penalty)
    db.commit()
    db.refresh(penalty)

    return PenaltyOut.model_validate(penalty)


@router.post("/{penalty_id}/done", response_model=PenaltyOut)
def mark_penalty_done(
    penalty_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """标记罚单已完成。"""
    couple = get_couple(current_user.id, db)
    penalty = db.query(Penalty).filter(
        Penalty.id == penalty_id,
        Penalty.couple_id == couple.id,
        Penalty.offender_id == current_user.id,
    ).first()
    if not penalty:
        raise HTTPException(404, "罚单不存在")

    penalty.is_done = True
    penalty.done_at = datetime.utcnow()
    db.commit()
    db.refresh(penalty)

    return PenaltyOut.model_validate(penalty)


@router.delete("/{penalty_id}")
def delete_penalty(
    penalty_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除罚单。"""
    from services.storage import delete_file, UPLOAD_BASE_URL

    couple = get_couple(current_user.id, db)
    penalty = db.query(Penalty).filter(
        Penalty.id == penalty_id,
        Penalty.couple_id == couple.id,
    ).first()
    if not penalty:
        raise HTTPException(404, "罚单不存在")

    # 删除证据照片（物理文件 + Photo 记录）
    if penalty.photo_url:
        from models.photo import Photo
        file_key = penalty.photo_url.replace(UPLOAD_BASE_URL + "/", "")
        if file_key != penalty.photo_url:
            delete_file(file_key)
        photo = db.query(Photo).filter(
            (Photo.file_key == file_key) | (Photo.thumbnail_key == file_key)
        ).first()
        if photo:
            if photo.thumbnail_key:
                delete_file(photo.thumbnail_key)
            db.delete(photo)

    db.delete(penalty)
    db.commit()
    return {"message": "已删除"}
