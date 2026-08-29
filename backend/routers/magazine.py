import logging
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models.user import User
from models.couple import Couple
from models.magazine import Magazine
from schemas.magazine import MagazineGenerate, MagazineOut
from services.magazine import generate_magazine_content
from auth import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/magazines", tags=["恋爱月刊"])


def get_couple(user_id: str, db: Session) -> Couple:
    couple = db.query(Couple).filter(
        (Couple.user1_id == user_id) | (Couple.user2_id == user_id)
    ).first()
    if not couple:
        raise HTTPException(400, "尚未配对")
    return couple


@router.get("", response_model=list[MagazineOut])
def list_magazines(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取月刊列表。"""
    couple = get_couple(current_user.id, db)
    magazines = db.query(Magazine).filter(
        Magazine.couple_id == couple.id
    ).order_by(Magazine.year.desc(), Magazine.month.desc()).all()
    return [MagazineOut.model_validate(m) for m in magazines]


@router.post("/generate", response_model=MagazineOut)
def generate_magazine(
    body: MagazineGenerate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """手动生成恋爱月刊（仅失败时可重试，最多3次）。"""
    couple = get_couple(current_user.id, db)

    # 查询该月所有记录
    existing_list = db.query(Magazine).filter(
        Magazine.couple_id == couple.id,
        Magazine.year == body.year,
        Magazine.month == body.month,
    ).all()

    # 已有成功记录 → 不能再生成
    success = next((m for m in existing_list if m.status == "success"), None)
    if success:
        raise HTTPException(400, "本月月刊已生成，不可重复生成")

    # 统计失败次数
    failed_count = sum(1 for m in existing_list if m.status == "failed")
    if failed_count >= 3:
        raise HTTPException(400, "已尝试 3 次均失败，本月无法再生成")

    # 清除旧的失败记录
    for m in existing_list:
        db.delete(m)
    db.commit()

    try:
        content = generate_magazine_content(db, couple, int(body.year), int(body.month))

        magazine = Magazine(
            couple_id=couple.id,
            year=body.year,
            month=body.month,
            content=content,
            generate_count=failed_count + 1,
            status="success",
        )
        db.add(magazine)
        db.commit()
        db.refresh(magazine)

        return MagazineOut.model_validate(magazine)
    except Exception as e:
        logger.exception("生成月刊失败")
        # 记录失败
        failed = Magazine(
            couple_id=couple.id,
            year=body.year,
            month=body.month,
            content="生成失败",
            generate_count=failed_count + 1,
            status="failed",
        )
        db.add(failed)
        db.commit()
        raise HTTPException(500, "生成月刊失败，请稍后重试")


@router.post("/auto-generate")
def auto_generate_magazines(
    retry: bool = False,
    db: Session = Depends(get_db),
):
    """自动为所有情侣生成上月月刊。retry=true 时重试失败的记录。"""
    from datetime import datetime, timedelta

    # 计算上个月的年月
    today = datetime.now()
    first_of_month = today.replace(day=1)
    last_month = first_of_month - timedelta(days=1)
    year, month = last_month.year, last_month.month
    year_str = str(year)
    month_str = str(month).zfill(2)

    couples = db.query(Couple).all()
    generated = 0
    skipped = 0
    retried = 0
    errors = 0

    for couple in couples:
        existing = db.query(Magazine).filter(
            Magazine.couple_id == couple.id,
            Magazine.year == year_str,
            Magazine.month == month_str,
        ).first()

        # 已成功生成 → 跳过
        if existing and existing.status == "success":
            skipped += 1
            continue

        # 之前失败且不是重试模式 → 跳过
        if existing and existing.status == "failed" and not retry:
            skipped += 1
            continue

        try:
            # 如果有失败记录，先删除再重新生成
            if existing:
                db.delete(existing)
                db.commit()

            content = generate_magazine_content(db, couple, year, month)
            magazine = Magazine(
                couple_id=couple.id,
                year=year_str,
                month=month_str,
                content=content,
                generate_count=1,
                status="success",
            )
            db.add(magazine)
            db.commit()
            generated += 1
            if existing:
                retried += 1
        except Exception as e:
            logger.warning(f"Auto generate magazine failed for couple {couple.id}: {e}")
            db.rollback()
            # 记录失败状态（不阻塞其他情侣）
            try:
                failed = Magazine(
                    couple_id=couple.id,
                    year=year_str,
                    month=month_str,
                    content="生成失败",
                    generate_count=0,
                    status="failed",
                )
                db.add(failed)
                db.commit()
            except Exception:
                db.rollback()
            errors += 1

    return {
        "year": year,
        "month": month,
        "total_couples": len(couples),
        "generated": generated,
        "retried": retried,
        "skipped": skipped,
        "errors": errors,
    }


@router.get("/{magazine_id}", response_model=MagazineOut)
def get_magazine(
    magazine_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """获取月刊详情。"""
    couple = get_couple(current_user.id, db)
    magazine = db.query(Magazine).filter(
        Magazine.id == magazine_id,
        Magazine.couple_id == couple.id,
    ).first()
    if not magazine:
        raise HTTPException(404, "月刊不存在")
    return MagazineOut.model_validate(magazine)


@router.delete("/{magazine_id}")
def delete_magazine(
    magazine_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """删除月刊（仅允许删除失败的记录）。"""
    couple = get_couple(current_user.id, db)
    magazine = db.query(Magazine).filter(
        Magazine.id == magazine_id,
        Magazine.couple_id == couple.id,
    ).first()
    if not magazine:
        raise HTTPException(404, "月刊不存在")

    if magazine.status == "success":
        raise HTTPException(400, "已生成的月刊不可删除")

    db.delete(magazine)
    db.commit()
    return {"message": "已删除"}
