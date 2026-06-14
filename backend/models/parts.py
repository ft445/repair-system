from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, func
from database import Base


class WorkOrderPart(Base):
    """工单配件/材料"""
    __tablename__ = "work_order_parts"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("work_orders.id"), nullable=False, index=True)
    name = Column(String(200), nullable=False, comment="配件名称")
    brand = Column(String(100), nullable=True, comment="品牌")
    model_no = Column(String(100), nullable=True, comment="型号")
    quantity = Column(Integer, default=1, comment="数量")
    unit_price = Column(Float, default=0, comment="单价")
    total_price = Column(Float, default=0, comment="总价")
    part_type = Column(String(20), default="new", comment="new=新配件 old=旧配件 other=其他")
    receipt_image = Column(String(500), nullable=True, comment="票据图片URL")
    part_photo = Column(String(500), nullable=True, comment="配件照片URL")
    notes = Column(String(500), nullable=True, comment="备注")
    store_name = Column(String(200), nullable=True, comment="购买店铺")
    store_phone = Column(String(50), nullable=True, comment="店铺电话")
    created_at = Column(DateTime, server_default=func.now())
