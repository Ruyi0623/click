from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from database import get_db
from models.user import User
from models.couple import Couple
from models.transaction import Transaction
from schemas.transaction import TransactionCreate, TransactionUpdate, TransactionOut, BalanceInfo, MonthlyStats, CategoryStat, UserSpending
from auth import get_current_user

router = APIRouter(prefix="/transactions", tags=["账单"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[TransactionOut])
def list_transactions(
    limit: int = 50,
    category: Optional[str] = None,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取账单列表，支持按分类和时间范围筛选。"""
    couple = get_couple(current_user.id, db)
    query = db.query(Transaction).filter(Transaction.couple_id == couple.id)

    if category:
        query = query.filter(Transaction.category == category)
    # 用 happened_at 筛选，没有 happened_at 的兜底到 created_at
    date_field = func.coalesce(Transaction.happened_at, Transaction.created_at)
    if start_date:
        query = query.filter(date_field >= start_date)
    if end_date:
        query = query.filter(date_field <= end_date + " 23:59:59")

    transactions = query.order_by(date_field.desc()).limit(limit).all()
    return [TransactionOut.model_validate(t) for t in transactions]


@router.post("", response_model=TransactionOut)
def create_transaction(
    body: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建账单。"""
    couple = get_couple(current_user.id, db)

    transaction = Transaction(
        couple_id=couple.id,
        paid_by=current_user.id,
        amount=body.amount,
        category=body.category,
        description=body.description,
        split_type=body.split_type,
        custom_amount=body.custom_amount,
        photo_url=body.photo_url,
        mood=body.mood,
        happened_at=body.happened_at,
    )
    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    return TransactionOut.model_validate(transaction)


@router.get("/stats", response_model=MonthlyStats)
def get_monthly_stats(
    month: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取月度消费统计。month 格式：2026-06，默认当月。"""
    couple = get_couple(current_user.id, db)

    if month:
        year, mon = map(int, month.split("-"))
    else:
        now = datetime.now()
        year, mon = now.year, now.month

    start = datetime(year, mon, 1)
    if mon == 12:
        end = datetime(year + 1, 1, 1)
    else:
        end = datetime(year, mon + 1, 1)

    date_field = func.coalesce(Transaction.happened_at, Transaction.created_at)
    transactions = db.query(Transaction).filter(
        Transaction.couple_id == couple.id,
        date_field >= start,
        date_field < end,
    ).all()

    total = sum(t.amount for t in transactions)

    # 按分类统计
    cat_map: dict[str, float] = {}
    for t in transactions:
        cat_map[t.category] = cat_map.get(t.category, 0) + t.amount

    categories = []
    for cat, amt in sorted(cat_map.items(), key=lambda x: -x[1]):
        pct = (amt / total * 100) if total > 0 else 0
        categories.append(CategoryStat(category=cat, amount=round(amt, 2), percentage=round(pct, 1)))

    # 查找当月预算，没有则为 None（不回退到全局）
    from models.couple import MonthlyBudget
    month_str = f"{year}-{mon:02d}"
    month_budget = db.query(MonthlyBudget).filter(
        MonthlyBudget.couple_id == couple.id,
        MonthlyBudget.month == month_str,
    ).first()
    budget = month_budget.amount if month_budget else None
    remaining = round(budget - total, 2) if budget else None

    # 按用户统计（根据分摊方式计算实际承担金额）
    user1 = db.query(User).filter(User.id == couple.user1_id).first()
    user2 = db.query(User).filter(User.id == couple.user2_id).first()
    user1_total = 0.0
    user2_total = 0.0
    for t in transactions:
        if t.split_type == "equal":
            user1_total += t.amount / 2
            user2_total += t.amount / 2
        elif t.split_type == "payer_full":
            if t.paid_by == couple.user1_id:
                user1_total += t.amount
            else:
                user2_total += t.amount
        elif t.split_type == "other_full":
            if t.paid_by == couple.user1_id:
                user2_total += t.amount
            else:
                user1_total += t.amount
        elif t.split_type == "custom":
            # custom_amount 是对方承担的金额，付款人承担剩余部分
            other_amt = t.custom_amount or 0
            payer_amt = t.amount - other_amt
            if t.paid_by == couple.user1_id:
                user1_total += payer_amt
                user2_total += other_amt
            else:
                user2_total += payer_amt
                user1_total += other_amt
        else:
            user1_total += t.amount / 2
            user2_total += t.amount / 2
    users = [
        UserSpending(user_id=user1.id, nickname=user1.nickname, amount=round(user1_total, 2)),
        UserSpending(user_id=user2.id, nickname=user2.nickname, amount=round(user2_total, 2)),
    ]

    return MonthlyStats(
        month=f"{year}-{mon:02d}",
        total=round(total, 2),
        budget=budget,
        budget_remaining=remaining,
        categories=categories,
        users=users,
    )


@router.get("/balance", response_model=BalanceInfo)
def get_balance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取账务平衡信息。"""
    couple = get_couple(current_user.id, db)

    user1 = db.query(User).filter(User.id == couple.user1_id).first()
    user2 = db.query(User).filter(User.id == couple.user2_id).first()

    user1_paid = db.query(func.sum(Transaction.amount)).filter(
        Transaction.couple_id == couple.id,
        Transaction.paid_by == couple.user1_id,
    ).scalar() or 0

    user2_paid = db.query(func.sum(Transaction.amount)).filter(
        Transaction.couple_id == couple.id,
        Transaction.paid_by == couple.user2_id,
    ).scalar() or 0

    total = user1_paid + user2_paid
    half = total / 2 if total > 0 else 0
    balance = user1_paid - half

    if balance > 0:
        who_owes = f"{user2.nickname}欠{user1.nickname} {abs(balance):.2f} 元"
    elif balance < 0:
        who_owes = f"{user1.nickname}欠{user2.nickname} {abs(balance):.2f} 元"
    else:
        who_owes = "账务平衡"

    return BalanceInfo(
        user1_id=couple.user1_id,
        user1_nickname=user1.nickname,
        user1_paid=user1_paid,
        user2_id=couple.user2_id,
        user2_nickname=user2.nickname,
        user2_paid=user2_paid,
        balance=balance,
        who_owes=who_owes,
    )


@router.put("/{transaction_id}", response_model=TransactionOut)
def update_transaction(
    transaction_id: str,
    body: TransactionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """编辑账单。"""
    couple = get_couple(current_user.id, db)
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.couple_id == couple.id,
    ).first()
    if not transaction:
        raise HTTPException(404, "账单不存在")

    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)
    return TransactionOut.model_validate(transaction)


@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除账单。"""
    from services.storage import delete_file, UPLOAD_BASE_URL

    couple = get_couple(current_user.id, db)
    transaction = db.query(Transaction).filter(
        Transaction.id == transaction_id,
        Transaction.couple_id == couple.id,
    ).first()
    if not transaction:
        raise HTTPException(404, "账单不存在")

    # 删除关联照片（物理文件 + Photo 记录）
    if transaction.photo_url:
        from models.photo import Photo
        file_key = transaction.photo_url.replace(UPLOAD_BASE_URL + "/", "")
        if file_key != transaction.photo_url:
            delete_file(file_key)
        photo = db.query(Photo).filter(
            (Photo.file_key == file_key) | (Photo.thumbnail_key == file_key)
        ).first()
        if photo:
            if photo.thumbnail_key:
                delete_file(photo.thumbnail_key)
            db.delete(photo)

    db.delete(transaction)
    db.commit()
    return {"message": "已删除"}
