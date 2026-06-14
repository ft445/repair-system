"""师傅入驻申请表"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Float
from database import Base
from datetime import datetime


class TechApplication(Base):
    __tablename__ = "tech_applications"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, comment="姓名")
    phone = Column(String(20), nullable=False, comment="手机号")
    age = Column(Integer, nullable=True, comment="年龄")
    skill = Column(String(200), nullable=True, comment="擅长技能")
    experience = Column(String(50), nullable=True, comment="从业经验")
    area = Column(String(100), nullable=True, comment="服务区域")
    tools = Column(String(200), nullable=True, comment="自备工具")
    status = Column(String(20), default="pending", comment="状态: pending/contacted/accepted/rejected")
    remark = Column(Text, nullable=True, comment="备注")
    created_at = Column(DateTime, default=datetime.now)
