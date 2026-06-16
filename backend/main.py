import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from datetime import date
from sqlalchemy import func
from database import init_db, get_db
from config import settings
from models import WorkOrder, OrderStatus
from models.application import TechApplication  # 注册模型
from routers import auth, customers, orders, services, technician, users, finance, attendance, parts, organizations, ai, quote, recruit, notifications, ws
from schemas import ApiResponse
from utils.helpers import save_upload

STATIC_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(title="云匠 API", version="1.0.0", lifespan=lifespan, docs_url="/docs")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")


# Library files (Vue, ElementPlus)
@app.get("/lib/vue.global.prod.js")
async def lib_vue():
    return FileResponse(os.path.join(STATIC_DIR, "lib", "vue.global.prod.js"), media_type="application/javascript")

@app.get("/lib/element-plus.umd.js")
async def lib_element():
    return FileResponse(os.path.join(STATIC_DIR, "lib", "element-plus.umd.js"), media_type="application/javascript")

@app.get("/lib/element-plus.css")
async def lib_element_css():
    return FileResponse(os.path.join(STATIC_DIR, "lib", "element-plus.css"), media_type="text/css")

# Register routers
app.include_router(auth.router)
app.include_router(customers.router)
app.include_router(orders.router)
app.include_router(services.router)
app.include_router(technician.router)
app.include_router(users.router)
app.include_router(finance.router)
app.include_router(attendance.router)
app.include_router(parts.router)
app.include_router(organizations.router)
app.include_router(ai.router)
app.include_router(quote.router)
app.include_router(recruit.router)
app.include_router(notifications.router)
app.include_router(ws.router)


# ── 通用上传接口 ──
@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """上传文件（图片/音频/视频），返回访问URL"""
    if not file.content_type:
        raise HTTPException(400, "无法识别文件类型")
    if not (file.content_type.startswith("image/") or file.content_type.startswith("audio/") or file.content_type.startswith("video/")):
        raise HTTPException(400, "仅支持图片、音频、视频文件")
    sub_dir = "images"
    if file.content_type.startswith("audio/"):
        sub_dir = "audio"
    elif file.content_type.startswith("video/"):
        sub_dir = "videos"
    path = save_upload(file, sub_dir)
    return ApiResponse(data={"url": path})


# ── 全局异常处理 ──
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"code": -1, "message": str(exc), "data": None},
    )


# Page routes
@app.get("/")
def serve_portal():
    return FileResponse("static/portal.html", media_type="text/html")

@app.get("/repair")
def serve_customer_page():
    return FileResponse("static/customer.html", media_type="text/html")

@app.get("/join")
def serve_recruit_page():
    return FileResponse("static/recruit.html", media_type="text/html")

@app.get("/poster")
def serve_poster_page():
    return FileResponse("static/poster.html", media_type="text/html")

@app.get("/qrcodes")
def serve_qrcodes_page():
    return FileResponse("static/qrcodes.html", media_type="text/html")

@app.get("/flyer")
def serve_flyer_page():
    return FileResponse("static/flyer.html", media_type="text/html")


@app.get("/admin")
@app.get("/hilnai")
def serve_admin_page():
    from fastapi.responses import FileResponse as FR
    resp = FR("static/admin.html", media_type="text/html")
    resp.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp


@app.get("/test")
def serve_test_page():
    return FileResponse("static/test.html", media_type="text/html")


@app.get("/api/health")
def health():
    return ApiResponse(message="ok", data={"version": "1.0.0"})


@app.get("/api/settings/public")
def public_settings(db=Depends(get_db)):
    """公开设置（供师傅APP读取）"""
    from sqlalchemy import text
    result = {}
    try:
        rows = db.execute(text("SELECT key, value FROM system_settings")).fetchall()
        result = {row[0]: row[1] for row in rows}
    except Exception:
        pass
    return ApiResponse(data={
        "commission_rate": int(result.get("commission_rate", 80)),
        "customer_service_phone": "13427632071",
        "platform_name": "云匠",
        "app_version": "1.1.0",
    })


@app.get("/api/stats/orders")
def order_stats(db=Depends(get_db)):
    """工单统计（仪表盘用）"""
    today = date.today()

    total = db.query(func.count(WorkOrder.id)).scalar() or 0
    pending = db.query(func.count(WorkOrder.id)).filter(WorkOrder.status == OrderStatus.PENDING.value).scalar() or 0
    undispatch = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status.in_([OrderStatus.PENDING.value, OrderStatus.ACCEPTED.value])
    ).scalar() or 0
    in_progress = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status.in_([
            OrderStatus.DISPATCHED.value,
            OrderStatus.IN_PROGRESS.value,
        ])
    ).scalar() or 0
    completed = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.DONE.value, OrderStatus.PAID.value])
    ).scalar() or 0
    completed_today = db.query(func.count(WorkOrder.id)).filter(
        WorkOrder.status.in_([OrderStatus.COMPLETED.value, OrderStatus.DONE.value, OrderStatus.PAID.value]),
        func.date(WorkOrder.completed_at) == today,
    ).scalar() or 0
    created_today = db.query(func.count(WorkOrder.id)).filter(
        func.date(WorkOrder.created_at) == today,
    ).scalar() or 0

    return ApiResponse(data={
        "total": total, "pending": pending, "undispatch": undispatch, "in_progress": in_progress,
        "completed": completed, "completed_today": completed_today, "created_today": created_today,
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
