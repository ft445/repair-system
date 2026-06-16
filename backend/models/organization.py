import enum
from sqlalchemy import Column, Integer, String, Enum, DateTime, func, text

from database import Base


class OrgLevel(str, enum.Enum):
    HEADQUARTERS = "headquarters"  # 总部
    BRANCH = "branch"              # 分公司
    DISTRICT = "district"          # 片区


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    parent_id = Column(Integer, nullable=True)
    city = Column(String(50), nullable=True)
    address = Column(String(200), nullable=True)
    level = Column(Enum(OrgLevel), nullable=False)
    contact_phone = Column(String(20), nullable=True)
    status = Column(String(20), default="active")  # active / disabled
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now','localtime')"), onupdate=text("datetime('now','localtime')"))
