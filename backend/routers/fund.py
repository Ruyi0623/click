from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.fund import Fund, FundContribution
from schemas.fund import FundCreate, FundOut, FundContributionCreate, FundContributionOut
from auth import get_current_user

router = APIRouter(prefix="/funds", tags=["心愿基金"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[FundOut])
def list_funds(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取心愿基金列表。"""
    couple = get_couple(current_user.id, db)
    funds = db.query(Fund).filter(Fund.couple_id == couple.id).all()

    result = []
    for f in funds:
        progress = (f.current_amount / f.target_amount * 100) if f.target_amount > 0 else 0
        fund_out = FundOut(
            id=f.id,
            name=f.name,
            target_amount=f.target_amount,
            current_amount=f.current_amount,
            icon=f.icon,
            progress=round(progress, 1),
            created_at=f.created_at,
        )
        result.append(fund_out)
    return result


@router.post("", response_model=FundOut)
def create_fund(
    body: FundCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """创建心愿基金。"""
    couple = get_couple(current_user.id, db)

    fund = Fund(
        couple_id=couple.id,
        name=body.name,
        target_amount=body.target_amount,
        icon=body.icon,
    )
    db.add(fund)
    db.commit()
    db.refresh(fund)

    return FundOut(
        id=fund.id,
        name=fund.name,
        target_amount=fund.target_amount,
        current_amount=fund.current_amount,
        icon=fund.icon,
        progress=0,
        created_at=fund.created_at,
    )


@router.post("/{fund_id}/contribute", response_model=FundContributionOut)
def contribute_to_fund(
    fund_id: str,
    body: FundContributionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """向心愿基金投入或取出资金。"""
    couple = get_couple(current_user.id, db)
    fund = db.query(Fund).filter(
        Fund.id == fund_id,
        Fund.couple_id == couple.id,
    ).first()
    if not fund:
        raise HTTPException(404, "基金不存在")

    if body.type == "withdraw":
        if fund.current_amount < body.amount:
            raise HTTPException(400, "余额不足")
        fund.current_amount -= body.amount
    else:
        fund.current_amount += body.amount

    contribution = FundContribution(
        fund_id=fund.id,
        user_id=current_user.id,
        amount=body.amount,
        type=body.type,
        note=body.note,
    )
    db.add(contribution)
    db.commit()
    db.refresh(contribution)

    return FundContributionOut.model_validate(contribution)


@router.get("/{fund_id}/contributions", response_model=list[FundContributionOut])
def list_contributions(
    fund_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取基金投入记录。"""
    couple = get_couple(current_user.id, db)
    fund = db.query(Fund).filter(
        Fund.id == fund_id,
        Fund.couple_id == couple.id,
    ).first()
    if not fund:
        raise HTTPException(404, "基金不存在")

    contributions = db.query(FundContribution).filter(
        FundContribution.fund_id == fund_id
    ).order_by(FundContribution.created_at.desc()).all()

    return [FundContributionOut.model_validate(c) for c in contributions]


@router.delete("/{fund_id}/contributions/{contribution_id}")
def delete_contribution(
    fund_id: str,
    contribution_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """撤销基金贡献记录。"""
    couple = get_couple(current_user.id, db)
    fund = db.query(Fund).filter(
        Fund.id == fund_id,
        Fund.couple_id == couple.id,
    ).first()
    if not fund:
        raise HTTPException(404, "基金不存在")

    contribution = db.query(FundContribution).filter(
        FundContribution.id == contribution_id,
        FundContribution.fund_id == fund_id,
    ).first()
    if not contribution:
        raise HTTPException(404, "记录不存在")

    # 反向修正基金余额
    if contribution.type == "withdraw":
        fund.current_amount += contribution.amount
    else:
        fund.current_amount -= contribution.amount

    db.delete(contribution)
    db.commit()
    return {"message": "已撤销"}


@router.delete("/{fund_id}")
def delete_fund(
    fund_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除心愿基金。"""
    couple = get_couple(current_user.id, db)
    fund = db.query(Fund).filter(
        Fund.id == fund_id,
        Fund.couple_id == couple.id,
    ).first()
    if not fund:
        raise HTTPException(404, "基金不存在")

    # 先删贡献记录，再删基金（外键约束）
    db.query(FundContribution).filter(FundContribution.fund_id == fund_id).delete()
    db.delete(fund)
    db.commit()
    return {"message": "已删除"}
