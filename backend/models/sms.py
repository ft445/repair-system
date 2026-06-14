from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func

from database import Base


class SmsLog(Base):
    """短信发送记录"""
    __tablename__ = "sms_logs"

    id = Column(Integer, primary_key=True, index=True)
    phone = Column(String(20), nullable=False)
    template = Column(String(50), nullable=False)
    params = Column(String(500), nullable=True)
    status = Column(String(20), default="sent")  # sent / failed
    created_at = Column(DateTime, server_default=func.now())
