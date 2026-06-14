"""
现场报价系统
师傅检查后报价 → 客户确认 → 维修
"""
import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from sqlalchemy.orm import Session

from database import get_db
from models import WorkOrder, WorkOrderLog, OrderStatus
from schemas import ApiResponse

router = APIRouter(prefix="/api/orders", tags=["现场报价"])


class QuoteItem(BaseModel):
    name: str
    quantity: int = 1
    unit_price: float = 0
    remark: Optional[str] = ""


class SubmitQuoteRequest(BaseModel):
    items: List[QuoteItem]
    total_amount: float
    remark: Optional[str] = ""
    service_fee: Optional[float] = 0
    material_fee: Optional[float] = 0


class CustomerQuoteAction(BaseModel):
    action: str  # accept / reject
    remark: Optional[str] = ""


@router.post("/{order_id}/quote")
def submit_quote(order_id: int, data: SubmitQuoteRequest, db: Session = Depends(get_db)):
    """师傅提交报价"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.status not in (OrderStatus.ACCEPTED.value, OrderStatus.IN_PROGRESS.value):
        raise HTTPException(400, "当前工单状态不允许报价")

    # 保存报价
    items_data = [{"name": i.name, "quantity": i.quantity, "unit_price": i.unit_price, "remark": i.remark} for i in data.items]
    order.quote_items = json.dumps(items_data, ensure_ascii=False)
    order.quote_amount = data.total_amount
    order.quote_status = "pending"
    order.quoted_at = datetime.now()
    if data.service_fee:
        order.service_fee = data.service_fee
    if data.material_fee:
        order.material_fee = data.material_fee

    log_entry = WorkOrderLog(
        order_id=order_id, action="quote",
        content=f"师傅提交报价 ¥{data.total_amount}，等待客户确认"
    )
    db.add(log_entry)
    db.commit()

    return ApiResponse(message="报价已提交，等待客户确认", data={
        "quote_status": "pending",
        "quote_amount": data.total_amount,
        "quote_items": items_data,
    })


@router.get("/{order_id}/quote")
def get_quote(order_id: int, db: Session = Depends(get_db)):
    """获取报价信息"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    items = []
    if order.quote_items:
        try:
            items = json.loads(order.quote_items)
        except json.JSONDecodeError:
            items = []

    return ApiResponse(data={
        "quote_status": order.quote_status,
        "quote_amount": order.quote_amount or 0,
        "quote_items": items,
        "service_fee": order.service_fee or 0,
        "material_fee": order.material_fee or 0,
        "quoted_at": str(order.quoted_at) if order.quoted_at else None,
    })


@router.post("/{order_id}/quote/respond")
def respond_quote(order_id: int, data: CustomerQuoteAction, db: Session = Depends(get_db)):
    """客户确认/拒绝报价"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.quote_status != "pending":
        raise HTTPException(400, "报价已处理")

    if data.action == "accept":
        order.quote_status = "accepted"
        order.total_fee = order.quote_amount or (order.service_fee or 0) + (order.material_fee or 0)
        order.status = OrderStatus.IN_PROGRESS.value
        action_text = "客户已接受报价，开始维修"
        log = WorkOrderLog(order_id=order_id, action="quote_accepted", content=action_text)
        db.add(log)
        db.commit()
        return ApiResponse(message="报价已接受，师傅将开始维修")

    elif data.action == "reject":
        order.quote_status = "rejected"
        action_text = f"客户拒绝报价" + (f"：{data.remark}" if data.remark else "")
        log = WorkOrderLog(order_id=order_id, action="quote_rejected", content=action_text)
        db.add(log)
        db.commit()
        return ApiResponse(message="报价已拒绝")

    raise HTTPException(400, "无效操作")


class TripFeeRequest(BaseModel):
    amount: float = 100
    remark: Optional[str] = ""


@router.post("/{order_id}/trip-fee")
def charge_trip_fee(order_id: int, data: TripFeeRequest, db: Session = Depends(get_db)):
    """师傅收取上门费（客户拒绝报价后）"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.quote_status != "rejected":
        raise HTTPException(400, "仅拒绝报价后可收取上门费")
    if order.trip_fee_status:
        raise HTTPException(400, "上门费已收取")

    order.trip_fee = data.amount
    order.trip_fee_status = "pending"
    order.total_fee = data.amount
    order.status = "completed"

    log = WorkOrderLog(
        order_id=order_id, action="trip_fee",
        content=f"收取上门费 ¥{data.amount}" + (f" ({data.remark})" if data.remark else "")
    )
    db.add(log)
    db.commit()

    return ApiResponse(message=f"上门费 ¥{data.amount} 已设置")
