from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
import uuid
import os
from database import get_db
from models.user import User
from schemas.auth import (
    SendCodeRequest,
    LoginRequest,
    WxLoginRequest,
    PasswordLoginRequest,
    BindUsernameRequest,
    BindEmailRequest,
    UpdateProfileRequest,
    TokenResponse,
    UserProfile,
)
from services.sms import send_verification_code, verify_code, is_rate_limited
from services.wechat import code2session
from utils.password import hash_password, verify_password
from auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["认证"])


# ──────────────────────────────────────────────
# 通用工具
# ──────────────────────────────────────────────

def _build_profile(user: User, db: Session) -> UserProfile:
    from models.couple import Couple
    has_couple = db.query(Couple).filter(
        (Couple.user1_id == user.id) | (Couple.user2_id == user.id)
    ).first() is not None
    return UserProfile(
        id=user.id,
        phone=user.phone,
        nickname=user.nickname,
        avatar_url=user.avatar_url,
        username=user.username,
        email=user.email,
        birthday=user.birthday,
        gender=user.gender,
        has_couple=has_couple,
        has_password=user.password_hash is not None,
    )


def _create_token(user: User) -> TokenResponse:
    token = create_access_token(user.id)
    return TokenResponse(access_token=token, user_id=user.id, nickname=user.nickname)


# ──────────────────────────────────────────────
# 微信登录
# ──────────────────────────────────────────────

@router.post("/wx-login", response_model=TokenResponse)
async def wx_login(body: WxLoginRequest, db: Session = Depends(get_db)):
    """微信小程序 wx.login() code 换取 JWT。首次登录自动创建用户。"""
    try:
        wx_data = await code2session(body.code)
    except ValueError as e:
        raise HTTPException(400, str(e))

    openid = wx_data["openid"]
    user = db.query(User).filter(User.wx_openid == openid).first()

    if not user:
        user = User(wx_openid=openid, nickname=f"用户{openid[-6:]}")
        db.add(user)
        db.commit()
        db.refresh(user)

    return _create_token(user)


# ──────────────────────────────────────────────
# 用户名+密码登录
# ──────────────────────────────────────────────

@router.post("/login-password", response_model=TokenResponse)
def login_password(body: PasswordLoginRequest, db: Session = Depends(get_db)):
    """用户名+密码登录。"""
    user = db.query(User).filter(User.username == body.username).first()
    if not user or not user.password_hash:
        raise HTTPException(400, "用户名或密码错误")
    if not verify_password(body.password, user.password_hash):
        raise HTTPException(400, "用户名或密码错误")
    return _create_token(user)


# ──────────────────────────────────────────────
# 手机号+验证码登录（保留兼容）
# ──────────────────────────────────────────────

@router.post("/send-code")
def send_code(body: SendCodeRequest, db: Session = Depends(get_db)):
    """发送验证码（短信或邮箱）。"""
    if is_rate_limited(body.phone):
        raise HTTPException(429, "请60秒后重试")
    code = send_verification_code(body.phone, body.email)
    result = {"message": "验证码已发送"}
    from services.sms import DEV_MODE
    if DEV_MODE:
        result["dev_code"] = code
    return result


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """手机号 + 验证码登录/注册。"""
    if not verify_code(body.phone, body.code):
        raise HTTPException(400, "验证码错误或已过期")

    user = db.query(User).filter(User.phone == body.phone).first()
    if not user:
        nickname = body.nickname or f"用户{body.phone[-4:]}"
        user = User(phone=body.phone, nickname=nickname)
        db.add(user)
        db.commit()
        db.refresh(user)

    return _create_token(user)


# ──────────────────────────────────────────────
# 绑定操作
# ──────────────────────────────────────────────

@router.post("/bind-username")
def bind_username(
    body: BindUsernameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """绑定用户名+密码，同时更新昵称和生日。"""
    existing = db.query(User).filter(
        User.username == body.username, User.id != current_user.id
    ).first()
    if existing:
        raise HTTPException(400, "用户名已被占用")

    current_user.username = body.username
    current_user.password_hash = hash_password(body.password)
    if body.nickname:
        current_user.nickname = body.nickname
    if body.birthday:
        current_user.birthday = body.birthday
    db.commit()
    return {"message": "绑定成功"}


@router.post("/bind-email")
def bind_email(
    body: BindEmailRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """绑定邮箱。"""
    existing = db.query(User).filter(
        User.email == body.email, User.id != current_user.id
    ).first()
    if existing:
        raise HTTPException(400, "邮箱已被其他账号绑定")

    current_user.email = body.email
    db.commit()
    return {"message": "绑定成功"}


# ──────────────────────────────────────────────
# 头像上传
# ──────────────────────────────────────────────

@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """上传头像。"""
    allowed = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in allowed:
        raise HTTPException(400, "不支持的文件类型")

    ext = file.filename.split(".")[-1] if file.filename else "jpg"
    filename = f"avatar_{current_user.id}_{uuid.uuid4().hex[:8]}.{ext}"
    upload_dir = os.getenv("UPLOAD_DIR", "./uploads")
    avatars_dir = os.path.join(upload_dir, "avatars")
    os.makedirs(avatars_dir, exist_ok=True)

    filepath = os.path.join(avatars_dir, filename)
    content = await file.read()
    with open(filepath, "wb") as f:
        f.write(content)

    # 删除旧头像文件
    if current_user.avatar_url:
        old_filename = current_user.avatar_url.rsplit("/", 1)[-1]
        old_filepath = os.path.join(avatars_dir, old_filename)
        if os.path.exists(old_filepath):
            os.remove(old_filepath)

    base_url = os.getenv("UPLOAD_BASE_URL", "")
    avatar_url = f"{base_url}/avatars/{filename}" if base_url else f"/uploads/avatars/{filename}"
    current_user.avatar_url = avatar_url
    db.commit()

    return {"avatar_url": avatar_url}


# ──────────────────────────────────────────────
# 用户信息
# ──────────────────────────────────────────────

@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """获取当前用户信息。"""
    return _build_profile(current_user, db)


@router.put("/me")
def update_profile(
    body: UpdateProfileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """更新用户资料（昵称、生日、性别）。"""
    if body.nickname is not None:
        current_user.nickname = body.nickname
    if body.birthday is not None:
        current_user.birthday = body.birthday
    if body.gender is not None:
        current_user.gender = body.gender
    db.commit()
    return {"message": "更新成功"}


@router.delete("/me")
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """注销账号。删除头像文件和用户记录。"""
    import logging
    from services.storage import delete_file

    logger = logging.getLogger(__name__)

    # 删除头像文件
    if current_user.avatar_url and "/uploads/" in current_user.avatar_url:
        try:
            key = current_user.avatar_url.split("/uploads/")[-1]
            delete_file(key)
        except Exception as e:
            logger.warning(f"Failed to delete avatar: {e}")

    db.delete(current_user)
    db.commit()
    return {"message": "账号已注销"}
