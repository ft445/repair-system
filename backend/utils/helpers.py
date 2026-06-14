from datetime import datetime


def generate_order_no() -> str:
    """生成工单号：日期 + 6位随机数"""
    from random import randint
    now = datetime.now()
    return f"WO{now.strftime('%Y%m%d%H%M%S')}{randint(100, 999)}"


def save_upload(file, sub_dir: str = "images") -> str:
    """保存上传文件，返回相对路径"""
    import os, uuid
    from config import settings

    upload_path = os.path.join(settings.UPLOAD_DIR, sub_dir)
    os.makedirs(upload_path, exist_ok=True)
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(upload_path, filename)

    with open(filepath, "wb") as f:
        content = file.file.read()
        f.write(content)

    return f"/uploads/{sub_dir}/{filename}"
