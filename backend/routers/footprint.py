from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.footprint import Footprint
from schemas.footprint import FootprintCreate, FootprintUpdate, FootprintOut
from auth import get_current_user

router = APIRouter(prefix="/footprints", tags=["足迹地图"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[FootprintOut])
def list_footprints(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取足迹列表。"""
    couple = get_couple(current_user.id, db)
    footprints = db.query(Footprint).filter(
        Footprint.couple_id == couple.id
    ).order_by(Footprint.visited_at.desc()).all()

    return [FootprintOut.model_validate(f) for f in footprints]


@router.post("", response_model=FootprintOut)
def create_footprint(
    body: FootprintCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加足迹。"""
    couple = get_couple(current_user.id, db)

    footprint = Footprint(
        couple_id=couple.id,
        created_by=current_user.id,
        name=body.name,
        latitude=body.latitude,
        longitude=body.longitude,
        visited_at=body.visited_at,
        note=body.note,
    )
    db.add(footprint)
    db.commit()
    db.refresh(footprint)

    return FootprintOut.model_validate(footprint)


@router.get("/{footprint_id}", response_model=FootprintOut)
def get_footprint(
    footprint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取足迹详情。"""
    couple = get_couple(current_user.id, db)
    footprint = db.query(Footprint).filter(
        Footprint.id == footprint_id,
        Footprint.couple_id == couple.id,
    ).first()
    if not footprint:
        raise HTTPException(404, "足迹不存在")

    return FootprintOut.model_validate(footprint)


@router.put("/{footprint_id}", response_model=FootprintOut)
def update_footprint(
    footprint_id: str,
    body: FootprintUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新足迹。"""
    couple = get_couple(current_user.id, db)
    footprint = db.query(Footprint).filter(
        Footprint.id == footprint_id,
        Footprint.couple_id == couple.id,
    ).first()
    if not footprint:
        raise HTTPException(404, "足迹不存在")

    if body.name is not None:
        footprint.name = body.name
    if body.latitude is not None:
        footprint.latitude = body.latitude
    if body.longitude is not None:
        footprint.longitude = body.longitude
    if body.visited_at is not None:
        footprint.visited_at = body.visited_at
    if body.note is not None:
        footprint.note = body.note

    db.commit()
    db.refresh(footprint)

    return FootprintOut.model_validate(footprint)


@router.delete("/{footprint_id}")
def delete_footprint(
    footprint_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除足迹。"""
    couple = get_couple(current_user.id, db)
    footprint = db.query(Footprint).filter(
        Footprint.id == footprint_id,
        Footprint.couple_id == couple.id,
    ).first()
    if not footprint:
        raise HTTPException(404, "足迹不存在")

    db.delete(footprint)
    db.commit()
    return {"message": "已删除"}
