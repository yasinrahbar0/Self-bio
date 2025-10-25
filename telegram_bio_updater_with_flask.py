#!/usr/bin/env python3
"""
telegram_bio_updater_with_flask.py

✅ آپدیت خودکار بیو تلگرام با:
- 🕒 ساعت تهران
- 📅 تاریخ شمسی (جلالی)
- 🌙 نام ماه شمسی
- 📆 روز هفته (فارسی)
- سلام صبح/ظهر/شب با ایموجی

📦 نصب وابستگی‌ها:
pip install telethon jdatetime pytz python-dotenv flask

⚙️ متغیرهای محیطی مورد نیاز:
API_ID, API_HASH, SESSION_STRING

👟 اجرا:
python telegram_bio_updater_with_flask.py
"""
import os
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import functions
import jdatetime
from dotenv import load_dotenv
from flask import Flask

# Flask app setup
app = Flask(__name__)

# Load .env variables
load_dotenv()
API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

if not API_ID or not API_HASH or not SESSION_STRING:
    raise SystemExit("❌ لطفاً متغیرهای محیطی API_ID، API_HASH و SESSION_STRING را تنظیم کنید.")

# منطقه زمانی تهران
TEHRAN_TZ = pytz.timezone("Asia/Tehran")

# نام ماه‌ها و روزهای هفته به فارسی
PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]
PERSIAN_WEEKDAYS = [
    "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه", "یک‌شنبه"
]

def persian_greeting(hour: int) -> str:
    """بر اساس ساعت تهران، پیام مناسب با ایموجی برگردان"""
    if 5 <= hour < 11:
        return "🌞 ✦ صبح بخیر ✦"
    if 11 <= hour < 17:
        return "☀️ ✦ ظهر بخیر ✦"
    return "🌙 ✦ شب بخیر ✦"

async def build_bio() -> str:
    """ساخت متن بیو"""
    now_utc = datetime.utcnow().replace(tzinfo=pytz.utc)
    now = now_utc.astimezone(TEHRAN_TZ)
    time_str = now.strftime("%H:%M:%S")
    jnow = jdatetime.datetime.fromgregorian(datetime=now)
    date_str = f"{jnow.year}/{jnow.month:02d}/{jnow.day:02d}"
    month_name = PERSIAN_MONTHS[jnow.month - 1]
    weekday_name = PERSIAN_WEEKDAYS[jnow.weekday()]
    greeting = persian_greeting(now.hour)

    bio = (
        f"🕒 ساعت: {time_str} | "
        f"📅 تاریخ: {date_str} | "
        f"🌙 ماه: {month_name} | "
        f"📆 امروز: {weekday_name} | "
        f"{greeting}"
    )
    return bio

async def main():
    if len(SESSION_STRING) > 200:
        session = StringSession(SESSION_STRING)
    else:
        session = SESSION_STRING
    client = TelegramClient(session, int(API_ID), API_HASH)
    await client.start()
    print("🚀 Client started — updating bio every 60 seconds...")

    try:
        while True:
            try:
                bio_text = await build_bio()
                await client(functions.account.UpdateProfileRequest(about=bio_text))
                print(f"✅ Updated bio: {bio_text}")
            except Exception as e:
                print("⚠️ Error updating bio:", e)
            await asyncio.sleep(60)
    finally:
        await client.disconnect()

@app.route('/')
def index():
    return "Bio updater is running..."

if __name__ == "__main__":
    # Run Flask to keep server alive
    import threading
    port = int(os.environ.get('PORT', 5000))
    threading.Thread(target=lambda: app.run(host='0.0.0.0', port=port, use_reloader=False)).start()

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Stopped by user")
    except Exception:
        import sys
        import traceback
        traceback.print_exc()
        sys.exit(1)
