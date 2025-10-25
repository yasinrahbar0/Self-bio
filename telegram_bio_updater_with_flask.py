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

from datetime import timezone

async def build_bio() -> str:
    """ساخت متن بیو"""
    now_utc = datetime.now(timezone.utc)
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

def run_telethon_client():
    """Wrapper to run the Telethon client in a separate thread."""
    print("🚀 Starting Telethon client in a background thread...")
    # Create a new event loop for the new thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(main())
    except Exception as e:
        print(f"❌ Error in Telethon client thread: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Start the Telethon client in a background thread
    import threading
    telethon_thread = threading.Thread(target=run_telethon_client)
    telethon_thread.daemon = True  # Allows main thread to exit even if this thread is running
    telethon_thread.start()

    # Run Flask app in the main thread (as expected by Render)
    print("🚀 Starting Flask server in the main thread...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)
