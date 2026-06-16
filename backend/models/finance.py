from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func, text

from database import Base


class TechnicianWallet(Base):
    """师傅钱包"""
    __tablename__ = "technician_wallets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    balance = Column(Float, default=0)
    frozen = Column(Float, default=0)
    total_earned = Column(Float, default=0)
    updated_at = Column(DateTime, server_default=text("datetime('now','localtime')"), onupdate=text("datetime('now','localtime')"))


class DepositRequest(Base):
    """保证金充值申请"""
    __tablename__ = "deposit_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    status = Column(String(20), default="pending")  # pending / approved / rejected
    reviewer_id = Column(Integer, nullable=True)
    note = Column(String(200), nullable=True)
    reviewed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))


class WithdrawRequest(Base):
    """提现申请"""
    __tablename__ = "withdraw_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    amount = Column(Float, nullable=False)
    bank_card = Column(String(50), nullable=True)
    status = Column(String(20), default="pending")  # pending / approved / rejected / done
    audit_time = Column(DateTime, nullable=True)
    remark = Column(String(200), nullable=True)
    created_at = Column(DateTime, server_default=text("datetime('now','localtime')"))
