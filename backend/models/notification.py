from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, func

from database import Base


class Notification(Base):
    """消息通知"""
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True, nullable=False, comment="接收人ID")
    type = Column(String(30), nullable=False, comment="通知类型: order_dispatch/order_status/leave_review/withdraw_review/deposit_review/system")
    title = Column(String(200), nullable=False, comment="标题")
    content = Column(Text, nullable=True, comment="内容")
    ref_id = Column(Integer, nullable=True, comment="关联ID（工单ID/请假ID等）")
    ref_type = Column(String(30), nullable=True, comment="关联类型: order/leave/withdraw/deposit")
    is_read = Column(Boolean, default=False, comment="是否已读")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
