from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, text

from database import Base


class ServiceCategory(Base):
    """业务大类：维修/保洁/清洗"""
    __tablename__ = "service_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    icon = Column(String(200), nullable=True)
    description = Column(String(200), nullable=True)
    sort_order = Column(Integer, default=0)
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))


class ServiceItem(Base):
    """服务项目：三级分类叶子节点（如 空调→加氟）"""
    __tablename__ = "service_items"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("service_categories.id"), nullable=False)
    name = Column(String(100), nullable=False)           # 项目名称
    parent_id = Column(Integer, nullable=True)           # 父级ID，支持三级分类
    level = Column(Integer, default=1)                   # 层级 1/2/3
    unit_type = Column(String(20), nullable=False)       # 计价单位：次/小时/㎡/台
    default_price = Column(Float, nullable=True)         # 默认参考价
    description = Column(String(500), nullable=True)
    status = Column(String(20), default="active")
    sort_order = Column(Integer, default=0)
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))


class TechnicianSkill(Base):
    """师傅技能关联表"""
    __tablename__ = "technician_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    service_item_id = Column(Integer, ForeignKey("service_items.id"), nullable=False)
    price = Column(Float, nullable=True)                 # 师傅自定义价格
    level = Column(String(20), default="junior")         # junior / medium / senior
    status = Column(String(20), default="active")
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))
