import asyncio
import threading
from datetime import date, datetime, timezone
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from database import get_db
from models import WorkOrder, WorkOrderLog, Customer, User, ServiceItem, TechnicianSkill, OrderStatus, PayStatus, Notification
from schemas import (
    WorkOrderCreate, WorkOrderUpdate, WorkOrderOut,
    WorkOrderListOut, ApiResponse,
)
from utils.helpers import generate_order_no
from routers.ws import send_notification as ws_send
from routers.notifications import create_notification

router = APIRouter(prefix="/api/orders", tags=["工单管理"])


def enrich_order(order, db):
    """填充关联字段"""
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if customer:
        order.customer_name = customer.name
        order.customer_phone = customer.phone
    if order.technician_id:
        tech = db.query(User).filter(User.id == order.technician_id).first()
        if tech:
            order.technician_name = tech.name
            order.technician_phone = tech.phone
    item = db.query(ServiceItem).filter(ServiceItem.id == order.service_item_id).first()
    if item:
        order.service_item_name = item.name
    return order


@router.post("")
def create_order(data: WorkOrderCreate, db: Session = Depends(get_db)):
    """客人扫码报修"""
    order = WorkOrder(
        order_no=generate_order_no(),
        customer_id=data.customer_id,
        service_item_id=data.service_item_id,
        category_type=data.category_type,
        fault_description=data.fault_description,
        address=data.address,
        appointment_time=data.appointment_time,
        images=data.images,
        source=data.source or "qrcode",
        status=OrderStatus.PENDING.value,
    )
    db.add(order)

    # 更新客户总工单数
    customer = db.query(Customer).filter(Customer.id == data.customer_id).first()
    if customer:
        customer.total_orders = (customer.total_orders or 0) + 1

    db.commit()
    db.refresh(order)
    order_id = order.id

    # 1秒后自动标记为已接单 + 检查自动派单
    async def auto_process():
        await asyncio.sleep(1)
        from database import SessionLocal
        from sqlalchemy import text as sa_text
        from models import TechnicianSkill, TechnicianAttendance as TA, LeaveRequest as LR
        from datetime import date as dt_date
        bg_db = SessionLocal()
        try:
            o = bg_db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
            if not o:
                return
            # Auto accept
            if o.status == OrderStatus.PENDING.value:
                o.status = OrderStatus.ACCEPTED.value
                bg_db.add(WorkOrderLog(order_id=order_id, action="auto_accept", content="系统自动接单"))
                bg_db.commit()

            # Check auto dispatch setting
            row = bg_db.execute(sa_text("SELECT value FROM system_settings WHERE key = 'auto_dispatch_enabled'")).fetchone()
            if not row or row[0] != '1':
                return

            # Auto dispatch logic (simplified from auto_dispatch_order)
            techs = bg_db.query(User).filter(User.role == "technician", User.status == "active").all()
            if not techs:
                return

            today = dt_date.today()
            best_tech, best_score = None, -999
            for tech in techs:
                skill = bg_db.query(TechnicianSkill).filter(
                    TechnicianSkill.user_id == tech.id,
                    TechnicianSkill.service_item_id == o.service_item_id,
                    TechnicianSkill.status == "active",
                ).first()
                if not skill:
                    continue
                score = 10
                if skill.level == "senior": score += 5
                elif skill.level == "medium": score += 3
                active_cnt = bg_db.query(func.count(WorkOrder.id)).filter(
                    WorkOrder.technician_id == tech.id,
                    WorkOrder.status.in_(["dispatched","accepted","in_progress"]),
                ).scalar() or 0
                score -= active_cnt * 2
                total_done = bg_db.query(func.count(WorkOrder.id)).filter(
                    WorkOrder.technician_id == tech.id,
                    WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.DONE.value]),
                ).scalar() or 0
                score += min(total_done, 5)
                on_leave = bg_db.query(LR).filter(
                    LR.user_id == tech.id, LR.start_date <= today, LR.end_date >= today,
                    LR.status == "approved",
                ).first()
                if on_leave: score -= 100
                if score > best_score:
                    best_score, best_tech = score, tech

            if best_tech:
                o.technician_id = best_tech.id
                o.status = OrderStatus.DISPATCHED.value
                bg_db.add(WorkOrderLog(order_id=order_id, action="auto_dispatch", content=f"自动派单给 {best_tech.name}"))
                bg_db.commit()
        finally:
            bg_db.close()

    import threading
    threading.Thread(target=lambda: asyncio.run(auto_process()), daemon=True).start()

    return ApiResponse(data={"id": order.id, "order_no": order.order_no})


@router.get("")
def list_orders(
    status: Optional[str] = Query(None),
    technician_id: Optional[int] = Query(None),
    keyword: Optional[str] = Query(None, description="搜索客户姓名/手机号/地址"),
    date_from: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    date_to: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    q = db.query(WorkOrder)
    if status == "active":
        q = q.filter(WorkOrder.status.in_([OrderStatus.DISPATCHED.value, OrderStatus.IN_PROGRESS.value]))
    elif status == "undispatch":
        q = q.filter(WorkOrder.status.in_([OrderStatus.PENDING.value, OrderStatus.ACCEPTED.value]))
    elif status == "today":
        q = q.filter(func.date(WorkOrder.created_at) == date.today())
    elif status == "completed_today":
        q = q.filter(
            WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.DONE.value, OrderStatus.PAID.value]),
            func.date(WorkOrder.completed_at) == date.today(),
        )
    elif status:
        q = q.filter(WorkOrder.status == status)
    if technician_id:
        q = q.filter(WorkOrder.technician_id == technician_id)
    if date_from:
        q = q.filter(func.date(WorkOrder.created_at) >= date_from)
    if date_to:
        q = q.filter(func.date(WorkOrder.created_at) <= date_to)
    if keyword:
        # 搜索：工单号 / 客户姓名 / 手机号 / 地址
        q = q.filter(
            WorkOrder.order_no.contains(keyword) |
            WorkOrder.customer_id.in_(
                db.query(Customer.id).filter(
                    Customer.name.contains(keyword) |
                    Customer.phone.contains(keyword) |
                    Customer.address.contains(keyword)
                )
            )
        )

    total = q.count()
    orders = q.order_by(WorkOrder.created_at.desc()).offset(
        (page - 1) * page_size
    ).limit(page_size).all()

    result = [WorkOrderOut.model_validate(enrich_order(o, db)) for o in orders]
    return ApiResponse(data={"total": total, "items": result})


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    logs = db.query(WorkOrderLog).filter(
        WorkOrderLog.order_id == order_id
    ).order_by(WorkOrderLog.created_at).all()

    return ApiResponse(data={
        "order": WorkOrderOut.model_validate(enrich_order(order, db)),
        "logs": [{"id": l.id, "action": l.action, "content": l.content, "created_at": str(l.created_at)} for l in logs],
    })


@router.put("/{order_id}")
def update_order(order_id: int, data: WorkOrderUpdate, db: Session = Depends(get_db)):
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(order, key, value)

    log = WorkOrderLog(
        order_id=order_id,
        action=f"update_{data.status or 'info'}",
        content=f"更新: status={data.status}",
    )
    db.add(log)
    db.commit()
    return ApiResponse(message="更新成功")


@router.post("/{order_id}/dispatch")
def dispatch_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    """调度派单（管理员/调度员操作）"""
    technician_id = data.get("technician_id")
    if not technician_id:
        raise HTTPException(400, "请指定师傅ID")

    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.status not in [OrderStatus.PENDING.value, OrderStatus.ACCEPTED.value, OrderStatus.DISPATCHED.value, OrderStatus.IN_PROGRESS.value]:
        raise HTTPException(400, f"当前状态「{order.status}」不可派单")

    # 验证师傅存在且是 active 状态
    tech = db.query(User).filter(
        User.id == technician_id,
        User.role == "technician",
        User.status == "active",
    ).first()
    if not tech:
        raise HTTPException(400, "指定的师傅不存在或已禁用")

    # 验证师傅有对应技能才能派单
    skill = db.query(TechnicianSkill).filter(
        TechnicianSkill.user_id == technician_id,
        TechnicianSkill.service_item_id == order.service_item_id,
        TechnicianSkill.status == "active",
    ).first()
    if not skill:
        item = db.query(ServiceItem).filter(ServiceItem.id == order.service_item_id).first()
        item_name = item.name if item else "未知"
        raise HTTPException(400, f"该师傅没有「{item_name}」技能，无法派单")

    order.technician_id = technician_id
    order.status = OrderStatus.DISPATCHED.value

    db.add(WorkOrderLog(
        order_id=order_id,
        action="dispatch",
        content=f"派单给 {tech.name}(ID:{technician_id})",
    ))

    # 创建通知
    create_notification(
        db, user_id=technician_id,
        type="order_dispatch",
        title="新工单已派单",
        content=f"您有新的工单 #{order.order_no}，请及时查看处理",
        ref_id=order_id, ref_type="order",
    )

    db.commit()

    # WebSocket实时推送（后台线程，不影响主流程）
    try:
        threading.Thread(
            target=lambda: asyncio.run(ws_send(
                technician_id, "order_dispatch",
                "新工单已派单",
                f"您有新的工单 #{order.order_no}，请及时查看处理",
                order_id, "order",
            )),
            daemon=True,
        ).start()
    except Exception:
        pass

    return ApiResponse(message=f"已派单给 {tech.name}")


@router.post("/{order_id}/refund")
def refund_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    """退款（取消工单并标记退款）"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    reason = data.get("reason", "客户退款")
    order.status = OrderStatus.CANCELLED.value
    order.pay_status = PayStatus.REFUNDED.value

    db.add(WorkOrderLog(
        order_id=order_id,
        action="refund",
        content=f"退款：{reason}",
    ))
    db.commit()
    return ApiResponse(message="已退款")


@router.post("/{order_id}/auto-dispatch")
def auto_dispatch_order(order_id: int, db: Session = Depends(get_db)):
    """智能派单：根据技能匹配+工作量最少优先"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.status not in [OrderStatus.PENDING.value, OrderStatus.ACCEPTED.value, OrderStatus.DISPATCHED.value, OrderStatus.IN_PROGRESS.value]:
        raise HTTPException(400, f"当前状态不可派单")

    # 找到该工单所属分类的师傅（有相关技能）
    from models import TechnicianSkill, TechnicianAttendance, LeaveRequest
    from datetime import date

    today = date.today()
    now = datetime.now()

    # 获取所有 active 师傅
    techs = db.query(User).filter(
        User.role == "technician",
        User.status == "active",
    ).all()

    best_tech = None
    best_score = -999

    for tech in techs:
        # 1. 必须有对应技能才能参与派单
        skill = db.query(TechnicianSkill).filter(
            TechnicianSkill.user_id == tech.id,
            TechnicianSkill.service_item_id == order.service_item_id,
            TechnicianSkill.status == "active",
        ).first()
        if not skill:
            continue

        score = 10
        if skill.level == "senior":
            score += 5
        elif skill.level == "medium":
            score += 3

        # 2. 如果有同分类的其他技能也加分
        cat_skills = db.query(TechnicianSkill).filter(
            TechnicianSkill.user_id == tech.id,
            TechnicianSkill.status == "active",
        ).join(ServiceItem, TechnicianSkill.service_item_id == ServiceItem.id).filter(
            ServiceItem.category_id == order.service_item_id,  # approximate
        ).count()
        score += min(cat_skills, 3)

        # 3. 当前工作量少加分（进行中工单越少越好）
        active_orders = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.technician_id == tech.id,
            WorkOrder.status.in_([OrderStatus.DISPATCHED.value, OrderStatus.ACCEPTED.value, OrderStatus.IN_PROGRESS.value]),
        ).scalar() or 0
        score -= active_orders * 2  # 每多一个进行中工单减2分

        # 4. 总工单量经验加分
        total_done = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.technician_id == tech.id,
            WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.DONE.value]),
        ).scalar() or 0
        score += min(total_done, 5)

        # 5. 今日已请假扣分
        on_leave = db.query(LeaveRequest).filter(
            LeaveRequest.user_id == tech.id,
            LeaveRequest.start_date <= today,
            LeaveRequest.end_date >= today,
            LeaveRequest.status == "approved",
        ).first()
        if on_leave:
            score -= 100  # 请假直接排到最后

        # 6. 今日已打卡加分（表示在岗）
        clocked_in = db.query(TechnicianAttendance).filter(
            TechnicianAttendance.user_id == tech.id,
            TechnicianAttendance.date == today,
        ).first()
        if clocked_in:
            score += 2

        if score > best_score:
            best_score = score
            best_tech = tech

    if not best_tech:
        raise HTTPException(400, "没有可派单的师傅")

    order.technician_id = best_tech.id
    order.status = OrderStatus.DISPATCHED.value

    db.add(WorkOrderLog(
        order_id=order_id,
        action="auto_dispatch",
        content=f"智能派单给 {best_tech.name} (得分:{best_score})",
    ))
    db.commit()
    return ApiResponse(message=f"智能派单完成：已派给 {best_tech.name}", data={
        "technician_id": best_tech.id,
        "technician_name": best_tech.name,
        "score": best_score,
    })


@router.post("/{order_id}/cancel")
def cancel_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    """取消工单"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    cancelled_statuses = [OrderStatus.CANCELLED.value, OrderStatus.DONE.value]
    if order.status in cancelled_statuses:
        raise HTTPException(400, "工单已结束，不能取消")

    reason = data.get("reason", "管理员取消")
    order.status = OrderStatus.CANCELLED.value

    db.add(WorkOrderLog(
        order_id=order_id,
        action="cancel",
        content=f"已取消：{reason}",
    ))

    # 通知师傅
    if order.technician_id:
        try:
            n = create_notification(
                db, user_id=order.technician_id,
                type="order_status",
                title="工单已取消",
                content=f"工单 #{order.order_no} 已取消：{reason}",
                ref_id=order_id, ref_type="order",
            )
            db.commit()
            threading.Thread(
                target=lambda: asyncio.run(ws_send(
                    order.technician_id, "order_status",
                    "工单已取消",
                    f"工单 #{order.order_no} 已取消：{reason}",
                    order_id, "order",
                )),
                daemon=True,
            ).start()
        except Exception:
            pass

    db.commit()
    return ApiResponse(message="工单已取消")


@router.put("/{order_id}/cancel-review")
def review_cancel_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    """审核师傅取消申请"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.status != OrderStatus.CANCEL_PENDING.value:
        raise HTTPException(400, "该工单无需审核")

    action = data.get("action", "approve")
    reason = data.get("reason", "")

    if action == "approve":
        order.status = OrderStatus.CANCELLED.value
        order.technician_id = None
        db.add(WorkOrderLog(order_id=order_id, action="cancel_approved", content=f"取消申请已批准" + (f"：{reason}" if reason else "")))
        msg = "取消申请已批准"
    elif action == "reject":
        order.status = OrderStatus.DISPATCHED.value
        db.add(WorkOrderLog(order_id=order_id, action="cancel_rejected", content=f"取消申请已驳回" + (f"：{reason}" if reason else "")))
        msg = "取消申请已驳回，继续派单"
    else:
        raise HTTPException(400, "无效操作")

    db.commit()
    return ApiResponse(message=msg)


@router.post("/{order_id}/transfer")
def transfer_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    """转单：把工单转给另一位师傅（管理员或师傅本人操作）"""
    new_tech_id = data.get("technician_id")
    if not new_tech_id:
        raise HTTPException(400, "请指定目标师傅ID")

    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.status not in [OrderStatus.DISPATCHED.value, OrderStatus.ACCEPTED.value, OrderStatus.IN_PROGRESS.value]:
        raise HTTPException(400, f"当前状态「{order.status}」不可转单")

    old_tech_id = order.technician_id
    old_tech = db.query(User).filter(User.id == old_tech_id).first() if old_tech_id else None

    new_tech = db.query(User).filter(
        User.id == new_tech_id,
        User.role == "technician",
        User.status == "active",
    ).first()
    if not new_tech:
        raise HTTPException(400, "指定的师傅不存在或已禁用")

    reason = data.get("reason", "")

    # 转单
    order.technician_id = new_tech_id
    # 如果是在已接单或已派单状态，保持状态不变
    if order.status == OrderStatus.IN_PROGRESS.value:
        order.status = OrderStatus.ACCEPTED.value  # 转给新师傅后需要新师傅重新开始服务

    # 记录日志
    log_content = f"转单：从 {old_tech.name if old_tech else '未指派'} 转给 {new_tech.name}"
    if reason:
        log_content += f"（原因：{reason}）"
    db.add(WorkOrderLog(order_id=order_id, action="transfer", content=log_content))

    # 通知新师傅
    create_notification(
        db, user_id=new_tech_id,
        type="order_dispatch",
        title="收到转单",
        content=f"您收到转单 #{order.order_no}，请及时查看处理",
        ref_id=order_id, ref_type="order",
    )
    # 通知原师傅（如果之前有指派）
    if old_tech_id and old_tech_id != new_tech_id:
        create_notification(
            db, user_id=old_tech_id,
            type="order_status",
            title="工单已转出",
            content=f"工单 #{order.order_no} 已转给 {new_tech.name}",
            ref_id=order_id, ref_type="order",
        )

    db.commit()

    # WebSocket推送（后台线程）
    try:
        threading.Thread(
            target=lambda: asyncio.run(ws_send(
                new_tech_id, "order_dispatch",
                "收到转单",
                f"您收到转单 #{order.order_no}，请及时查看处理",
                order_id, "order",
            )),
            daemon=True,
        ).start()
    except Exception:
        pass

    return ApiResponse(message=f"已转单给 {new_tech.name}")
