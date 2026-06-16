"""
短信发送服务
当前为日志模式（记录到 sms_logs 表），接入真实 SMS 提供商后替换 send_sms 函数。

对接阿里云/腾讯云/SUBMAIL 等提供商的步骤：
1. 在 config.py 中添加 SMS_API_KEY / SMS_SECRET
2. 修改 send_sms() 中的 HTTP 请求为对应提供商的接口
3. 设置 SMS_ENABLED = True
"""
import logging
from datetime import datetime
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

SMS_ENABLED = False  # 设为 True 后启用真实发送
SMS_API_URL = ""     # 例如 "https://api.mysubmail.com/message/send"
SMS_APP_ID = ""
SMS_APP_KEY = ""
SMS_SIGN = "云匠"    # 短信签名


def send_sms(db: Session, phone: str, template: str, params: dict = None):
    """
    发送短信并记录到 sms_logs 表

    Args:
        db: 数据库会话
        phone: 接收手机号
        template: 短信模板标识 (如 "order_created", "order_dispatched")
        params: 模板参数 (如 {"code": "1234", "name": "张先生"})

    Returns:
        bool: 是否成功
    """
    from models.sms import SmsLog

    try:
        if SMS_ENABLED and SMS_API_URL:
            # ── 真实发送（接入 SMS 提供商后启用） ──
            # import requests
            # resp = requests.post(SMS_API_URL, json={
            #     "appid": SMS_APP_ID,
            #     "sign": SMS_SIGN,
            #     "to": phone,
            #     "project": template,
            #     "vars": params or {},
            # })
            # success = resp.status_code == 200
            success = False  # 暂未接入
            logger.info(f"[SMS] 发送至 {phone}: 模板={template}, 结果={'成功' if success else '失败'}")
        else:
            # ── 日志模式：只记录，不真实发送 ──
            param_str = ",".join(f"{k}={v}" for k, v in (params or {}).items())
            logger.info(f"[SMS] 日志模式 → 发送至 {phone}: [{template}] {param_str}")
            success = True

        # 写入发送记录
        log = SmsLog(
            phone=phone,
            template=template,
            params=str(params) if params else None,
            status="sent" if success else "failed",
        )
        db.add(log)
        db.commit()

        if not success:
            logger.error(f"[SMS] 发送失败: phone={phone}, template={template}")

        return success

    except Exception as e:
        logger.error(f"[SMS] 异常: phone={phone}, template={template}, err={e}")
        try:
            db.rollback()
        except Exception:
            pass
        return False


def send_order_notification(db: Session, phone: str, order_no: str, customer_name: str = "客户"):
    """
    客户下单后的短信通知

    短信内容: 【云匠】{name}您好，您的报修已收到（单号：{order_no}），
              师傅将在30分钟内联系您，请保持电话畅通。
    """
    params = {
        "name": customer_name,
        "order_no": order_no,
    }
    return send_sms(db, phone, "order_created", params)
