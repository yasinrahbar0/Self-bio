#!/usr/bin/env python3
import os
import asyncio
from datetime import datetime
import pytz
from telethon import TelegramClient, functions
from telethon.sessions import StringSession
import jdatetime
from dotenv import load_dotenv
from keep_alive import keep_alive

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
    "شنبه", "یک‌شنبه", "دوشنبه", "سه‌شنبه", "چهارشنبه", "پنج‌شنبه", "جمعه"
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
    date_str = f"📅 {jnow.year}/{jnow.month:02d}/{jnow.day:02d}"
    month_name = f"🌙 {PERSIAN_MONTHS[jnow.month - 1]}"
    weekday_name = f"📆 {PERSIAN_WEEKDAYS[jnow.weekday()]}"
    greeting = get_greeting(now.hour)
    return f"{date_str} | {month_name} | {weekday_name} | {greeting}"

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

if __name__ == '__main__':
    keep_alive()
    asyncio.run(update_bio())
