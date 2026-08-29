import secrets
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from database import get_db, get_redis
from models.user import User
from models.couple import Couple
from models.anniversary import Anniversary
from models.photo import Photo
from models.wish import Wish
from models.mood import Mood
from models.message import Message
from models.capsule import Capsule
from models.footprint import Footprint
from models.magazine import Magazine
from models.fund import Fund, FundContribution
from models.transaction import Transaction
from models.penalty import Penalty
from models.collection import Collection
from models.diary import Diary, DiaryPhoto, DiaryLike, DiaryComment
from models.couple import MonthlyBudget
from schemas.couple import GenerateCodeResponse, ConfirmPairRequest, CoupleInfo, BudgetUpdate
from auth import get_current_user

router = APIRouter(prefix="/couple", tags=["配对"])


def get_couple_by_user(user_id: str, db: Session) -> Optional[Couple]:
    return db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()


@router.post("/generate", response_model=GenerateCodeResponse)
def generate_code(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
):
    """生成配对码。"""
    if get_couple_by_user(current_user.id, db):
        raise HTTPException(400, "你已有伴侣，请先解除配对")

    old_code = redis.get(f"pair:user:{current_user.id}")
    if old_code:
        redis.delete(f"pair:{old_code}")

    code = str(secrets.randbelow(900000) + 100000)  # 6位数字，密码学安全
    redis.setex(f"pair:{code}", 300, current_user.id)
    redis.setex(f"pair:user:{current_user.id}", 300, code)

    return GenerateCodeResponse(code=code, expires_in=300)


@router.post("/confirm")
def confirm_pair(
    body: ConfirmPairRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    redis=Depends(get_redis),
):
    """输入配对码确认配对。"""
    partner_id = redis.getdel(f"pair:{body.code}")
    if not partner_id:
        raise HTTPException(400, "配对码无效或已过期")
    if partner_id == current_user.id:
        raise HTTPException(400, "不能和自己配对")

    if get_couple_by_user(partner_id, db) or get_couple_by_user(current_user.id, db):
        raise HTTPException(400, "其中一方已有伴侣，配对失败")

    start = body.start_date or date.today()
    couple = Couple(
        user1_id=partner_id,
        user2_id=current_user.id,
        start_date=start,
    )
    db.add(couple)
    db.commit()

    redis.delete(f"pair:user:{partner_id}")

    return {"message": "配对成功", "couple_id": couple.id}


@router.get("/info", response_model=CoupleInfo)
def get_couple_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取配对信息。"""
    couple = get_couple_by_user(current_user.id, db)
    if not couple:
        raise HTTPException(404, "尚未配对")

    partner_id = couple.user2_id if couple.user1_id == current_user.id else couple.user1_id
    partner = db.query(User).filter(User.id == partner_id).first()

    days = (date.today() - couple.start_date).days

    return CoupleInfo(
        id=couple.id,
        partner_id=partner_id,
        partner_nickname=partner.nickname,
        partner_username=partner.username,
        partner_avatar=partner.avatar_url,
        partner_birthday=partner.birthday,
        partner_gender=partner.gender,
        start_date=couple.start_date,
        days_together=days,
        monthly_budget=couple.monthly_budget,
    )


@router.put("/budget", response_model=CoupleInfo)
def update_budget(
    body: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """设置月度预算。传 month 格式如 "2026-06"，不传则设置全局默认。"""
    from models.couple import MonthlyBudget

    couple = get_couple_by_user(current_user.id, db)
    if not couple:
        raise HTTPException(404, "尚未配对")

    if body.month:
        # 按月设置预算
        existing = db.query(MonthlyBudget).filter(
            MonthlyBudget.couple_id == couple.id,
            MonthlyBudget.month == body.month,
        ).first()
        if existing:
            existing.amount = body.monthly_budget
        else:
            db.add(MonthlyBudget(
                couple_id=couple.id,
                month=body.month,
                amount=body.monthly_budget,
            ))
    else:
        # 设置全局默认
        couple.monthly_budget = body.monthly_budget

    db.commit()
    db.refresh(couple)

    partner_id = couple.user2_id if couple.user1_id == current_user.id else couple.user1_id
    partner = db.query(User).filter(User.id == partner_id).first()
    days = (date.today() - couple.start_date).days

    return CoupleInfo(
        id=couple.id,
        partner_id=partner_id,
        partner_nickname=partner.nickname,
        partner_username=partner.username,
        partner_avatar=partner.avatar_url,
        partner_birthday=partner.birthday,
        partner_gender=partner.gender,
        start_date=couple.start_date,
        days_together=days,
        monthly_budget=couple.monthly_budget,
    )


@router.post("/unbind")
def unbind(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """解除配对。删除所有共享数据（含文件）后删除配对关系。"""
    import logging
    from services.storage import delete_file

    logger = logging.getLogger(__name__)
    couple = get_couple_by_user(current_user.id, db)
    if not couple:
        raise HTTPException(404, "尚未配对")

    cid = couple.id

    # 1. 删除照片文件（原图 + 缩略图）
    photos = db.query(Photo).filter(Photo.couple_id == cid).all()
    for p in photos:
        try:
            delete_file(p.file_key)
            if p.thumbnail_key:
                delete_file(p.thumbnail_key)
        except Exception as e:
            logger.warning(f"Failed to delete photo file: {e}")

    # 2. 删除日记照片文件
    diary_photos = db.query(DiaryPhoto).filter(
        DiaryPhoto.diary_id.in_(db.query(Diary.id).filter(Diary.couple_id == cid))
    ).all()
    for dp in diary_photos:
        try:
            delete_file(dp.file_key)
            if dp.thumbnail_key:
                delete_file(dp.thumbnail_key)
        except Exception as e:
            logger.warning(f"Failed to delete diary photo file: {e}")

    # 3. 删除头像文件
    from models.user import User as UserModel
    user1 = db.query(UserModel).filter(UserModel.id == couple.user1_id).first()
    user2 = db.query(UserModel).filter(UserModel.id == couple.user2_id).first()
    for u in [user1, user2]:
        if u and u.avatar_url and "/uploads/" in u.avatar_url:
            try:
                key = u.avatar_url.split("/uploads/")[-1]
                delete_file(key)
            except Exception as e:
                logger.warning(f"Failed to delete avatar file: {e}")

    # 4. 按依赖顺序删除所有关联数据
    # 日记子表（无 couple_id，通过 diary_id 子查询）
    diary_ids = db.query(Diary.id).filter(Diary.couple_id == cid).subquery()
    db.query(DiaryLike).filter(DiaryLike.diary_id.in_(diary_ids)).delete(synchronize_session=False)
    db.query(DiaryComment).filter(DiaryComment.diary_id.in_(diary_ids)).delete(synchronize_session=False)
    db.query(DiaryPhoto).filter(DiaryPhoto.diary_id.in_(diary_ids)).delete(synchronize_session=False)

    # 基金子表（无 couple_id，通过 fund_id 子查询）
    fund_ids = db.query(Fund.id).filter(Fund.couple_id == cid).subquery()
    db.query(FundContribution).filter(FundContribution.fund_id.in_(fund_ids)).delete(synchronize_session=False)

    # 有 couple_id 的表直接删
    for model in [Diary, Collection, MonthlyBudget,
                  Anniversary, Photo, Wish, Mood, Message, Capsule,
                  Footprint, Magazine, Fund, Transaction, Penalty]:
        db.query(model).filter(model.couple_id == cid).delete()

    # 5. 删除配对关系
    db.delete(couple)
    db.commit()
    return {"message": "已解除配对"}
