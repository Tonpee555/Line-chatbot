# LINE OA Chatbot 🤖

Chatbot เชื่อมต่อ LINE Messaging API พร้อมดึงข้อมูลจาก API/Database

## 📁 โครงสร้างไฟล์
```
line-chatbot/
├── main.py          ← โค้ดหลัก (แก้ตรงนี้)
├── requirements.txt ← Library ที่ใช้
├── .env.example     ← ตัวอย่าง Environment Variables
├── Procfile         ← สำหรับ Deploy บน Railway
└── README.md        ← คู่มือนี้
```

## 🚀 วิธี Deploy บน Railway (ฟรี)

### 1. เตรียม GitHub
```bash
git init
git add .
git commit -m "first commit"
git push origin main
```

### 2. Deploy บน Railway
1. ไปที่ https://railway.app → New Project
2. เลือก "Deploy from GitHub"
3. เลือก repo นี้
4. เพิ่ม Environment Variables:
   - `LINE_CHANNEL_ACCESS_TOKEN` = token จาก LINE Developer Console
   - `LINE_CHANNEL_SECRET` = secret จาก LINE Developer Console
   - `YOUR_API_URL` = URL ของ API คุณ

### 3. ตั้งค่า Webhook ใน LINE
1. ไปที่ https://developers.line.biz
2. เลือก Channel → Messaging API
3. ใส่ Webhook URL: `https://your-app.railway.app/webhook`
4. กด Verify ✅

## ✏️ วิธีแก้โค้ดเชื่อม API/DB ของคุณ

แก้ฟังก์ชัน `fetch_data_from_api()` ใน `main.py`:

```python
async def fetch_data_from_api(user_message: str) -> str:
    # แก้ตรงนี้ให้เชื่อม API หรือ DB ของคุณ
    async with httpx.AsyncClient() as client:
        res = await client.get(f"{YOUR_API_URL}/query?q={user_message}")
        data = res.json()
        return data.get("answer", "ไม่พบข้อมูลค่ะ")
```

## 🛠️ ทดสอบบน Local
```bash
pip install -r requirements.txt
cp .env.example .env
# แก้ค่าใน .env
uvicorn main:app --reload
```

## 📌 Endpoint
- `POST /webhook` — รับข้อความจาก LINE
- `GET /` — ตรวจสอบว่า server ทำงาน
- `GET /health` — Health check
