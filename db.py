import httpx
import os

# ============================
# Gemini API Config
# ============================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

# ============================
# System Prompt — แก้ตรงนี้!
# ============================
SYSTEM_PROMPT = """คุณคือผู้ช่วยอัจฉริยะของ [ชื่อธุรกิจของคุณ]
ตอบภาษาไทยเท่านั้น ด้วยน้ำเสียงสุภาพ กระชับ และเป็นมิตร
หากไม่ทราบคำตอบ ให้บอกว่า 'ขออภัยค่ะ ไม่ทราบข้อมูลในส่วนนี้ กรุณาติดต่อเจ้าหน้าที่ได้เลยค่ะ'
"""

# ============================
# เก็บประวัติสนทนาแต่ละ user
# ============================
conversation_history: dict = {}
MAX_HISTORY = 10


async def fetch_answer(user_message: str, user_id: str = "default") -> str:
    """
    ส่งข้อความให้ Gemini ตอบ (ฟรี 1,500 req/วัน)
    รองรับการจำบทสนทนา (multi-turn)
    """

    # เพิ่มข้อความใหม่ลงประวัติ
    if user_id not in conversation_history:
        conversation_history[user_id] = []

    conversation_history[user_id].append({
        "role": "user",
        "parts": [{"text": user_message}]
    })

    # ตัดประวัติถ้ายาวเกินไป
    if len(conversation_history[user_id]) > MAX_HISTORY * 2:
        conversation_history[user_id] = conversation_history[user_id][-MAX_HISTORY * 2:]

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{GEMINI_URL}?key={GEMINI_API_KEY}",
                headers={"Content-Type": "application/json"},
                json={
                    "system_instruction": {
                        "parts": [{"text": SYSTEM_PROMPT}]
                    },
                    "contents": conversation_history[user_id],
                    "generationConfig": {
                        "maxOutputTokens": 500,
                        "temperature": 0.7,
                    }
                }
            )

            if response.status_code == 200:
                data = response.json()
                reply = data["candidates"][0]["content"]["parts"][0]["text"]

                # บันทึกคำตอบลงประวัติ
                conversation_history[user_id].append({
                    "role": "model",
                    "parts": [{"text": reply}]
                })

                return reply.strip()

            else:
                print(f"[ERROR] Gemini API: {response.status_code} - {response.text}")
                return "ขออภัยค่ะ ระบบขัดข้องชั่วคราว กรุณาลองใหม่อีกครั้งนะคะ"

    except Exception as e:
        print(f"[ERROR] fetch_answer: {e}")
        return "เกิดข้อผิดพลาด กรุณาติดต่อเจ้าหน้าที่ค่ะ"


def clear_history(user_id: str):
    """ล้างประวัติสนทนา (ผู้ใช้พิมพ์ 'เริ่มใหม่')"""
    if user_id in conversation_history:
        del conversation_history[user_id]
