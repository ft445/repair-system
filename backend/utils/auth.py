from datetime import datetime, timedelta, timezone
import bcrypt
from jose import jwt, JWTError
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from config import settings
from database import get_db
from models import User

security = HTTPBearer()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """从 JWT token 解析当前登录用户"""
    token = credentials.credentials
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(401, "无效的认证凭据")
    except JWTError:
        raise HTTPException(401, "无效的认证凭据")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(401, "用户不存在")
    if user.status != "active":
        raise HTTPException(403, "账号已禁用")
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """要求管理员权限"""
    if current_user.role not in ("admin", "dispatcher"):
        raise HTTPException(403, "需要管理员或调度员权限")
    return current_user
