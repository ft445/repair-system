import asyncio
import threading
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from database import get_db, engine
from models import WorkOrder, OrderStatus, PayStatus, User, TechnicianWallet, WithdrawRequest, Notification
from schemas import ApiResponse
from routers.ws import send_notification as ws_send
from routers.notifications import create_notification

router = APIRouter(prefix="/api/finance", tags=["财务管理"])


@router.get("/summary")
def finance_summary(db: Session = Depends(get_db)):
    """财务总览"""
    today = date.today()
    month_start = today.replace(day=1)

    # 总收入（已完成的工单费用总和）
    total_revenue = db.query(func.coalesce(func.sum(WorkOrder.total_fee), 0)).filter(
        WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.PAID.value, OrderStatus.DONE.value])
    ).scalar() or 0

    # 本月收入
    month_revenue = db.query(func.coalesce(func.sum(WorkOrder.total_fee), 0)).filter(
        WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.PAID.value, OrderStatus.DONE.value]),
        func.date(WorkOrder.completed_at) >= month_start,
    ).scalar() or 0

    # 今日收入
    today_revenue = db.query(func.coalesce(func.sum(WorkOrder.total_fee), 0)).filter(
        WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.PAID.value, OrderStatus.DONE.value]),
        func.date(WorkOrder.completed_at) == today,
    ).scalar() or 0

    # 待收款（已完工未付款）
    pending_payment = db.query(func.coalesce(func.sum(WorkOrder.total_fee), 0)).filter(
        WorkOrder.status == OrderStatus.COMPLETED.value,
        WorkOrder.pay_status != PayStatus.PAID.value,
    ).scalar() or 0
    pending_count = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status == OrderStatus.COMPLETED.value,
        WorkOrder.pay_status != PayStatus.PAID.value,
    ).scalar() or 0

    # 已付款总额
    paid_revenue = db.query(func.coalesce(func.sum(WorkOrder.total_fee), 0)).filter(
        WorkOrder.pay_status == PayStatus.PAID.value,
    ).scalar() or 0

    # 总工单数
    total_orders = db.query(func.count(WorkOrder.id)).scalar() or 0

    # 本月工单数
    month_orders = db.query(func.count(WorkOrder.id)).filter(
        func.date(WorkOrder.created_at) >= month_start,
    ).scalar() or 0

    from sqlalchemy import text
    rate_row = db.execute(text("SELECT value FROM system_settings WHERE key = 'commission_rate'")).fetchone()
    comm_rate = float(rate_row[0]) / 100.0 if rate_row else 0.8

    return ApiResponse(data={
        "total_revenue": round(total_revenue, 2),
        "month_revenue": round(month_revenue, 2),
        "today_revenue": round(today_revenue, 2),
        "pending_payment": round(pending_payment, 2),
        "pending_count": pending_count,
        "paid_revenue": round(paid_revenue, 2),
        "total_tech_share": round(total_revenue * comm_rate, 2),
        "total_platform_share": round(total_revenue * (1 - comm_rate), 2),
        "commission_rate": int(comm_rate * 100),
        "total_orders": total_orders,
        "month_orders": month_orders,
    })


@router.get("/orders")
def finance_orders(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None, description="pay_status: paid/unpaid"),
    db: Session = Depends(get_db),
):
    """工单账单明细"""
    q = db.query(WorkOrder).filter(
        WorkOrder.total_fee > 0,
    )
    if status == "paid":
        q = q.filter(WorkOrder.pay_status == PayStatus.PAID.value)
    elif status == "unpaid":
        q = q.filter(WorkOrder.pay_status != PayStatus.PAID.value)

    total = q.count()
    items = q.order_by(WorkOrder.completed_at.desc().nullslast(), WorkOrder.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = []
    for o in items:
        customer = db.query(func.coalesce(func.count(WorkOrder.id), 0)).filter(WorkOrder.id == o.id).scalar()
        from sqlalchemy import text
        rate_row = db.execute(text("SELECT value FROM system_settings WHERE key = 'commission_rate'")).fetchone()
        comm_rate = float(rate_row[0]) / 100.0 if rate_row else 0.8
        tech_share = round((o.total_fee or 0) * comm_rate, 2)
        platform_share = round((o.total_fee or 0) * (1 - comm_rate), 2)

        result.append({
            "id": o.id,
            "order_no": o.order_no,
            "customer_id": o.customer_id,
            "technician_id": o.technician_id,
            "service_item_id": o.service_item_id,
            "category_type": o.category_type,
            "address": o.address,
            "status": o.status,
            "pay_status": o.pay_status or "unpaid",
            "material_fee": o.material_fee or 0,
            "service_fee": o.service_fee or 0,
            "total_fee": o.total_fee or 0,
            "tech_share": tech_share,
            "platform_share": platform_share,
            "commission_rate": int(comm_rate * 100),
            "payment_method": o.payment_method,
            "paid_at": str(o.paid_at) if o.paid_at else None,
            "completed_at": str(o.completed_at) if o.completed_at else None,
            "created_at": str(o.created_at) if o.created_at else None,
        })

    return ApiResponse(data={"total": total, "items": result})


@router.get("/technician-earnings")
def technician_earnings(db: Session = Depends(get_db)):
    """师傅收入排行榜"""
    wallets = db.query(
        User.id, User.name, User.phone, User.status,
        TechnicianWallet.balance, TechnicianWallet.frozen,
        TechnicianWallet.total_earned,
    ).join(TechnicianWallet, User.id == TechnicianWallet.user_id).filter(
        User.role == "technician",
    ).order_by(TechnicianWallet.total_earned.desc()).all()

    result = []
    for w in wallets:
        # 本月完成工单
        month_start = date.today().replace(day=1)
        month_orders = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.technician_id == w.id,
            WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.PAID.value, OrderStatus.DONE.value]),
            func.date(WorkOrder.completed_at) >= month_start,
        ).scalar() or 0

        # 当月收入（按工单总费用和提成比例估算）
        from sqlalchemy import text
        rate_row = db.execute(text("SELECT value FROM system_settings WHERE key = 'commission_rate'")).fetchone()
        comm_rate = float(rate_row[0]) / 100.0 if rate_row else 0.8

        month_orders_total = db.query(func.coalesce(func.sum(WorkOrder.total_fee), 0)).filter(
            WorkOrder.technician_id == w.id,
            WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.PAID.value, OrderStatus.DONE.value]),
            func.date(WorkOrder.completed_at) >= month_start,
        ).scalar() or 0

        month_commission = round(month_orders_total * comm_rate, 2)

        result.append({
            "id": w.id,
            "name": w.name,
            "phone": w.phone,
            "status": w.status,
            "balance": round(w.balance or 0, 2),
            "frozen": round(w.frozen or 0, 2),
            "total_earned": round(w.total_earned or 0, 2),
            "month_orders": month_orders,
            "month_revenue": round(month_orders_total, 2),
            "month_commission": month_commission,
            "commission_rate": int(comm_rate * 100),
        })

    return ApiResponse(data=result)


@router.get("/withdrawals")
def withdrawal_list(
    user_id: Optional[int] = Query(None, description="师傅ID，师傅端查看自己的记录"),
    status: Optional[str] = Query(None, description="pending/approved/rejected/done"),
    db: Session = Depends(get_db),
):
    """提现申请列表"""
    q = db.query(WithdrawRequest).order_by(WithdrawRequest.created_at.desc())
    if user_id:
        q = q.filter(WithdrawRequest.user_id == user_id)
    if status:
        q = q.filter(WithdrawRequest.status == status)

    items = q.all()
    result = []
    for w in items:
        user = db.query(User).filter(User.id == w.user_id).first()
        result.append({
            "id": w.id,
            "user_id": w.user_id,
            "user_name": user.name if user else "-",
            "amount": w.amount,
            "bank_card": w.bank_card,
            "status": w.status,
            "audit_time": str(w.audit_time) if w.audit_time else None,
            "remark": w.remark,
            "created_at": str(w.created_at) if w.created_at else None,
        })

    return ApiResponse(data=result)


@router.post("/withdrawals")
def create_withdrawal(data: dict, db: Session = Depends(get_db)):
    """师傅发起提现申请"""
    user_id = data.get("user_id")
    amount = data.get("amount")
    method = data.get("method", "wechat")

    if not user_id or not amount or amount <= 0:
        raise HTTPException(400, "参数无效")

    wallet = db.query(TechnicianWallet).filter(TechnicianWallet.user_id == user_id).first()
    if not wallet or wallet.balance < amount:
        raise HTTPException(400, "余额不足")

    # 冻结余额
    wallet.frozen = (wallet.frozen or 0) + amount
    wallet.balance -= amount

    req = WithdrawRequest(
        user_id=user_id,
        amount=amount,
        bank_card=method,
        status="pending",
    )
    db.add(req)
    db.commit()
    db.refresh(req)
    return ApiResponse(data={"id": req.id}, message="提现申请已提交")


@router.post("/withdrawals/{withdraw_id}/audit")
def audit_withdrawal(withdraw_id: int, data: dict, db: Session = Depends(get_db)):
    """审核提现申请"""
    req = db.query(WithdrawRequest).filter(WithdrawRequest.id == withdraw_id).first()
    if not req:
        raise HTTPException(404, "提现申请不存在")

    action = data.get("action", "approve")
    remark = data.get("remark", "")

    if action == "approve":
        req.status = "approved"
    elif action == "reject":
        req.status = "rejected"
    else:
        raise HTTPException(400, "无效操作")

    req.audit_time = func.now()
    req.remark = remark
    db.commit()

    # 通知师傅
    try:
        action_text = "批准" if action == "approve" else "驳回"
        content = f"您的提现申请 ¥{req.amount} 已被{action_text}"
        if remark:
            content += f"（备注：{remark}）"
        n = create_notification(
            db, user_id=req.user_id,
            type="withdraw_review",
            title=f"提现{action_text}",
            content=content,
            ref_id=withdraw_id, ref_type="withdraw",
        )
        db.commit()
        threading.Thread(
            target=lambda: asyncio.run(ws_send(
                req.user_id, "withdraw_review",
                f"提现{action_text}",
                content,
                withdraw_id, "withdraw",
            )),
            daemon=True,
        ).start()
    except Exception:
        pass

    return ApiResponse(message=f"提现已{ '批准' if action=='approve' else '驳回' }")


# ─── 提成设置 ───

@router.get("/settings")
def get_finance_settings(db: Session = Depends(get_db)):
    """获取财务设置"""
    from sqlalchemy import text
    rows = db.execute(text("SELECT key, value, description FROM system_settings")).fetchall()
    settings = {row[0]: {"value": row[1], "description": row[2]} for row in rows}
    return ApiResponse(data=settings)


@router.put("/settings")
def update_finance_settings(data: dict, db: Session = Depends(get_db)):
    """更新财务设置"""
    from sqlalchemy import text
    allowed = {"commission_rate", "platform_fee_percent", "commission_fixed", "auto_dispatch_enabled"}
    for key, val in data.items():
        if key in allowed:
            db.execute(
                text("UPDATE system_settings SET value = :val WHERE key = :key"),
                {"val": str(val), "key": key}
            )
    db.commit()
    return ApiResponse(message="设置已更新")
