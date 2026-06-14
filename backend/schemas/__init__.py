from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ── 组织架构 ──
class OrganizationCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    city: Optional[str] = None
    address: Optional[str] = None
    level: str  # headquarters / branch / district
    contact_phone: Optional[str] = None


class OrganizationOut(OrganizationCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── 用户/员工 ──
class UserCreate(BaseModel):
    name: str
    phone: str
    password: str
    role: str
    org_id: Optional[int] = None
    id_card: Optional[str] = None
    address: Optional[str] = None
    emergency_contact: Optional[str] = None
    emergency_phone: Optional[str] = None
    hire_date: Optional[str] = None


class UserLogin(BaseModel):
    phone: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    phone: str
    role: str
    org_id: Optional[int] = None
    status: str
    avatar: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


# ── 客户 ──
class CustomerCreate(BaseModel):
    name: str
    phone: str
    address: Optional[str] = None
    city: Optional[str] = None


class CustomerOut(CustomerCreate):
    id: int
    total_orders: int
    created_at: datetime

    class Config:
        from_attributes = True


# ── 服务分类 ──
class ServiceCategoryCreate(BaseModel):
    name: str
    icon: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = 0


class ServiceCategoryOut(ServiceCategoryCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


class ServiceCategoryUpdate(BaseModel):
    name: Optional[str] = None
    icon: Optional[str] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None


class ServiceItemCreate(BaseModel):
    category_id: int
    name: str
    parent_id: Optional[int] = None
    level: int = 1
    unit_type: str = "次"
    default_price: Optional[float] = None
    description: Optional[str] = None
    sort_order: Optional[int] = 0


class ServiceItemUpdate(BaseModel):
    name: Optional[str] = None
    category_id: Optional[int] = None
    parent_id: Optional[int] = None
    level: Optional[int] = None
    unit_type: Optional[str] = None
    default_price: Optional[float] = None
    description: Optional[str] = None
    sort_order: Optional[int] = None
    status: Optional[str] = None


class ServiceItemOut(ServiceItemCreate):
    id: int
    status: str
    created_at: datetime

    class Config:
        from_attributes = True


# ── 工单 ──
class WorkOrderCreate(BaseModel):
    customer_id: int
    service_item_id: int
    category_type: str
    fault_description: Optional[str] = None
    address: str
    appointment_time: Optional[datetime] = None
    images: Optional[str] = None  # JSON string
    source: str = "qrcode"


class WorkOrderUpdate(BaseModel):
    status: Optional[str] = None
    technician_id: Optional[int] = None
    service_item_id: Optional[int] = None
    category_type: Optional[str] = None
    fault_description: Optional[str] = None
    address: Optional[str] = None
    appointment_time: Optional[datetime] = None
    material_fee: Optional[float] = None
    service_fee: Optional[float] = None
    total_fee: Optional[float] = None
    before_photos: Optional[str] = None
    after_photos: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    customer_signature: Optional[str] = None
    rating: Optional[int] = None
    comment: Optional[str] = None
    quote_status: Optional[str] = None
    quote_amount: Optional[float] = None
    trip_fee: Optional[float] = None
    trip_fee_status: Optional[str] = None


class WorkOrderOut(BaseModel):
    id: int
    order_no: str
    org_id: Optional[int] = None
    customer_id: int
    technician_id: Optional[int] = None
    dispatcher_id: Optional[int] = None
    service_item_id: int
    category_type: str
    fault_description: Optional[str] = None
    address: str
    status: str
    source: str
    total_fee: float = 0
    service_fee: float = 0
    material_fee: float = 0
    pay_status: str = "unpaid"
    rating: Optional[int] = None
    images: Optional[str] = None
    before_photos: Optional[str] = None
    after_photos: Optional[str] = None
    quote_status: Optional[str] = None
    quote_amount: float = 0
    appointment_time: Optional[datetime] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    comment: Optional[str] = None
    trip_fee: float = 0
    trip_fee_status: Optional[str] = None
    created_at: datetime
    accepted_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    quoted_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    technician_name: Optional[str] = None
    technician_phone: Optional[str] = None
    service_item_name: Optional[str] = None

    class Config:
        from_attributes = True


class WorkOrderListOut(BaseModel):
    total: int
    items: list[WorkOrderOut]


# ── 通用 ──
class ApiResponse(BaseModel):
    code: int = 0
    message: str = "ok"
    data: Optional[object] = None
