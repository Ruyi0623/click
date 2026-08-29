import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from database import get_db
from models.user import User

JWT_SECRET = os.getenv("JWT_SECRET", "")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = int(os.getenv("JWT_EXPIRE_DAYS", "7"))

# 启动时检查 JWT_SECRET 是否已配置
_INSECURE_SECRETS = {"", "dev-secret-change-in-production", "your-secret-key-change-this", "root123"}
if JWT_SECRET in _INSECURE_SECRETS:
    raise RuntimeError(
        "JWT_SECRET 未配置或使用了不安全的默认值，请在 .env 中设置一个强随机密钥。"
        "可使用命令: python -c \"import secrets; print(secrets.token_urlsafe(48))\""
    )

security = HTTPBearer()


def create_access_token(user_id: str) -> str:
    expire = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": user_id, "exp": expire},
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="无效的认证凭据")
        return user_id
    except JWTError:
        raise HTTPException(status_code=401, detail="无效的认证凭据")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    user_id = decode_token(credentials.credentials)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=401, detail="用户不存在")
    return user
