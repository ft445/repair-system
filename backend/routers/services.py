from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional

from database import get_db
from models import ServiceCategory, ServiceItem
from schemas import (
    ServiceCategoryCreate, ServiceCategoryUpdate, ServiceCategoryOut,
    ServiceItemCreate, ServiceItemUpdate, ServiceItemOut,
    ApiResponse,
)

router = APIRouter(prefix="/api/services", tags=["服务管理"])


@router.get("/categories")
def list_categories(db: Session = Depends(get_db)):
    items = db.query(ServiceCategory).filter(
        ServiceCategory.status == "active"
    ).order_by(ServiceCategory.sort_order).all()
    return ApiResponse(data=[ServiceCategoryOut.model_validate(c) for c in items])


@router.post("/categories")
def create_category(data: ServiceCategoryCreate, db: Session = Depends(get_db)):
    cat = ServiceCategory(**data.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return ApiResponse(data={"id": cat.id})


@router.put("/categories/{category_id}")
def update_category(category_id: int, data: ServiceCategoryUpdate, db: Session = Depends(get_db)):
    cat = db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    if not cat:
        raise HTTPException(404, "分类不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(cat, key, val)
    db.commit()
    return ApiResponse(data=ServiceCategoryOut.model_validate(cat))


@router.delete("/categories/{category_id}")
def delete_category(category_id: int, db: Session = Depends(get_db)):
    cat = db.query(ServiceCategory).filter(ServiceCategory.id == category_id).first()
    if not cat:
        raise HTTPException(404, "分类不存在")
    cat.status = "inactive"
    # 同时禁用分类下所有项目
    db.query(ServiceItem).filter(ServiceItem.category_id == category_id).update({"status": "inactive"})
    db.commit()
    return ApiResponse(message="分类已删除")


@router.get("/items")
def list_items(
    category_id: Optional[int] = Query(None),
    parent_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    q = db.query(ServiceItem).filter(ServiceItem.status == "active")
    if category_id:
        q = q.filter(ServiceItem.category_id == category_id)
    if parent_id is not None:
        q = q.filter(ServiceItem.parent_id == parent_id)
    items = q.order_by(ServiceItem.sort_order).all()
    return ApiResponse(data=[ServiceItemOut.model_validate(i) for i in items])


@router.post("/items")
def create_item(data: ServiceItemCreate, db: Session = Depends(get_db)):
    item = ServiceItem(**data.model_dump())
    db.add(item)
    db.commit()
    db.refresh(item)
    return ApiResponse(data={"id": item.id})


@router.put("/items/{item_id}")
def update_item(item_id: int, data: ServiceItemUpdate, db: Session = Depends(get_db)):
    item = db.query(ServiceItem).filter(ServiceItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "服务项目不存在")
    for key, val in data.model_dump(exclude_unset=True).items():
        setattr(item, key, val)
    db.commit()
    db.refresh(item)
    return ApiResponse(data=ServiceItemOut.model_validate(item))


@router.delete("/items/{item_id}")
def delete_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(ServiceItem).filter(ServiceItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "服务项目不存在")
    item.status = "inactive"
    db.commit()
    return ApiResponse(message="服务项目已删除")
