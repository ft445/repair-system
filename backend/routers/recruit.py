"""师傅入驻申请"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db
from models.application import TechApplication
from schemas import ApiResponse

router = APIRouter(prefix="/api/recruit", tags=["师傅入驻"])


class ApplyRequest(BaseModel):
    name: str
    phone: str
    age: Optional[int] = None
    skill: Optional[str] = ""
    experience: Optional[str] = ""
    area: Optional[str] = ""
    tools: Optional[str] = ""


@router.post("/apply")
def tech_apply(data: ApplyRequest, db: Session = Depends(get_db)):
    """师傅在线报名"""
    if not data.name or not data.phone:
        return ApiResponse(code=-1, message="请填写姓名和手机号")

    app = TechApplication(
        name=data.name, phone=data.phone, age=data.age,
        skill=data.skill, experience=data.experience,
        area=data.area, tools=data.tools,
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return ApiResponse(message="报名成功，我们会尽快联系您")


@router.get("/list")
def list_applications(db: Session = Depends(get_db)):
    """管理员查看报名列表"""
    items = db.query(TechApplication).order_by(TechApplication.created_at.desc()).all()
    result = []
    for a in items:
        result.append({
            "id": a.id, "name": a.name, "phone": a.phone,
            "age": a.age, "skill": a.skill, "experience": a.experience,
            "area": a.area, "tools": a.tools, "status": a.status,
            "remark": a.remark, "created_at": str(a.created_at)[:19] if a.created_at else None,
        })
    return ApiResponse(data=result)
