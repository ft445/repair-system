import asyncio
import threading
from datetime import date, datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional

from database import get_db
from models import User, TechnicianAttendance, LeaveRequest, TechnicianLocation, TechnicianLocationLog, WorkOrder, OrderStatus, Notification
from schemas import ApiResponse
from routers.ws import send_notification as ws_send
from routers.notifications import create_notification

router = APIRouter(prefix="/api/attendance", tags=["考勤管理"])


# ─── 打卡 ───

@router.post("/clock-in")
def clock_in(data: dict, db: Session = Depends(get_db)):
    """上班打卡"""
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(400, "缺少 user_id")

    today = date.today()
    now = datetime.now()

    # 检查今日是否已打卡
    existing = db.query(TechnicianAttendance).filter(
        TechnicianAttendance.user_id == user_id,
        TechnicianAttendance.date == today,
    ).first()

    if existing:
        if existing.clock_in:
            raise HTTPException(400, "今日已打卡，不能重复打卡")
        existing.clock_in = now
    else:
        late = now.hour > 9 or (now.hour == 9 and now.minute > 0)
        att = TechnicianAttendance(
            user_id=user_id,
            date=today,
            clock_in=now,
            status="late" if late else "present",
            clock_in_addr=data.get("address", ""),
        )
        db.add(att)

    db.commit()
    return ApiResponse(message="打卡成功")


@router.post("/clock-out")
def clock_out(data: dict, db: Session = Depends(get_db)):
    """下班打卡"""
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(400, "缺少 user_id")

    today = date.today()
    now = datetime.now()

    att = db.query(TechnicianAttendance).filter(
        TechnicianAttendance.user_id == user_id,
        TechnicianAttendance.date == today,
    ).first()

    if not att:
        raise HTTPException(400, "今日未打卡上班")
    if att.clock_out:
        raise HTTPException(400, "今日已打下班卡")

    att.clock_out = now
    db.commit()
    return ApiResponse(message="下班打卡成功")


@router.get("/today")
def today_status(
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """今日考勤状态"""
    today = date.today()

    if user_id:
        att = db.query(TechnicianAttendance).filter(
            TechnicianAttendance.user_id == user_id,
            TechnicianAttendance.date == today,
        ).first()
        items = [{
            "id": att.id, "user_id": att.user_id,
            "clock_in": str(att.clock_in) if att.clock_in else None,
            "clock_out": str(att.clock_out) if att.clock_out else None,
            "status": att.status, "date": str(att.date),
        }] if att else []
    else:
        atts = db.query(TechnicianAttendance).filter(
            TechnicianAttendance.date == today,
        ).all()
        items = []
        for att in atts:
            user = db.query(User).filter(User.id == att.user_id).first()
            items.append({
                "id": att.id, "user_id": att.user_id,
                "user_name": user.name if user else "-",
                "clock_in": str(att.clock_in) if att.clock_in else None,
                "clock_out": str(att.clock_out) if att.clock_out else None,
                "status": att.status, "date": str(att.date),
            })

    # 今日请假
    leaves_today = db.query(LeaveRequest).filter(
        LeaveRequest.start_date <= today,
        LeaveRequest.end_date >= today,
        LeaveRequest.status == "approved",
    )
    if user_id:
        leaves_today = leaves_today.filter(LeaveRequest.user_id == user_id)
    leaves_today = leaves_today.all()

    return ApiResponse(data={
        "attendances": items,
        "on_leave_count": len(leaves_today),
    })


# ─── 请假 ───

@router.post("/leave")
def apply_leave(data: dict, db: Session = Depends(get_db)):
    """申请请假"""
    user_id = data.get("user_id")
    if not user_id:
        raise HTTPException(400, "缺少 user_id")

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "用户不存在")

    leave_type = data.get("type", "other")
    start_date_str = data.get("start_date")
    end_date_str = data.get("end_date")

    if not start_date_str or not end_date_str:
        raise HTTPException(400, "请选择日期")

    try:
        start = date.fromisoformat(start_date_str)
        end = date.fromisoformat(end_date_str)
    except:
        raise HTTPException(400, "日期格式错误")

    if end < start:
        raise HTTPException(400, "结束日期不能早于开始日期")

    days = (end - start).days + 1

    leave = LeaveRequest(
        user_id=user_id,
        type=leave_type,
        start_date=start,
        end_date=end,
        days=days,
        reason=data.get("reason", ""),
        status="pending",
    )
    db.add(leave)
    db.commit()
    db.refresh(leave)
    return ApiResponse(data={"id": leave.id}, message="请假申请已提交")


@router.get("/leaves")
def list_leaves(
    status: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    """请假列表"""
    q = db.query(LeaveRequest).order_by(LeaveRequest.created_at.desc())
    if status:
        q = q.filter(LeaveRequest.status == status)
    if user_id:
        q = q.filter(LeaveRequest.user_id == user_id)

    items = q.all()
    result = []
    for lv in items:
        user = db.query(User).filter(User.id == lv.user_id).first()
        approver = db.query(User).filter(User.id == lv.approver_id).first() if lv.approver_id else None
        result.append({
            "id": lv.id,
            "user_id": lv.user_id,
            "user_name": user.name if user else "-",
            "type": lv.type,
            "start_date": str(lv.start_date),
            "end_date": str(lv.end_date),
            "days": lv.days,
            "reason": lv.reason,
            "status": lv.status,
            "approver_name": approver.name if approver else None,
            "reject_reason": lv.reject_reason,
            "created_at": str(lv.created_at) if lv.created_at else None,
        })
    return ApiResponse(data=result)


@router.put("/leaves/{leave_id}/review")
def review_leave(leave_id: int, data: dict, db: Session = Depends(get_db)):
    """审核请假"""
    leave = db.query(LeaveRequest).filter(LeaveRequest.id == leave_id).first()
    if not leave:
        raise HTTPException(404, "申请不存在")
    if leave.status != "pending":
        raise HTTPException(400, "该申请已处理")

    action = data.get("action", "approve")
    reviewer_id = data.get("reviewer_id")

    if action == "approve":
        leave.status = "approved"
    elif action == "reject":
        leave.status = "rejected"
        leave.reject_reason = data.get("reason", "")
    else:
        raise HTTPException(400, "无效操作")

    leave.approver_id = reviewer_id
    db.commit()

    # 通知师傅
    try:
        action_text = "批准" if action == "approve" else "驳回"
        reason_text = leave.reject_reason if action == "reject" else ""
        content = f"您的请假申请已被{action_text}"
        if reason_text:
            content += f"（原因：{reason_text}）"
        n = create_notification(
            db, user_id=leave.user_id,
            type="leave_review",
            title=f"请假{action_text}",
            content=content,
            ref_id=leave_id, ref_type="leave",
        )
        db.commit()
        threading.Thread(
            target=lambda: asyncio.run(ws_send(
                leave.user_id, "leave_review",
                f"请假{action_text}",
                content,
                leave_id, "leave",
            )),
            daemon=True,
        ).start()
    except Exception:
        pass

    return ApiResponse(message="已" + ("批准" if action == "approve" else "驳回"))


# ─── 定位 ───

@router.post("/location")
def update_location(data: dict, db: Session = Depends(get_db)):
    """更新师傅位置"""
    user_id = data.get("user_id")
    latitude = data.get("latitude")
    longitude = data.get("longitude")
    if not user_id or not latitude or not longitude:
        raise HTTPException(400, "缺少位置信息")

    existing = db.query(TechnicianLocation).filter(
        TechnicianLocation.user_id == user_id,
    ).first()

    if existing:
        existing.latitude = str(latitude)
        existing.longitude = str(longitude)
        existing.address = data.get("address", "")
        existing.accuracy = data.get("accuracy", "")
    else:
        loc = TechnicianLocation(
            user_id=user_id,
            latitude=str(latitude),
            longitude=str(longitude),
            address=data.get("address", ""),
            accuracy=data.get("accuracy", ""),
        )
        db.add(loc)

    # 写日志
    log = TechnicianLocationLog(
        user_id=user_id,
        latitude=str(latitude),
        longitude=str(longitude),
        address=data.get("address", ""),
    )
    db.add(log)
    db.commit()
    return ApiResponse(message="位置已更新")


@router.get("/locations")
def get_locations(user_id: Optional[int] = Query(None), db: Session = Depends(get_db)):
    """获取师傅当前位置"""
    q = db.query(
        TechnicianLocation, User.name, User.phone
    ).join(User, TechnicianLocation.user_id == User.id)
    if user_id:
        q = q.filter(TechnicianLocation.user_id == user_id)

    items = q.all()
    result = []
    for loc, name, phone in items:
        result.append({
            "user_id": loc.user_id,
            "name": name,
            "phone": phone,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "address": loc.address,
            "updated_at": str(loc.updated_at) if loc.updated_at else None,
        })

    return ApiResponse(data=result)
