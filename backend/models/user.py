import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, func, text

from database import Base


class UserRole(str, enum.Enum):
    ADMIN = "admin"               # 系统管理员
    DISPATCHER = "dispatcher"     # 调度员
    TECHNICIAN = "technician"     # 维修师傅


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    org_id = Column(Integer, nullable=True, comment="所属组织ID")
    name = Column(String(50), nullable=False)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(200), nullable=False)
    role = Column(Enum(UserRole), nullable=False)
    avatar = Column(String(200), nullable=True)
    status = Column(String(20), default="active")  # active / disabled
    id_card = Column(String(20), nullable=True, comment="身份证号")
    address = Column(String(200), nullable=True, comment="住址")
    emergency_contact = Column(String(50), nullable=True, comment="紧急联系人")
    emergency_phone = Column(String(20), nullable=True, comment="紧急联系电话")
    hire_date = Column(String(20), nullable=True, comment="入职日期 YYYY-MM-DD")
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now','localtime')"), onupdate=text("datetime('now','localtime')"))
