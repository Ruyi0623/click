import os
from datetime import datetime, date
from typing import Optional
from sqlalchemy.orm import Session
from openai import OpenAI

from sqlalchemy import func as sql_func
from models.user import User
from models.couple import Couple
from models.mood import Mood
from models.anniversary import Anniversary
from models.wish import Wish
from models.fund import Fund, FundContribution
from models.transaction import Transaction
from models.penalty import Penalty
from models.footprint import Footprint
from models.capsule import Capsule
from models.diary import Diary


def get_deepseek_client() -> OpenAI:
    """获取 DeepSeek API 客户端。"""
    api_key = os.getenv("DEEPSEEK_API_KEY", "")
    return OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )


def collect_monthly_data(db: Session, couple: Couple, year: int, month: int) -> dict:
    """收集当月的情侣互动数据。"""
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1)
    else:
        end_date = date(year, month + 1, 1)

    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.min.time())

    # 心情记录
    moods = db.query(Mood).filter(
        Mood.couple_id == couple.id,
        Mood.mood_date >= start_date,
        Mood.mood_date < end_date,
    ).all()

    # 纪念日
    anniversaries = db.query(Anniversary).filter(
        Anniversary.couple_id == couple.id,
    ).all()

    # 愿望
    wishes = db.query(Wish).filter(
        Wish.couple_id == couple.id,
    ).all()

    # 日记（当月，仅文字）
    date_field = sql_func.coalesce(Diary.happened_at, Diary.created_at) if hasattr(Diary, 'happened_at') else Diary.created_at
    diaries = db.query(Diary).filter(
        Diary.couple_id == couple.id,
        Diary.created_at >= start_dt,
        Diary.created_at < end_dt,
    ).all()

    # 账单（用 happened_at 筛选，兜底 created_at）
    tx_date = sql_func.coalesce(Transaction.happened_at, Transaction.created_at)
    transactions = db.query(Transaction).filter(
        Transaction.couple_id == couple.id,
        tx_date >= start_dt,
        tx_date < end_dt,
    ).all()

    total_spent = sum(t.amount for t in transactions)
    user1_spent = sum(t.amount for t in transactions if t.paid_by == couple.user1_id)
    user2_spent = sum(t.amount for t in transactions if t.paid_by == couple.user2_id)

    # 消费分类统计
    category_stats = {}
    for t in transactions:
        category_stats[t.category] = category_stats.get(t.category, 0) + t.amount

    # 罚单
    penalties = db.query(Penalty).filter(
        Penalty.couple_id == couple.id,
        Penalty.created_at >= start_dt,
        Penalty.created_at < end_dt,
    ).all()

    user1_penalties = [p for p in penalties if p.offender_id == couple.user1_id]
    user2_penalties = [p for p in penalties if p.offender_id == couple.user2_id]

    # 基金
    funds = db.query(Fund).filter(Fund.couple_id == couple.id).all()
    contributions = db.query(FundContribution).filter(
        FundContribution.fund_id.in_([f.id for f in funds]) if funds else [],
        FundContribution.created_at >= start_dt,
        FundContribution.created_at < end_dt,
    ).all() if funds else []

    total_contributed = sum(c.amount for c in contributions if c.type == "deposit")
    total_withdrawn = sum(c.amount for c in contributions if c.type == "withdraw")

    # 足迹
    footprints = db.query(Footprint).filter(
        Footprint.couple_id == couple.id,
        Footprint.visited_at >= start_date,
        Footprint.visited_at < end_date,
    ).all()

    # 时光胶囊
    capsules = db.query(Capsule).filter(
        Capsule.couple_id == couple.id,
        Capsule.created_at >= start_dt,
        Capsule.created_at < end_dt,
    ).all()

    opened_capsules = [c for c in capsules if c.is_opened]

    # 心情统计
    mood_stats = {}
    for m in moods:
        mood_stats[m.emoji] = mood_stats.get(m.emoji, 0) + 1

    # 恋爱天数
    from datetime import date as date_type
    days_together = (date_type.today() - couple.start_date).days

    return {
        "days_together": days_together,
        "generation_time": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "mood_stats": mood_stats,
        "mood_records": [{"emoji": m.emoji, "date": str(m.mood_date)} for m in moods],
        "anniversaries": [{"title": a.title, "date": str(a.date)} for a in anniversaries],
        "wishes": [{"content": w.content, "is_done": w.is_done} for w in wishes],
        "diaries": [{"title": d.title, "content": d.content[:200]} for d in diaries],
        "total_spent": round(total_spent, 2),
        "user1_spent": round(user1_spent, 2),
        "user2_spent": round(user2_spent, 2),
        "category_stats": {k: round(v, 2) for k, v in sorted(category_stats.items(), key=lambda x: -x[1])},
        "transaction_count": len(transactions),
        "penalty_count": len(penalties),
        "user1_penalty_count": len(user1_penalties),
        "user2_penalty_count": len(user2_penalties),
        "penalty_reasons": [p.reason for p in penalties],
        "fund_count": len(funds),
        "fund_names": [f.name for f in funds],
        "total_contributed": round(total_contributed, 2),
        "total_withdrawn": round(total_withdrawn, 2),
        "footprint_count": len(footprints),
        "footprint_names": [fp.name for fp in footprints],
        "capsule_count": len(capsules),
        "capsule_opened": len(opened_capsules),
        "capsules": [
            {"content": c.content[:100], "is_opened": c.is_opened, "open_at": str(c.open_at)}
            for c in capsules
        ],
    }


def build_prompt(user1: User, user2: User, data: dict, year: int, month: int) -> str:
    """构建 AI 生成提示词。"""
    return f"""你是一位幽默风趣的"恋爱观察员"，请根据以下情侣的月度数据，生成一份《恋爱月刊》。

## 情侣信息
- 用户1: {user1.nickname}
- 用户2: {user2.nickname}
- 统计月份: {year}年{month}月
- 在一起: {data['days_together']}天
- 生成时间: {data['generation_time']}

## 月度数据

### 心情记录
- 心情统计: {data['mood_stats']}
- 心情详情: {data['mood_records']}

### 日记（本月精选）
{data['diaries'] if data['diaries'] else '本月暂无日记'}

### 纪念日
- {data['anniversaries']}

### 愿望清单
- {data['wishes']}

### 消费账单
- 本月消费总额: ¥{data['total_spent']}
- {user1.nickname}消费: ¥{data['user1_spent']}
- {user2.nickname}消费: ¥{data['user2_spent']}
- 消费分类: {data['category_stats']}
- 记账笔数: {data['transaction_count']}

### 恋爱罚单
- 本月罚单数: {data['penalty_count']}
- {user1.nickname}被罚: {data['user1_penalty_count']}次
- {user2.nickname}被罚: {data['user2_penalty_count']}次
- 罚单原因: {data['penalty_reasons']}

### 心愿基金
- 基金数量: {data['fund_count']}
- 基金名称: {data['fund_names']}
- 本月投入: ¥{data['total_contributed']}
- 本月取出: ¥{data['total_withdrawn']}

### 足迹地图
- 本月打卡: {data['footprint_count']}个地点
- 地点名称: {data['footprint_names']}

### 时光胶囊
- 本月创建: {data['capsule_count']}个
- 已开启: {data['capsule_opened']}个
- 胶囊详情: {data['capsules'] if data['capsules'] else '本月暂无胶囊'}

## 生成要求

请按以下格式生成月刊内容（使用 Markdown 格式）：

### 1. 主编致辞
以"恋爱观察员"的身份，写一段幽默、傲娇的卷首语，点评这对情侣本月的表现。点出本月最突出的一个数据亮点（消费/心情/罚单等）。要有趣味性和共鸣感。

### 2. 数据解剖室
用趣味的方式解读数据：
- 心情曲线解读（哪天最开心/最低落）
- 消费分析（谁是剁手王，钱花在哪了）
- 罚单播报（谁被罚最多，最离谱的罚单原因）
- 基金动态（存钱还是取钱，目标进度如何）
- 足迹与胶囊：如果有足迹，点评去了哪里；如果有未开启的胶囊，提醒开启时间

### 3. 恋爱大赏
根据本月数据颁发有趣的虚拟奖项，如"最佳外卖辩护律师奖"、"剁手冠军"、"罚单收割机"、"足迹探险家"等。

### 4. 恋爱天气预报
根据本月数据，预测下个月的"恋爱天气"，并附赠"相处防踩雷指南"。

请用幽默、温暖、有共鸣的语气来写，让这对情侣看了会心一笑。"""


def generate_magazine_content(db: Session, couple: Couple, year: int, month: int) -> str:
    """生成月刊内容。"""
    # 获取用户信息
    user1 = db.query(User).filter(User.id == couple.user1_id).first()
    user2 = db.query(User).filter(User.id == couple.user2_id).first()

    if not user1 or not user2:
        raise ValueError("用户信息不存在")

    # 收集数据
    data = collect_monthly_data(db, couple, year, month)

    # 构建提示词
    prompt = build_prompt(user1, user2, data, year, month)

    # 调用 DeepSeek API
    client = get_deepseek_client()
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一位幽默风趣的恋爱观察员，擅长用温暖有趣的方式解读情侣的日常。"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=2000,
    )

    return response.choices[0].message.content
