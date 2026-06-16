"""
AI 智能功能路由
- /api/ai/diagnose - AI 故障诊断
- /api/ai/chat - AI 客服对话
"""
import os
import json
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/api/ai", tags=["AI 智能"])

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-332af52a02b74f7eb1b519151d898513")
API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL = "deepseek-chat"


async def call_deepseek(messages: list, max_tokens: int = 1024) -> str:
    """调用 DeepSeek API"""
    async with httpx.AsyncClient(timeout=30) as client:
        resp = await client.post(API_URL, json={
            "model": MODEL,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }, headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}",
        })
        if resp.status_code != 200:
            raise HTTPException(502, f"AI 服务异常: {resp.text[:200]}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]


# ─── 请求模型 ───

class DiagnoseRequest(BaseModel):
    fault_description: str
    service_name: Optional[str] = ""
    category_name: Optional[str] = ""


class ChatRequest(BaseModel):
    message: str
    history: Optional[List[dict]] = []


# ─── AI 故障诊断 ───

@router.post("/diagnose")
async def ai_diagnose(req: DiagnoseRequest):
    """AI 智能诊断：分析故障原因、建议维修方案、预估价格"""
    system_prompt = """你是一个专业的家庭维修诊断助手，名叫"云匠AI诊断"。根据用户描述的故障情况，给出以下三方面的分析：

1. 可能原因：列出 2-4 个可能的原因，按可能性从高到低排列
2. 维修建议：针对每个原因给出建议的维修方案
3. 预估价格：根据故障类型给出大致的价格范围

请用中文回答，格式简洁清晰，适合在手机屏幕上阅读。回答使用以下 JSON 格式：
{
  "possible_causes": [{"cause": "原因描述", "probability": "高/中/低"}],
  "suggestions": ["建议1", "建议2"],
  "price_estimate": {"min": 100, "max": 500, "note": "价格说明"},
  "summary": "一句话总结"
}"""

    user_prompt = f"【故障描述】{req.fault_description}"
    if req.category_name:
        user_prompt += f"\n【服务分类】{req.category_name}"
    if req.service_name:
        user_prompt += f"\n【服务项目】{req.service_name}"

    try:
        result = await call_deepseek([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ], max_tokens=2048)

        # 尝试解析 JSON
        result = result.strip()
        if result.startswith("```"):
            result = result.split("```")[1]
            if result.startswith("json"):
                result = result[4:]
        result = result.strip()

        try:
            data = json.loads(result)
        except json.JSONDecodeError:
            data = {"raw": result}

        return {
            "code": 0,
            "message": "ok",
            "data": data,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"诊断失败: {str(e)}")


# ─── AI 客服对话 ───

@router.post("/chat")
async def ai_chat(req: ChatRequest):
    """AI 客服：回答用户关于维修服务的问题"""
    system_prompt = """你是一个家庭维修平台的AI客服助手，名叫"小黄"。你服务于"云匠"平台。

平台信息：
- 服务范围：家电维修、家政保洁、清洗服务、上门检测、电脑维修
- 服务流程：提交报修 → 系统派单 → 师傅接单 → 上门维修 → 完工付费
- 保修政策：所有维修服务享有一年免费保修
- 价格政策：显示价格为参考价，上门检测后确认

你的回答要求：
1. 热情友好，用亲切的语气
2. 回答简洁，适合手机阅读
3. 不知道的不要瞎编，引导用户联系人工客服
4. 可以询问更多细节来帮助用户
5. 使用中文"""

    messages = [{"role": "system", "content": system_prompt}]

    # 添加历史消息
    for msg in req.history[-10:]:  # 最多保留10条历史
        if msg.get("role") in ("user", "assistant"):
            messages.append({"role": msg["role"], "content": msg["content"]})

    # 添加当前消息
    messages.append({"role": "user", "content": req.message})

    try:
        reply = await call_deepseek(messages, max_tokens=1024)
        return {
            "code": 0,
            "message": "ok",
            "data": {
                "reply": reply,
            },
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"AI 回复失败: {str(e)}")
