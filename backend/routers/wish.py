from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.wish import Wish
from schemas.wish import WishCreate, WishUpdate, WishOut
from auth import get_current_user

router = APIRouter(prefix="/wishes", tags=["愿望清单"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


def build_wish_out(wish: Wish, nicknames: dict[str, str]) -> WishOut:
    return WishOut(
        id=wish.id,
        created_by=wish.created_by,
        creator_nickname=nicknames.get(wish.created_by, ""),
        content=wish.content,
        is_done=wish.is_done,
        done_at=wish.done_at,
        created_at=wish.created_at,
    )


@router.get("", response_model=list[WishOut])
def list_wishes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取愿望清单。"""
    couple = get_couple(current_user.id, db)
    wishes = db.query(Wish).filter(
        Wish.couple_id == couple.id
    ).order_by(Wish.created_at.desc(), Wish.id.desc()).all()

    # 批量获取创建者昵称
    creator_ids = list({w.created_by for w in wishes})
    users = db.query(User).filter(User.id.in_(creator_ids)).all() if creator_ids else []
    nicknames = {u.id: (u.nickname or "") for u in users}

    return [build_wish_out(w, nicknames) for w in wishes]


@router.post("", response_model=WishOut)
def create_wish(
    body: WishCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """添加愿望。"""
    couple = get_couple(current_user.id, db)
    wish = Wish(
        couple_id=couple.id,
        created_by=current_user.id,
        content=body.content,
    )
    db.add(wish)
    db.commit()
    db.refresh(wish)
    nicknames = {current_user.id: current_user.nickname or ""}
    return build_wish_out(wish, nicknames)


@router.put("/{wish_id}", response_model=WishOut)
def update_wish(
    wish_id: str,
    body: WishUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新愿望（修改内容或标记完成）。"""
    couple = get_couple(current_user.id, db)
    wish = db.query(Wish).filter(
        Wish.id == wish_id,
        Wish.couple_id == couple.id,
    ).first()
    if not wish:
        raise HTTPException(404, "愿望不存在")

    if body.content is not None:
        wish.content = body.content
    if body.is_done is not None:
        wish.is_done = body.is_done
        wish.done_at = datetime.utcnow() if body.is_done else None

    db.commit()
    db.refresh(wish)
    creator = db.query(User).filter(User.id == wish.created_by).first()
    nicknames = {wish.created_by: (creator.nickname if creator else "") or ""}
    return build_wish_out(wish, nicknames)


@router.delete("/{wish_id}")
def delete_wish(
    wish_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除愿望。"""
    couple = get_couple(current_user.id, db)
    wish = db.query(Wish).filter(
        Wish.id == wish_id,
        Wish.couple_id == couple.id,
    ).first()
    if not wish:
        raise HTTPException(404, "愿望不存在")

    db.delete(wish)
    db.commit()
    return {"message": "已删除"}
