from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import Organization, OrgLevel, User
from schemas import ApiResponse

router = APIRouter(prefix="/api/organizations", tags=["组织管理"])


@router.get("")
def list_organizations(
    level: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """获取组织列表"""
    q = db.query(Organization).order_by(Organization.id)
    if level:
        q = q.filter(Organization.level == level)
    orgs = q.all()

    result = []
    for org in orgs:
        # 统计该组织下的师傅人数
        tech_count = db.query(User).filter(
            User.org_id == org.id,
            User.role == "technician",
        ).count()

        # 查找管理员
        admins = db.query(User).filter(
            User.org_id == org.id,
            User.role.in_(["admin", "dispatcher"]),
            User.status == "active",
        ).all()

        result.append({
            "id": org.id,
            "name": org.name,
            "parent_id": org.parent_id,
            "city": org.city,
            "address": org.address,
            "level": org.level,
            "contact_phone": org.contact_phone,
            "status": org.status,
            "tech_count": tech_count,
            "managers": [{"id": a.id, "name": a.name, "phone": a.phone, "role": a.role} for a in admins],
            "created_at": str(org.created_at) if org.created_at else None,
        })

    return ApiResponse(data=result)


@router.post("")
def create_organization(data: dict, db: Session = Depends(get_db)):
    """创建组织"""
    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(400, "请输入组织名称")

    org = Organization(
        name=name,
        parent_id=data.get("parent_id"),
        city=data.get("city", ""),
        address=data.get("address", ""),
        level=data.get("level", "branch"),
        contact_phone=data.get("contact_phone", ""),
    )
    db.add(org)
    db.commit()
    db.refresh(org)
    return ApiResponse(data={"id": org.id}, message="组织已创建")


@router.put("/{org_id}")
def update_organization(org_id: int, data: dict, db: Session = Depends(get_db)):
    """更新组织"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "组织不存在")

    for field in ["name", "city", "address", "contact_phone", "status"]:
        if field in data:
            setattr(org, field, data[field])

    db.commit()
    return ApiResponse(message="组织已更新")


@router.delete("/{org_id}")
def delete_organization(org_id: int, db: Session = Depends(get_db)):
    """删除组织"""
    org = db.query(Organization).filter(Organization.id == org_id).first()
    if not org:
        raise HTTPException(404, "组织不存在")

    # 检查是否有师傅关联
    tech_count = db.query(User).filter(User.org_id == org_id).count()
    if tech_count > 0:
        raise HTTPException(400, f"该组织下有 {tech_count} 名师傅，不能删除")

    org.status = "disabled"
    db.commit()
    return ApiResponse(message="组织已停用")
