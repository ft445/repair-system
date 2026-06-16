from sqlalchemy import Column, Integer, String, DateTime, Date, Text, func, text
from database import Base


class TechnicianAttendance(Base):
    """师傅考勤打卡"""
    __tablename__ = "technician_attendance"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)
    clock_in = Column(DateTime, nullable=True, comment="上班打卡时间")
    clock_out = Column(DateTime, nullable=True, comment="下班打卡时间")
    clock_in_addr = Column(String(200), nullable=True, comment="打卡位置")
    status = Column(String(20), default="present", comment="present/late/absent/halfday")
    notes = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now','localtime')"), onupdate=text("datetime('now','localtime')"))


class LeaveRequest(Base):
    """请假申请"""
    __tablename__ = "leave_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    type = Column(String(20), nullable=False, comment="sick/vacation/personal/other")
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    days = Column(Integer, nullable=False, comment="请假天数")
    reason = Column(Text, nullable=True)
    status = Column(String(20), default="pending", comment="pending/approved/rejected/cancelled")
    approver_id = Column(Integer, nullable=True)
    reject_reason = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))
    updated_at = Column(DateTime, server_default=text("datetime('now','localtime')"), onupdate=text("datetime('now','localtime')"))


class TechnicianLocation(Base):
    """师傅实时定位"""
    __tablename__ = "technician_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    latitude = Column(String(30), nullable=False, comment="纬度")
    longitude = Column(String(30), nullable=False, comment="经度")
    address = Column(String(200), nullable=True, comment="位置描述")
    accuracy = Column(String(20), nullable=True, comment="精度")
    updated_at = Column(DateTime, server_default=text("datetime('now','localtime')"), onupdate=text("datetime('now','localtime')"))


class TechnicianLocationLog(Base):
    """定位历史日志"""
    __tablename__ = "technician_location_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    latitude = Column(String(30), nullable=False)
    longitude = Column(String(30), nullable=False)
    address = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))

