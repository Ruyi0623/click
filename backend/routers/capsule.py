from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.capsule import Capsule
from schemas.capsule import CapsuleCreate, CapsuleOut
from auth import get_current_user

router = APIRouter(prefix="/capsules", tags=["时光胶囊"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[CapsuleOut])
def list_capsules(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取时光胶囊列表。"""
    couple = get_couple(current_user.id, db)
    capsules = db.query(Capsule).filter(
        Capsule.couple_id == couple.id
    ).order_by(Capsule.open_at.desc()).all()

    result = []
    for c in capsules:
        # 如果已到期但未标记为已开启，自动更新
        if not c.is_opened and c.open_at <= datetime.now():
            c.is_opened = True
            db.commit()

        # 未到期的胶囊隐藏内容
        capsule_out = CapsuleOut(
            id=c.id,
            created_by=c.created_by,
            content=c.content if c.is_opened else "未到期，暂不可见",
            open_at=c.open_at,
            is_opened=c.is_opened,
            created_at=c.created_at,
        )
        result.append(capsule_out)

    return result


@router.post("", response_model=CapsuleOut)
def create_capsule(
    body: CapsuleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建时光胶囊。"""
    couple = get_couple(current_user.id, db)

    if body.open_at <= datetime.now():
        raise HTTPException(400, "开启时间必须在未来")

    capsule = Capsule(
        couple_id=couple.id,
        created_by=current_user.id,
        content=body.content,
        open_at=body.open_at,
    )
    db.add(capsule)
    db.commit()
    db.refresh(capsule)

    return CapsuleOut(
        id=capsule.id,
        created_by=capsule.created_by,
        content="未到期，暂不可见",
        open_at=capsule.open_at,
        is_opened=False,
        created_at=capsule.created_at,
    )


@router.get("/{capsule_id}", response_model=CapsuleOut)
def get_capsule(
    capsule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取时光胶囊详情。"""
    couple = get_couple(current_user.id, db)
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.couple_id == couple.id,
    ).first()
    if not capsule:
        raise HTTPException(404, "胶囊不存在")

    # 如果已到期但未标记为已开启，自动更新
    if not capsule.is_opened and capsule.open_at <= datetime.now():
        capsule.is_opened = True
        db.commit()

    return CapsuleOut(
        id=capsule.id,
        created_by=capsule.created_by,
        content=capsule.content if capsule.is_opened else "未到期，暂不可见",
        open_at=capsule.open_at,
        is_opened=capsule.is_opened,
        created_at=capsule.created_at,
    )


@router.post("/{capsule_id}/open", response_model=CapsuleOut)
def open_capsule(
    capsule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """手动开启时光胶囊（需到期后才能开启）。"""
    couple = get_couple(current_user.id, db)
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.couple_id == couple.id,
    ).first()
    if not capsule:
        raise HTTPException(404, "胶囊不存在")

    if capsule.is_opened:
        raise HTTPException(400, "胶囊已开启")

    if capsule.open_at > datetime.now():
        raise HTTPException(400, "胶囊尚未到期，无法开启")

    capsule.is_opened = True
    db.commit()
    db.refresh(capsule)

    return CapsuleOut(
        id=capsule.id,
        created_by=capsule.created_by,
        content=capsule.content,
        open_at=capsule.open_at,
        is_opened=True,
        created_at=capsule.created_at,
    )


@router.delete("/{capsule_id}")
def delete_capsule(
    capsule_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除时光胶囊。"""
    couple = get_couple(current_user.id, db)
    capsule = db.query(Capsule).filter(
        Capsule.id == capsule_id,
        Capsule.couple_id == couple.id,
    ).first()
    if not capsule:
        raise HTTPException(404, "胶囊不存在")

    db.delete(capsule)
    db.commit()
    return {"message": "已删除"}
