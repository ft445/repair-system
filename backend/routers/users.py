from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from utils.auth import hash_password
from models import User
from schemas import UserOut, ApiResponse

router = APIRouter(prefix="/api/users", tags=["用户管理"])


@router.get("")
def list_users(
    role: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(User)
    if role:
        q = q.filter(User.role == role)
    users = q.order_by(User.created_at.desc()).all()
    return ApiResponse(data=[UserOut.model_validate(u) for u in users])


@router.put("/{user_id}/status")
def update_user_status(user_id: int, data: dict, db: Session = Depends(get_db)):
    """更新用户状态（active/disabled）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")

    new_status = data.get("status")
    if new_status not in ("active", "disabled", "paused"):
        raise HTTPException(400, "状态值无效（active/disabled/paused）")

    user.status = new_status
    db.commit()
    return ApiResponse(message="状态已更新")


@router.put("/{user_id}/profile")
def update_user_profile(user_id: int, data: dict, db: Session = Depends(get_db)):
    """更新用户档案"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")

    allowed = {"id_card", "address", "emergency_contact", "emergency_phone", "hire_date", "name", "phone", "org_id"}
    for key, val in data.items():
        if key == "password":
            user.password_hash = hash_password(val)
        elif key in allowed:
            setattr(user, key, val)

    db.commit()
    return ApiResponse(message="档案已更新")


@router.get("/{user_id}/profile")
def get_user_profile(user_id: int, db: Session = Depends(get_db)):
    """获取用户详细信息"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    return ApiResponse(data={
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "role": user.role,
        "org_id": user.org_id,
        "status": user.status,
        "id_card": user.id_card,
        "address": user.address,
        "emergency_contact": user.emergency_contact,
        "emergency_phone": user.emergency_phone,
        "hire_date": user.hire_date,
        "created_at": str(user.created_at) if user.created_at else None,
    })
