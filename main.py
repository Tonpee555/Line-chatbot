from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
import httpx
import os
import logging
from db import fetch_answer, clear_history

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="LINE OA Chatbot x Claude AI")

LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "YOUR_TOKEN_HERE")
LINE_SECRET = os.getenv("LINE_CHANNEL_SECRET", "YOUR_SECRET_HERE")


async def reply_message(reply_token: str, text: str):
    """ส่งข้อความกลับไปหาผู้ใช้ใน LINE"""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.line.me/v2/bot/message/reply",
            headers={
                "Authorization": f"Bearer {LINE_TOKEN}",
                "Content-Type": "application/json"
            },
            json={
                "replyToken": reply_token,
                "messages": [{"type": "text", "text": text}]
            }
        )
        if response.status_code != 200:
            logger.error(f"LINE API Error: {response.text}")


@app.post("/webhook")
async def webhook(request: Request):
    """รับ Webhook จาก LINE และส่งให้ Claude ตอบ"""
    try:
        body = await request.json()
        logger.info(f"Received webhook: {body}")

        for event in body.get("events", []):
            event_type = event.get("type")
            reply_token = event.get("replyToken")
            user_id = event.get("source", {}).get("userId", "unknown")

            # เมื่อผู้ใช้ส่งข้อความ
            if event_type == "message" and event.get("message", {}).get("type") == "text":
                user_text = event["message"].get("text", "").strip()
                logger.info(f"[{user_id}] Message: {user_text}")

                # คำสั่งพิเศษ: ล้างประวัติสนทนา
                if user_text.lower() in ["เริ่มใหม่", "reset", "clear"]:
                    clear_history(user_id)
                    await reply_message(reply_token, "เริ่มบทสนทนาใหม่แล้วค่ะ 🔄")
                    continue

                # ส่งให้ Claude ตอบ (จำบทสนทนาแยกตาม user_id)
                answer = await fetch_answer(user_text, user_id=user_id)
                await reply_message(reply_token, answer)

            # เมื่อผู้ใช้ Follow บัญชี
            elif event_type == "follow":
                welcome = "ยินดีต้อนรับค่ะ! 🎉\nมีอะไรให้ช่วยถามได้เลยนะคะ"
                await reply_message(reply_token, welcome)

        return JSONResponse(content={"status": "ok"})

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/")
async def root():
    return {"message": "LINE OA Chatbot x Claude AI is running! 🤖", "status": "ok"}


@app.get("/health")
async def health():
    return {"status": "healthy"}
