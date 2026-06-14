"""
WebSocket 实时推送
师傅APP通过 WebSocket 接收实时通知
"""
import json
import logging
from typing import Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from jose import jwt, JWTError
from config import settings

logger = logging.getLogger(__name__)

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器（单例）"""

    def __init__(self):
        # user_id -> list of WebSocket connections
        self.active_connections: dict[int, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: int):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)
        logger.info(f"WebSocket 连接: user_id={user_id}, 当前连接数={len(self.active_connections[user_id])}")

    def disconnect(self, websocket: WebSocket, user_id: int):
        if user_id in self.active_connections:
            try:
                self.active_connections[user_id].remove(websocket)
            except ValueError:
                pass
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
        logger.info(f"WebSocket 断开: user_id={user_id}")

    async def send_personal_message(self, message: dict, user_id: int):
        """向指定用户的所有连接发送消息"""
        if user_id not in self.active_connections:
            return
        disconnected = []
        for conn in self.active_connections[user_id]:
            try:
                await conn.send_json(message)
            except Exception:
                disconnected.append(conn)
        for conn in disconnected:
            self.disconnect(conn, user_id)

    async def broadcast(self, message: dict):
        """向所有用户广播"""
        for user_id in list(self.active_connections.keys()):
            await self.send_personal_message(message, user_id)

    def get_online_users(self) -> list[int]:
        """获取当前在线用户ID列表"""
        return list(self.active_connections.keys())

    def is_online(self, user_id: int) -> bool:
        return user_id in self.active_connections and bool(self.active_connections[user_id])


# 全局单例
manager = ConnectionManager()


def decode_ws_token(token: str) -> Optional[int]:
    """解析 WebSocket token，返回 user_id 或 None"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id = payload.get("sub")
        if user_id is not None:
            return int(user_id)
    except (JWTError, ValueError):
        pass
    return None


@router.websocket("/api/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int, token: str = Query("")):
    """WebSocket 端点：/api/ws/{user_id}?token=xxx"""
    # 鉴权
    decoded_id = decode_ws_token(token)
    if decoded_id is None or decoded_id != user_id:
        await websocket.close(code=4001, reason="认证失败")
        return

    await manager.connect(websocket, user_id)
    try:
        # 发送连接成功消息
        await websocket.send_json({
            "type": "connected",
            "message": "连接成功",
            "user_id": user_id,
        })

        # 保持心跳
        while True:
            try:
                data = await websocket.receive_text()
                msg = json.loads(data)
                msg_type = msg.get("type", "")

                if msg_type == "pong":
                    pass  # 心跳回复，不需要处理
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})

            except json.JSONDecodeError:
                pass

    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)
    except Exception as e:
        logger.error(f"WebSocket 错误: {e}")
        manager.disconnect(websocket, user_id)


async def send_notification(
    user_id: int,
    type: str,
    title: str,
    content: Optional[str] = None,
    ref_id: Optional[int] = None,
    ref_type: Optional[str] = None,
):
    """工具函数：通过 WebSocket 发送实时通知（供其他路由调用）"""
    message = {
        "type": "notification",
        "data": {
            "type": type,
            "title": title,
            "content": content,
            "ref_id": ref_id,
            "ref_type": ref_type,
            "created_at": __import__("datetime").datetime.now().isoformat(),
        },
    }
    await manager.send_personal_message(message, user_id)
