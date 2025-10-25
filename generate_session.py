#!/usr/bin/env python3
"""
generate_session.py

A helper script to generate a Telethon session string for the bio updater.
"""
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print("🚀 Starting session generator...")
print("🔑 Please enter your Telegram API credentials.")

try:
    api_id = int(input("Enter your API_ID: "))
    api_hash = input("Enter your API_HASH: ")
except (ValueError, TypeError):
    print("\n❌ Error: API_ID must be a number.")
    exit()

with TelegramClient(StringSession(), api_id, api_hash) as client:
    session_string = client.session.save()
    print("\n✅ Session string generated successfully!")
    print("👇 Copy the following string and add it to your .env file or environment variables on Render:")
    print(f"\nSESSION_STRING={session_string}\n")

print("🛑 Session generator finished.")
