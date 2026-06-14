"""
消息通知系统
师傅APP通知中心的后端支持
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import Optional

from database import get_db
from models import Notification
from schemas import ApiResponse
from utils.auth import get_current_user

router = APIRouter(prefix="/api/notifications", tags=["消息通知"])


@router.get("")
def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: Optional[bool] = Query(False),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取当前用户的通知列表（分页）"""
    q = db.query(Notification).filter(Notification.user_id == current_user.id)
    if unread_only:
        q = q.filter(Notification.is_read == False)

    total = q.count()
    items = q.order_by(desc(Notification.created_at)) \
             .offset((page - 1) * page_size) \
             .limit(page_size) \
             .all()

    return ApiResponse(data={
        "total": total,
        "page": page,
        "page_size": page_size,
        "items": [{
            "id": n.id,
            "type": n.type,
            "title": n.title,
            "content": n.content,
            "ref_id": n.ref_id,
            "ref_type": n.ref_type,
            "is_read": n.is_read,
            "created_at": str(n.created_at) if n.created_at else None,
        } for n in items],
    })


@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取未读通知数量"""
    count = db.query(func.count(Notification.id)).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).scalar() or 0
    return ApiResponse(data={"count": count})


@router.put("/{notification_id}/read")
def mark_read(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """标记单条通知为已读"""
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not n:
        raise HTTPException(404, "通知不存在")
    n.is_read = True
    db.commit()
    return ApiResponse(message="已标记已读")


@router.put("/read-all")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """全部标记已读"""
    db.query(Notification).filter(
        Notification.user_id == current_user.id,
        Notification.is_read == False,
    ).update({"is_read": True})
    db.commit()
    return ApiResponse(message="已全部标记已读")


@router.delete("/{notification_id}")
def delete_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """删除通知"""
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == current_user.id,
    ).first()
    if not n:
        raise HTTPException(404, "通知不存在")
    db.delete(n)
    db.commit()
    return ApiResponse(message="已删除")


def create_notification(
    db: Session,
    user_id: int,
    type: str,
    title: str,
    content: Optional[str] = None,
    ref_id: Optional[int] = None,
    ref_type: Optional[str] = None,
) -> Notification:
    """工具函数：创建通知并写入数据库（供其他路由调用）"""
    n = Notification(
        user_id=user_id,
        type=type,
        title=title,
        content=content,
        ref_id=ref_id,
        ref_type=ref_type,
        is_read=False,
    )
    db.add(n)
    db.flush()
    db.refresh(n)
    return n
