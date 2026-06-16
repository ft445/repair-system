import enum
from sqlalchemy import Column, Integer, String, Float, Enum, DateTime, Text, ForeignKey, func, text

from database import Base


class OrderStatus(str, enum.Enum):
    PENDING = "pending"               # 待接单
    DISPATCHED = "dispatched"         # 已派单
    ACCEPTED = "accepted"             # 已接单
    IN_PROGRESS = "in_progress"       # 维修中
    COMPLETED = "completed"           # 完工待确认
    PAID = "paid"                     # 已付款
    DONE = "done"                     # 已完成（含评价）
    CANCELLED = "cancelled"           # 已取消
    CANCEL_PENDING = "CANCEL_PENDING"  # 待审核取消


class PayStatus(str, enum.Enum):
    UNPAID = "unpaid"
    PAID = "paid"
    REFUNDED = "refunded"


class WorkOrder(Base):
    """工单 - 核心表"""
    __tablename__ = "work_orders"

    id = Column(Integer, primary_key=True, index=True)
    order_no = Column(String(50), unique=True, nullable=False, comment="工单号")
    org_id = Column(Integer, nullable=True, comment="所属分公司")
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    technician_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    dispatcher_id = Column(Integer, nullable=True)

    # 服务信息
    service_item_id = Column(Integer, ForeignKey("service_items.id"), nullable=False)
    category_type = Column(String(20), nullable=False, comment="大类: repair/cleaning/家政")
    fault_description = Column(Text, nullable=True)
    images = Column(Text, nullable=True)  # JSON 图片路径数组

    # 地址信息
    address = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    # 预约信息
    appointment_time = Column(DateTime, nullable=True)

    # 状态
    status = Column(Enum(OrderStatus), default=OrderStatus.PENDING)
    source = Column(String(20), default="qrcode")  # qrcode / phone / app

    # 费用
    unit_type = Column(String(20), nullable=True)
    quantity = Column(Float, default=1)
    unit_price = Column(Float, nullable=True)
    material_fee = Column(Float, default=0)
    service_fee = Column(Float, default=0)
    total_fee = Column(Float, default=0)

    # 支付
    payment_method = Column(String(20), nullable=True)  # wechat / alipay / cash
    pay_status = Column(Enum(PayStatus), default=PayStatus.UNPAID)
    paid_at = Column(DateTime, nullable=True)

    # 评价
    rating = Column(Integer, nullable=True)
    comment = Column(Text, nullable=True)

    # 电子签名
    customer_signature = Column(Text, nullable=True)
    warranty_date = Column(DateTime, nullable=True)

    # 时间
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))
    accepted_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # 上门照片
    before_photos = Column(Text, nullable=True)
    after_photos = Column(Text, nullable=True)

    # 维修视频
    video_url = Column(String(500), nullable=True)

    # 维修录音
    audio_url = Column(String(500), nullable=True, comment="维修录音")

    # 现场报价
    quote_status = Column(String(20), nullable=True, comment="报价状态: pending/accepted/rejected")
    trip_fee = Column(Float, default=0, comment="上门费")
    trip_fee_status = Column(String(20), nullable=True, comment="上门费状态: pending/paid")
    quote_amount = Column(Float, default=0, comment="报价金额")
    quote_items = Column(Text, nullable=True, comment="报价明细JSON")
    quoted_at = Column(DateTime, nullable=True, comment="报价时间")


class WorkOrderLog(Base):
    """工单操作日志"""
    __tablename__ = "work_order_logs"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False)
    user_id = Column(Integer, nullable=True)
    user_name = Column(String(50), nullable=True)
    action = Column(String(50), nullable=False)
    content = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))
