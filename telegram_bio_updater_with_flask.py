#!/usr/bin/env python3
import os
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
import jdatetime
from dotenv import load_dotenv
from flask import Flask

# بارگذاری متغیرها
load_dotenv()
API_ID = os.getenv('API_ID')
API_HASH = os.getenv('API_HASH')
SESSION_STRING = os.getenv('SESSION_STRING')

if not all([API_ID, API_HASH, SESSION_STRING]):
    raise SystemExit("❌ لطفا API_ID, API_HASH و SESSION_STRING را در .env وارد کنید.")

TEHRAN_TZ = pytz.timezone('Asia/Tehran')
PERSIAN_MONTHS = [
    "فروردین", "اردیبهشت", "خرداد", "تیر", "مرداد", "شهریور",
    "مهر", "آبان", "آذر", "دی", "بهمن", "اسفند"
]
PERSIAN_WEEKDAYS = [
    "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه", "شنبه"
]

def get_greeting(hour):
    if 5 <= hour < 11:
        return "🌞 ✦ صبح بخیر ✦"
    elif 11 <= hour < 17:
        return "☀️ ✦ ظهر بخیر ✦"
    else:
        return "🌙 ✦ شب بخیر ✦"

async def build_bio():
    now = datetime.now(TEHRAN_TZ)
    jnow = jdatetime.datetime.fromgregorian(datetime=now)
    time_str = now.strftime("🕒 %H:%M:%S")
    date_str = f"📅 {jnow.year}/{jnow.month:02d}/{jnow.day:02d}"
    month_name = f"🌙 {PERSIAN_MONTHS[jnow.month - 1]}"
    weekday_name = f"📆 {PERSIAN_WEEKDAYS[jnow.weekday()]}"
    greeting = get_greeting(now.hour)
    return f"{time_str} | {date_str} | {month_name} | {weekday_name} | {greeting}"

async def update_bio():
    session = StringSession(SESSION_STRING)
    client = TelegramClient(session, int(API_ID), API_HASH)
    await client.start()
    print("✅ Telegram client connected. Starting bio updates...")
    while True:
        try:
            bio_text = await build_bio()
            await client(functions.account.UpdateProfileRequest(about=bio_text))
            print("✅ Bio updated to:", bio_text)
        except Exception as e:
            print("⚠️ Error updating bio:", e)
        await asyncio.sleep(60)

# اجرای همزمان Flask و updater
app = Flask(__name__)

@app.route('/')
def home():
    return "🟢 Telegram Bio Updater is running!"

def start_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(update_bio())

if __name__ == '__main__':
    import threading
    threading.Thread(target=start_asyncio_loop).start()
    app.run(host="0.0.0.0", port=10000)
