from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.message import Message
from schemas.message import MessageCreate, MessageOut
from auth import get_current_user

router = APIRouter(prefix="/messages", tags=["聊天"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[MessageOut])
def list_messages(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取聊天消息列表。"""
    couple = get_couple(current_user.id, db)
    messages = db.query(Message).filter(
        Message.couple_id == couple.id
    ).order_by(Message.created_at.desc()).limit(limit).all()
    return [MessageOut.model_validate(m) for m in reversed(messages)]


@router.post("", response_model=MessageOut)
def create_message(
    body: MessageCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """发送消息。"""
    couple = get_couple(current_user.id, db)

    message = Message(
        couple_id=couple.id,
        sender_id=current_user.id,
        type=body.type,
        content=body.content,
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return MessageOut.model_validate(message)


@router.delete("/{message_id}")
def delete_message(
    message_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除消息（只能删除自己的）。"""
    couple = get_couple(current_user.id, db)
    message = db.query(Message).filter(
        Message.id == message_id,
        Message.couple_id == couple.id,
        Message.sender_id == current_user.id,
    ).first()
    if not message:
        raise HTTPException(404, "消息不存在")

    db.delete(message)
    db.commit()
    return {"message": "已删除"}
