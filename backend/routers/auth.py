from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import User, TechnicianWallet
from schemas import UserCreate, UserLogin, UserOut, TokenOut, ApiResponse
from utils.auth import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register")
def register(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.phone == data.phone).first()
    if existing:
        raise HTTPException(400, "手机号已注册")

    user = User(
        name=data.name,
        phone=data.phone,
        password_hash=hash_password(data.password),
        role=data.role,
        org_id=data.org_id,
        id_card=data.id_card,
        address=data.address,
        emergency_contact=data.emergency_contact,
        emergency_phone=data.emergency_phone,
        hire_date=data.hire_date,
    )
    db.add(user)
    db.flush()

    # 如果是师傅，自动创建钱包
    if data.role == "technician":
        wallet = TechnicianWallet(user_id=user.id, balance=0, frozen=0, total_earned=0)
        db.add(wallet)

    db.commit()
    db.refresh(user)
    return ApiResponse(data={"id": user.id}, message="创建成功")


@router.post("/login")
def login(data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.phone == data.phone).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, "手机号或密码错误")
    if user.status != "active":
        raise HTTPException(403, "账号已禁用")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return ApiResponse(data=TokenOut(
        access_token=token,
        user=UserOut.model_validate(user),
    ))


@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    return ApiResponse(data=UserOut.model_validate(current_user))


@router.post("/change-password")
def change_password(data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """修改密码"""
    old_pwd = data.get("old_password")
    new_pwd = data.get("new_password")
    if not old_pwd or not new_pwd:
        raise HTTPException(400, "请输入旧密码和新密码")
    if len(new_pwd) < 6:
        raise HTTPException(400, "新密码至少6位")
    if not verify_password(old_pwd, current_user.password_hash):
        raise HTTPException(400, "旧密码错误")

    current_user.password_hash = hash_password(new_pwd)
    db.commit()
    return ApiResponse(message="密码已修改")


@router.get("/admins")
def list_admins(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """获取所有管理员/调度员"""
    if current_user.role != "admin":
        raise HTTPException(403, "仅管理员可查看")

    users = db.query(User).filter(
        User.role.in_(["admin", "dispatcher"])
    ).order_by(User.created_at.desc()).all()

    result = []
    for u in users:
        result.append({
            "id": u.id,
            "name": u.name,
            "phone": u.phone,
            "role": u.role,
            "org_id": u.org_id,
            "status": u.status,
            "created_at": str(u.created_at) if u.created_at else None,
        })

    return ApiResponse(data=result)


@router.put("/admins/{user_id}/reset-password")
def reset_admin_password(user_id: int, data: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """管理员重置他人密码"""
    if current_user.role != "admin":
        raise HTTPException(403, "仅管理员可操作")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")

    new_password = data.get("new_password", "123456")
    user.password_hash = hash_password(new_password)
    db.commit()
    return ApiResponse(message=f"密码已重置为 {new_password}")
