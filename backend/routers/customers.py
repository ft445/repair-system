from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import Customer
from schemas import CustomerCreate, CustomerOut, ApiResponse

router = APIRouter(prefix="/api/customers", tags=["客户管理"])


@router.get("")
def list_customers(db: Session = Depends(get_db)):
    customers = db.query(Customer).order_by(Customer.created_at.desc()).all()
    return ApiResponse(data=[CustomerOut.model_validate(c) for c in customers])


@router.post("/find")
def find_or_create(data: CustomerCreate, db: Session = Depends(get_db)):
    """查找或创建客户"""
    customer = db.query(Customer).filter(Customer.phone == data.phone).first()
    if customer:
        # 更新信息
        if data.name:
            customer.name = data.name
        if data.address:
            customer.address = data.address
        db.commit()
        db.refresh(customer)
        return ApiResponse(data={"id": customer.id, "is_new": False})

    customer = Customer(**data.model_dump())
    db.add(customer)
    db.commit()
    db.refresh(customer)
    return ApiResponse(data={"id": customer.id, "is_new": True})
