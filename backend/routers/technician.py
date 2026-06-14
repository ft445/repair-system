from datetime import datetime, date
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, asc
from typing import Optional
from database import get_db
from models import WorkOrder, WorkOrderLog, Customer, User, ServiceItem, OrderStatus, PayStatus, TechnicianSkill, TechnicianWallet, TechnicianLocation, DepositRequest, LeaveRequest, TechnicianAttendance
from schemas import WorkOrderOut, ApiResponse

router = APIRouter(prefix="/api/technician", tags=["师傅端"])


def enrich(order, db):
    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if customer:
        order.customer_name = customer.name
        order.customer_phone = customer.phone
    item = db.query(ServiceItem).filter(ServiceItem.id == order.service_item_id).first()
    if item:
        order.service_item_name = item.name
    return order


@router.get("/list")
def list_technicians(db: Session = Depends(get_db)):
    """师傅列表（含技能、钱包、业绩统计）"""
    users = db.query(User).filter(User.role == "technician").order_by(User.created_at.desc()).all()
    result = []
    for u in users:
        # 技能
        skills = db.query(TechnicianSkill).filter(
            TechnicianSkill.user_id == u.id,
            TechnicianSkill.status == "active",
        ).all()
        skill_list = []
        for s in skills:
            item = db.query(ServiceItem).filter(ServiceItem.id == s.service_item_id).first()
            skill_list.append({
                "id": s.id,
                "service_item_id": s.service_item_id,
                "service_name": item.name if item else "-",
                "level": s.level,
                "price": s.price,
            })

        # 钱包
        wallet = db.query(TechnicianWallet).filter(TechnicianWallet.user_id == u.id).first()

        # 业绩统计
        total_orders = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.technician_id == u.id,
        ).scalar() or 0
        completed_orders = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.technician_id == u.id,
            WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.DONE.value]),
        ).scalar() or 0
        in_progress = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.technician_id == u.id,
            WorkOrder.status.in_([OrderStatus.DISPATCHED.value, OrderStatus.ACCEPTED.value, OrderStatus.IN_PROGRESS.value]),
        ).scalar() or 0

        # 当月完成
        month_start = date.today().replace(day=1)
        month_orders = db.query(func.count(WorkOrder.id)).filter(
            WorkOrder.technician_id == u.id,
            WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.DONE.value]),
            func.date(WorkOrder.completed_at) >= month_start,
        ).scalar() or 0

        # 评分（取工单评价平均值）
        avg_rating = db.query(func.avg(WorkOrder.rating)).filter(
            WorkOrder.technician_id == u.id,
            WorkOrder.rating.isnot(None),
        ).scalar()

        # 定位
        location = db.query(TechnicianLocation).filter(
            TechnicianLocation.user_id == u.id,
        ).first()

        result.append({
            "id": u.id,
            "name": u.name,
            "phone": u.phone,
            "org_id": u.org_id,
            "avatar": u.avatar,
            "status": u.status,
            "id_card": u.id_card,
            "address": u.address,
            "emergency_contact": u.emergency_contact,
            "emergency_phone": u.emergency_phone,
            "hire_date": u.hire_date,
            "location": {
                "latitude": location.latitude,
                "longitude": location.longitude,
                "address": location.address,
                "updated_at": str(location.updated_at) if location.updated_at else None,
            } if location else None,
            "created_at": str(u.created_at) if u.created_at else None,
            "skills": skill_list,
            "wallet": {
                "balance": wallet.balance if wallet else 0,
                "frozen": wallet.frozen if wallet else 0,
                "total_earned": wallet.total_earned if wallet else 0,
            } if wallet else None,
            "stats": {
                "total_orders": total_orders,
                "completed_orders": completed_orders,
                "in_progress": in_progress,
                "month_orders": month_orders,
                "avg_rating": round(float(avg_rating), 1) if avg_rating else None,
            },
        })

    return ApiResponse(data=result)


@router.get("/{tech_id}/skills")
def get_technician_skills(tech_id: int, db: Session = Depends(get_db)):
    """获取师傅技能列表"""
    user = db.query(User).filter(User.id == tech_id, User.role == "technician").first()
    if not user:
        raise HTTPException(404, "师傅不存在")

    skills = db.query(TechnicianSkill).filter(
        TechnicianSkill.user_id == tech_id,
        TechnicianSkill.status == "active",
    ).all()

    result = []
    for s in skills:
        item = db.query(ServiceItem).filter(ServiceItem.id == s.service_item_id).first()
        result.append({
            "id": s.id,
            "service_item_id": s.service_item_id,
            "service_name": item.name if item else "-",
            "level": s.level,
            "price": s.price,
        })
    return ApiResponse(data=result)


@router.post("/{tech_id}/skills")
def add_technician_skill(tech_id: int, data: dict, db: Session = Depends(get_db)):
    """添加师傅技能"""
    user = db.query(User).filter(User.id == tech_id, User.role == "technician").first()
    if not user:
        raise HTTPException(404, "师傅不存在")

    service_item_id = data.get("service_item_id")
    if not service_item_id:
        raise HTTPException(400, "请选择服务项目")

    item = db.query(ServiceItem).filter(ServiceItem.id == service_item_id).first()
    if not item:
        raise HTTPException(404, "服务项目不存在")

    # 去重检查
    existing = db.query(TechnicianSkill).filter(
        TechnicianSkill.user_id == tech_id,
        TechnicianSkill.service_item_id == service_item_id,
        TechnicianSkill.status == "active",
    ).first()
    if existing:
        raise HTTPException(400, "该技能已存在")

    skill = TechnicianSkill(
        user_id=tech_id,
        service_item_id=service_item_id,
        level=data.get("level", "junior"),
        price=data.get("price"),
    )
    db.add(skill)
    db.commit()
    db.refresh(skill)
    return ApiResponse(data={"id": skill.id}, message="技能已添加")


@router.put("/skills/{skill_id}")
def update_technician_skill(skill_id: int, data: dict, db: Session = Depends(get_db)):
    """更新师傅技能"""
    skill = db.query(TechnicianSkill).filter(TechnicianSkill.id == skill_id).first()
    if not skill:
        raise HTTPException(404, "技能记录不存在")

    if "level" in data:
        skill.level = data["level"]
    if "price" in data:
        skill.price = data["price"]
    db.commit()
    return ApiResponse(message="技能已更新")


@router.delete("/skills/{skill_id}")
def delete_technician_skill(skill_id: int, db: Session = Depends(get_db)):
    """删除师傅技能"""
    skill = db.query(TechnicianSkill).filter(TechnicianSkill.id == skill_id).first()
    if not skill:
        raise HTTPException(404, "技能记录不存在")

    skill.status = "inactive"
    db.commit()
    return ApiResponse(message="技能已删除")


@router.get("/orders")
def my_orders(
    technician_id: int = Query(..., description="师傅ID"),
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(100, ge=1, le=200, description="每页条数"),
    db: Session = Depends(get_db),
):
    """师傅查看自己的工单（支持分页）"""
    q = db.query(WorkOrder).filter(WorkOrder.technician_id == technician_id)
    if status:
        q = q.filter(WorkOrder.status == status)
    total = q.count()
    orders = q.order_by(WorkOrder.created_at.desc()) \
              .offset((page - 1) * page_size) \
              .limit(page_size) \
              .all()
    return ApiResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [WorkOrderOut.model_validate(enrich(o, db)) for o in orders],
    })


@router.get("/stats/monthly")
def monthly_stats(
    technician_id: int = Query(..., description="师傅ID"),
    db: Session = Depends(get_db),
):
    """师傅月度统计（用于APP收入页）"""
    now = date.today()
    month_start = now.replace(day=1)
    month_end = now

    # 当月完成工单
    month_orders = db.query(WorkOrder).filter(
        WorkOrder.technician_id == technician_id,
        WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.PAID.value, OrderStatus.DONE.value]),
        func.date(WorkOrder.completed_at) >= month_start,
        func.date(WorkOrder.completed_at) <= month_end,
    ).all()

    month_income = sum((o.total_fee or 0) for o in month_orders)
    month_count = len(month_orders)

    # 评分
    avg_rating = db.query(func.avg(WorkOrder.rating)).filter(
        WorkOrder.technician_id == technician_id,
        WorkOrder.rating.isnot(None),
    ).scalar()

    # 排名（当月完成数在所有师傅中的位置）
    rank_sub = db.query(
        WorkOrder.technician_id,
        func.count(WorkOrder.id).label("cnt"),
    ).filter(
        WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.PAID.value, OrderStatus.DONE.value]),
        func.date(WorkOrder.completed_at) >= month_start,
        func.date(WorkOrder.completed_at) <= month_end,
    ).group_by(WorkOrder.technician_id).subquery()

    my_count = db.query(func.count()).filter(
        rank_sub.c.technician_id == technician_id,
    ).scalar() or 0

    higher_count = db.query(func.count()).filter(
        rank_sub.c.cnt > month_count,
    ).scalar() or 0

    total_techs = db.query(func.count()).filter(
        rank_sub.c.technician_id.isnot(None),
    ).scalar() or 0

    return ApiResponse(data={
        "month_income": round(month_income, 2),
        "month_orders": month_count,
        "avg_rating": round(float(avg_rating), 1) if avg_rating else None,
        "rank": higher_count + 1 if total_techs > 0 else 1,
        "total_techs": total_techs,
    })


@router.get("/{tech_id}/schedule")
def technician_schedule(
    tech_id: int,
    start_date: str = Query(..., description="开始日期 YYYY-MM-DD"),
    end_date: str = Query(..., description="结束日期 YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    """师傅日程（按日期范围查询预约工单）"""
    orders = db.query(WorkOrder).filter(
        WorkOrder.technician_id == tech_id,
        WorkOrder.appointment_time.isnot(None),
        func.date(WorkOrder.appointment_time) >= start_date,
        func.date(WorkOrder.appointment_time) <= end_date,
        WorkOrder.status.notin_([OrderStatus.CANCELLED.value]),
    ).order_by(asc(WorkOrder.appointment_time)).all()

    result = []
    for o in orders:
        enriched = enrich(o, db)
        day = str(o.appointment_time.date()) if o.appointment_time else None
        result.append({
            "id": o.id,
            "order_no": o.order_no,
            "day": day,
            "time": str(o.appointment_time.time())[:5] if o.appointment_time else "",
            "service_item_name": getattr(enriched, "service_item_name", None),
            "customer_name": getattr(enriched, "customer_name", None),
            "address": o.address,
            "status": o.status,
        })

    # 按日期分组
    from collections import defaultdict
    grouped = defaultdict(list)
    for item in result:
        if item["day"]:
            grouped[item["day"]].append(item)

    return ApiResponse(data={
        "items": result,
        "grouped": dict(grouped),
        "total": len(result),
    })


@router.get("/customers/{customer_id}/history")
def customer_order_history(
    customer_id: int,
    technician_id: int = Query(..., description="当前师傅ID"),
    db: Session = Depends(get_db),
):
    """客户历史工单（仅显示当前师傅服务过的该客户的工单）"""
    orders = db.query(WorkOrder).filter(
        WorkOrder.customer_id == customer_id,
        WorkOrder.technician_id == technician_id,
    ).order_by(WorkOrder.created_at.desc()).limit(10).all()

    return ApiResponse(data=[WorkOrderOut.model_validate(enrich(o, db)) for o in orders])


@router.get("/nearby")
def nearby_orders(technician_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """附近可接单（待派单池），传 technician_id 则按技能过滤"""
    q = db.query(WorkOrder).filter(WorkOrder.status == OrderStatus.PENDING.value)
    if technician_id:
        skill_ids = db.query(TechnicianSkill.service_item_id).filter(
            TechnicianSkill.user_id == technician_id,
            TechnicianSkill.status == "active",
        ).subquery()
        q = q.filter(WorkOrder.service_item_id.in_(skill_ids))
    orders = q.order_by(WorkOrder.created_at.desc()).limit(50).all()
    return ApiResponse(data=[WorkOrderOut.model_validate(enrich(o, db)) for o in orders])


@router.post("/orders/{order_id}/accept")
def accept_order(order_id: int, data: dict = {}, db: Session = Depends(get_db), technician_id: Optional[int] = Query(None)):
    """师傅接单"""
    if not technician_id:
        technician_id = data.get("technician_id")
    if not technician_id:
        raise HTTPException(400, "缺少 technician_id")

    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.technician_id != technician_id:
        raise HTTPException(403, "非指派给你的工单")
    if order.status != OrderStatus.DISPATCHED.value:
        raise HTTPException(400, f"当前状态不可接单（{order.status}）")

    order.status = OrderStatus.ACCEPTED.value
    db.add(WorkOrderLog(
        order_id=order_id, user_id=technician_id,
        action="accept", content="师傅已接单",
    ))
    db.commit()
    return ApiResponse(message="接单成功")


@router.post("/orders/{order_id}/start")
def start_service(order_id: int, data: dict, db: Session = Depends(get_db)):
    """开始服务"""
    technician_id = data.get("technician_id")
    if not technician_id:
        raise HTTPException(400, "缺少 technician_id")

    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order or order.technician_id != technician_id:
        raise HTTPException(404, "工单不存在")

    allowed = [OrderStatus.ACCEPTED.value]
    if order.status not in allowed:
        raise HTTPException(400, f"当前状态不可开始服务（{order.status}）")

    order.status = OrderStatus.IN_PROGRESS.value
    db.add(WorkOrderLog(order_id=order_id, user_id=technician_id, action="start", content="开始服务"))
    db.commit()
    return ApiResponse(message="已开始服务")


@router.post("/orders/{order_id}/complete")
def complete_order(
    order_id: int,
    data: dict,
    db: Session = Depends(get_db),
):
    """完工回单（师傅提交完工信息）"""
    technician_id = data.get("technician_id")
    if not technician_id:
        raise HTTPException(400, "缺少 technician_id")

    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order or order.technician_id != technician_id:
        raise HTTPException(404, "工单不存在")

    if order.status not in [OrderStatus.IN_PROGRESS.value, OrderStatus.ACCEPTED.value]:
        raise HTTPException(400, f"当前状态不可完工（{order.status}）")

    order.status = OrderStatus.COMPLETED.value
    if "material_fee" in data:
        order.material_fee = data["material_fee"]
    if "service_fee" in data:
        order.service_fee = data["service_fee"]
    if "total_fee" in data:
        order.total_fee = data["total_fee"]
    order.before_photos = data.get("before_photos")
    order.after_photos = data.get("after_photos")
    order.video_url = data.get("video_url")
    order.audio_url = data.get("audio_url")
    order.customer_signature = data.get("customer_signature")
    order.completed_at = func.now()

    db.add(WorkOrderLog(
        order_id=order_id, user_id=technician_id,
        action="complete", content=f"完工，总价¥{data.get('total_fee', 0)}",
    ))
    db.commit()
    return ApiResponse(message="完工提交成功")


@router.post("/orders/{order_id}/reject")
def reject_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    """师傅拒单 — 自动判断是否重新派单"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.status not in (OrderStatus.PENDING.value, OrderStatus.DISPATCHED.value, OrderStatus.ACCEPTED.value):
        raise HTTPException(400, "当前状态不可取消")

    reason = data.get("reason", "师傅拒单")
    db.add(WorkOrderLog(order_id=order_id, action="reject", content=f"师傅申请取消: {reason}"))

    # 检查自动派单开关
    from sqlalchemy import text as sa_text
    auto_row = db.execute(sa_text("SELECT value FROM system_settings WHERE key = 'auto_dispatch_enabled'")).fetchone()
    auto_dispatch_on = auto_row and auto_row[0] == '1'

    if auto_dispatch_on:
        # 自动派单：退回已接单状态，重新评分派给最优师傅
        order.status = OrderStatus.ACCEPTED.value
        order.technician_id = None
        db.flush()

        techs = db.query(User).filter(User.role == "technician", User.status == "active").all()
        best_tech, best_score = None, -999
        today = date.today()

        for tech in techs:
            skill = db.query(TechnicianSkill).filter(
                TechnicianSkill.user_id == tech.id,
                TechnicianSkill.service_item_id == order.service_item_id,
                TechnicianSkill.status == "active",
            ).first()
            if not skill:
                continue
            score = 10
            if skill.level == "senior": score += 5
            elif skill.level == "medium": score += 3

            active_cnt = db.query(func.count(WorkOrder.id)).filter(
                WorkOrder.technician_id == tech.id,
                WorkOrder.status.in_([OrderStatus.DISPATCHED.value, OrderStatus.ACCEPTED.value, OrderStatus.IN_PROGRESS.value]),
            ).scalar() or 0
            score -= active_cnt * 2

            total_done = db.query(func.count(WorkOrder.id)).filter(
                WorkOrder.technician_id == tech.id,
                WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.DONE.value]),
            ).scalar() or 0
            score += min(total_done, 5)

            on_leave = db.query(LeaveRequest).filter(
                LeaveRequest.user_id == tech.id,
                LeaveRequest.start_date <= today,
                LeaveRequest.end_date >= today,
                LeaveRequest.status == "approved",
            ).first()
            if on_leave: score -= 100

            clocked_in = db.query(TechnicianAttendance).filter(
                TechnicianAttendance.user_id == tech.id,
                TechnicianAttendance.date == today,
            ).first()
            if clocked_in: score += 2

            if score > best_score:
                best_score, best_tech = score, tech

        if best_tech:
            order.technician_id = best_tech.id
            order.status = OrderStatus.DISPATCHED.value
            db.add(WorkOrderLog(order_id=order_id, action="auto_dispatch", content=f"师傅拒单后自动派单给 {best_tech.name} (得分:{best_score})"))
            db.commit()
            return ApiResponse(message=f"已自动重新派单给 {best_tech.name}")
        else:
            order.status = OrderStatus.CANCEL_PENDING.value
            db.commit()
            return ApiResponse(message="暂无可用师傅，已转入待审核")
    else:
        # 手动模式：进入待审核，等待管理员手动处理
        order.status = OrderStatus.CANCEL_PENDING.value
        db.commit()
        return ApiResponse(message="已提交取消申请，待管理员审核")


@router.post("/orders/{order_id}/verify-customer")
def verify_customer(order_id: int, data: dict, db: Session = Depends(get_db)):
    """验证客户手机尾号4位"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    customer = db.query(Customer).filter(Customer.id == order.customer_id).first()
    if not customer:
        raise HTTPException(400, "找不到客户信息")

    input_tail = data.get("phone_tail", "")
    real_tail = customer.phone[-4:] if customer.phone else ""

    if input_tail != real_tail:
        raise HTTPException(400, "手机尾号不正确")

    db.add(WorkOrderLog(order_id=order_id, action="verify", content="客户验证通过"))
    db.commit()
    return ApiResponse(message="验证通过")


@router.post("/orders/{order_id}/rate")
def rate_order(order_id: int, data: dict, db: Session = Depends(get_db)):
    """客户评价"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")

    order.rating = data.get("rating", 5)
    order.comment = data.get("comment", "")
    db.add(WorkOrderLog(order_id=order_id, action="rate", content=f"客户评分: {order.rating}星" + (f" {order.comment}" if order.comment else "")))
    db.commit()
    return ApiResponse(message="评价成功")


@router.post("/orders/{order_id}/mark-paid")
def mark_paid(order_id: int, data: dict, db: Session = Depends(get_db)):
    """师傅标记已收款"""
    order = db.query(WorkOrder).filter(WorkOrder.id == order_id).first()
    if not order:
        raise HTTPException(404, "工单不存在")
    if order.status not in (OrderStatus.COMPLETED.value, OrderStatus.PAID.value):
        raise HTTPException(400, "仅已完成工单可标记收款")

    method = data.get("payment_method", "cash")
    order.pay_status = PayStatus.PAID.value
    order.payment_method = method
    order.paid_at = func.now()
    order.status = OrderStatus.PAID.value

    method_names = {"cash": "现金", "wechat": "微信", "alipay": "支付宝", "transfer": "转账"}
    method_name = method_names.get(method, method)

    # 扣除平台佣金（从师傅保证金/余额中扣）
    total = order.total_fee or order.service_fee or 0
    if total > 0 and order.technician_id:
        from sqlalchemy import text
        row = db.execute(text("SELECT value FROM system_settings WHERE key = 'commission_rate'")).fetchone()
        commission_rate = int(row[0]) if row else 80  # 默认师傅得80%
        platform_fee = round(total * (100 - commission_rate) / 100, 2)
        if platform_fee > 0:
            wallet = db.query(TechnicianWallet).filter(TechnicianWallet.user_id == order.technician_id).first()
            if wallet:
                wallet.balance = max(0, (wallet.balance or 0) - platform_fee)
                wallet.total_earned = (wallet.total_earned or 0) + (total - platform_fee)
                db.add(WorkOrderLog(
                    order_id=order_id, action="commission",
                    content=f"平台抽成 {platform_fee}元（费率{100-commission_rate}%），师傅收入 {total-platform_fee}元",
                ))

    db.add(WorkOrderLog(
        order_id=order_id, action="paid",
        content=f"师傅标记已收款，方式: {method_name}",
    ))
    db.commit()
    return ApiResponse(message=f"已标记{method_name}收款")


@router.get("/deposit/{tech_id}")
def get_deposit(tech_id: int, db: Session = Depends(get_db)):
    """获取师傅当前保证金（钱包余额）"""
    wallet = db.query(TechnicianWallet).filter(TechnicianWallet.user_id == tech_id).first()
    deposit = wallet.balance if wallet else 0
    return ApiResponse(data={"deposit": deposit, "frozen": wallet.frozen if wallet else 0})


@router.post("/deposit/{tech_id}")
def pay_deposit(tech_id: int, data: dict, db: Session = Depends(get_db)):
    """师傅充值保证金（提交申请，管理员审核后到账）"""
    amount = data.get("amount", 0)
    if not amount or amount <= 0:
        raise HTTPException(400, "金额无效")

    req = DepositRequest(user_id=tech_id, amount=amount, status="pending")
    db.add(req)
    db.commit()
    return ApiResponse(message=f"充值申请已提交，等待管理员审核", data={"request_id": req.id, "amount": amount})


@router.get("/deposit-requests")
def list_deposit_requests(
    status: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """保证金申请列表（管理员）"""
    q = db.query(DepositRequest)
    if status:
        q = q.filter(DepositRequest.status == status)
    total = q.count()
    items = q.order_by(DepositRequest.created_at.desc()).offset((page-1)*page_size).limit(page_size).all()
    result = []
    for r in items:
        user = db.query(User).filter(User.id == r.user_id).first()
        reviewer = db.query(User).filter(User.id == r.reviewer_id).first() if r.reviewer_id else None
        result.append({
            "id": r.id, "user_id": r.user_id, "tech_name": user.name if user else "-",
            "tech_phone": user.phone if user else "",
            "amount": r.amount, "status": r.status, "remark": r.note,
            "reviewer_name": reviewer.name if reviewer else None,
            "created_at": str(r.created_at)[:19] if r.created_at else None,
            "reviewed_at": str(r.reviewed_at)[:19] if r.reviewed_at else None,
        })
    return ApiResponse(data={"total": total, "items": result})


@router.get("/deposit-requests/pending-count")
def pending_deposit_count(db: Session = Depends(get_db)):
    """待审核保证金数量"""
    count = db.query(DepositRequest).filter(DepositRequest.status == "pending").count()
    return ApiResponse(data={"count": count})


@router.post("/deposit-requests/{req_id}/review")
def review_deposit(req_id: int, data: dict, db: Session = Depends(get_db)):
    """审核保证金申请"""
    req = db.query(DepositRequest).filter(DepositRequest.id == req_id).first()
    if not req:
        raise HTTPException(404, "申请不存在")
    if req.status != "pending":
        raise HTTPException(400, "该申请已处理")

    action = data.get("action", "approve")
    note = data.get("note", "")
    reviewer_id = data.get("reviewer_id")

    if action == "approve":
        req.status = "approved"
        wallet = db.query(TechnicianWallet).filter(TechnicianWallet.user_id == req.user_id).first()
        if not wallet:
            wallet = TechnicianWallet(user_id=req.user_id, balance=0, frozen=0, total_earned=0)
            db.add(wallet)
            db.flush()
        wallet.balance = (wallet.balance or 0) + req.amount
        msg = f"¥{req.amount} 保证金已审核通过"
    elif action == "reject":
        req.status = "rejected"
        msg = "保证金申请已驳回"
    else:
        raise HTTPException(400, "无效操作")

    req.reviewer_id = reviewer_id
    req.note = note
    req.reviewed_at = func.now()
    db.commit()
    return ApiResponse(message=msg)
