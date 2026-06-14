from sqlalchemy import Column, Integer, String, DateTime, func

from database import Base


class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    phone = Column(String(20), nullable=False, index=True)
    address = Column(String(200), nullable=True)
    city = Column(String(50), nullable=True)
    total_orders = Column(Integer, default=0)
    remark = Column(String(500), nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
