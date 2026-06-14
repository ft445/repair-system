from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import get_db
from models import WorkOrder, WorkOrderPart
from schemas import ApiResponse

router = APIRouter(prefix="/api/orders", tags=["工单配件"])


@router.get("/{order_id}/parts")
def list_parts(order_id: int, db: Session = Depends(get_db)):
    """获取工单配件列表"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    parts = db.query(WorkOrderPart).filter(
        WorkOrderPart.order_id == order_id
    ).order_by(WorkOrderPart.created_at).all()

    result = []
    for p in parts:
        result.append({
            "id": p.id,
            "order_id": p.order_id,
            "name": p.name,
            "brand": p.brand,
            "model_no": p.model_no,
            "quantity": p.quantity,
            "unit_price": p.unit_price,
            "total_price": p.total_price,
            "part_type": p.part_type,
            "receipt_image": p.receipt_image,
            "part_photo": p.part_photo,
            "notes": p.notes,
            "store_name": p.store_name,
            "store_phone": p.store_phone,
            "created_at": str(p.created_at) if p.created_at else None,
        })

    return ApiResponse(data=result)


@router.post("/{order_id}/parts")
def add_part(order_id: int, data: dict, db: Session = Depends(get_db)):
    """添加工单配件"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    name = data.get("name", "").strip()
    if not name:
        raise HTTPException(400, "请输入配件名称")

    quantity = data.get("quantity", 1)
    unit_price = data.get("unit_price", 0)
    total_price = data.get("total_price", quantity * unit_price)

    part = WorkOrderPart(
        order_id=order_id,
        name=name,
        brand=data.get("brand", ""),
        store_name=data.get("store_name", ""),
        store_phone=data.get("store_phone", ""),
        model_no=data.get("model_no", ""),
        quantity=quantity,
        unit_price=unit_price,
        total_price=data.get("total_price", total_price),
        part_type=data.get("part_type", "new"),
        receipt_image=data.get("receipt_image", ""),
        part_photo=data.get("part_photo", ""),
        notes=data.get("notes", ""),
    )
    db.add(part)
    db.commit()
    db.refresh(part)
    return ApiResponse(data={"id": part.id}, message="配件已添加")


@router.put("/parts/{part_id}")
def update_part(part_id: int, data: dict, db: Session = Depends(get_db)):
    """更新配件信息"""
    part = db.query(WorkOrderPart).filter(WorkOrderPart.id == part_id).first()
    if not part:
        raise HTTPException(404, "配件不存在")

    for field in ["name", "brand", "model_no", "quantity", "unit_price", "total_price", "part_type", "receipt_image", "part_photo", "notes"]:
        if field in data:
            setattr(part, field, data[field])

    db.commit()
    return ApiResponse(message="配件已更新")


@router.delete("/parts/{part_id}")
def delete_part(part_id: int, db: Session = Depends(get_db)):
    """删除配件"""
    part = db.query(WorkOrderPart).filter(WorkOrderPart.id == part_id).first()
    if not part:
        raise HTTPException(404, "配件不存在")

    db.delete(part)
    db.commit()
    return ApiResponse(message="配件已删除")
