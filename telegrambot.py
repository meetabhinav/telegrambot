#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PUBLIC NUMBER LOOKUP BOT — RENDER READY
Auto-Delete: 40s | Second Bot Backup | User Profile Log
"""

import requests
import json
import os
import time
import threading
from datetime import datetime
from pathlib import Path

# ============================================================
# CONFIG — ENVIRONMENT VARIABLES
# ============================================================
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN', '8828522785:AAFn5vykRq1JRMor0xhVknM4t-iBSRYdogg')
SECOND_BOT_TOKEN = os.environ.get('SECOND_BOT_TOKEN', '8971907815:AAEKNI_tCtjbXgUp-pi5-TPNecYI1wXJqcA')
ALPHA_CHAT_ID = os.environ.get('ALPHA_CHAT_ID', '8207657563')
TRACEX_API_KEY = os.environ.get('TRACEX_API_KEY', 'tx_9e7daa9c251d3d29093393ab845b0ea6')

TRACEX_URL = 'https://tracexdata-api.onrender.com/api/lookup'

# ============================================================
# PATHS — Render Compatible
# ============================================================
BASE_DIR = Path(__file__).parent
LOG_DIR = BASE_DIR / "logs"
LOG_FILE = LOG_DIR / "botRespons.txt"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================
# FALTOO FIELDS REMOVER
# ============================================================
FIELDS_TO_REMOVE = [
    "api_buy_link", "website_link", "buy_api_link", "site_link",
    "purchase_link", "api_purchase_url", "buy_link", "promo_link",
    "ad_link", "sponsored_link"
]

def clean_json(data):
    if isinstance(data, dict):
        keys_to_delete = []
        for key in data:
            if key.lower() in [f.lower() for f in FIELDS_TO_REMOVE]:
                keys_to_delete.append(key)
        for key in keys_to_delete:
            del data[key]
        for key, value in data.items():
            data[key] = clean_json(value)
    elif isinstance(data, list):
        for i in range(len(data)):
            data[i] = clean_json(data[i])
    return data

# ============================================================
# LOG FUNCTION
# ============================================================
def log_to_file(data):
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write(f"[SERVER LOG] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("SERVICE: TELEGRAM BOT RESPONSE\n")
            f.write("-" * 60 + "\n")
            f.write(data + "\n")
            f.write("=" * 60 + "\n\n")
    except Exception as e:
        print(f"⚠️ Log Error: {e}")

# ============================================================
# SEND MESSAGE TO MAIN BOT
# ============================================================
def send_telegram(chat_id, message):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    data = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            log_to_file(message)
            return response.json()['result']['message_id']
        else:
            print(f"❌ Telegram Error: {response.json()}")
            return None
    except Exception as e:
        print(f"❌ Send Error: {e}")
        return None

# ============================================================
# AUTO-DELETE MESSAGE (40 सेकंड बाद)
# ============================================================
def auto_delete_message(chat_id, message_id, delay=40):
    time.sleep(delay)
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/deleteMessage'
    data = {'chat_id': chat_id, 'message_id': message_id}
    try:
        response = requests.post(url, data=data, timeout=10)
        if response.status_code == 200:
            print(f"🗑️ Deleted: User={chat_id}, MsgID={message_id}")
        else:
            print(f"⚠️ Delete Error: {response.json()}")
    except Exception as e:
        print(f"❌ Delete Error: {e}")

# ============================================================
# SEND TO SECOND BOT (सुरक्षित कॉपी)
# ============================================================
def send_to_second_bot(number, data, user_info_dict):
    try:
        cleaned_data = clean_json(data)
        json_str = json.dumps(cleaned_data, indent=2, ensure_ascii=False)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # JSON File Send
        url = f'https://api.telegram.org/bot{SECOND_BOT_TOKEN}/sendDocument'
        filename = f"{number}_{timestamp}.json"
        files = {'document': (filename, json_str.encode('utf-8'), 'application/json')}
        
        caption = (
            f"📁 <b>#NumberLookup_Log</b>\n"
            f"{'=' * 40}\n"
            f"🕵️ <b>USER PROFILE:</b>\n"
            f"   • <b>Chat ID:</b> <code>{user_info_dict.get('chat_id', 'N/A')}</code>\n"
            f"   • <b>Name:</b> {user_info_dict.get('first_name', 'N/A')} {user_info_dict.get('last_name', '')}\n"
            f"   • <b>Username:</b> @{user_info_dict.get('username', 'N/A')}\n"
            f"   • <b>Language:</b> {user_info_dict.get('language_code', 'N/A')}\n"
            f"   • <b>Is Premium:</b> {'✅ Yes' if user_info_dict.get('is_premium') else '❌ No'}\n"
            f"   • <b>Chat Type:</b> {user_info_dict.get('type', 'N/A')}\n"
            f"{'=' * 40}\n"
            f"🔢 <b>LOOKUP NUMBER:</b> <code>{number}</code>\n"
            f"🕒 <b>TIME:</b> {current_time}\n"
        )
        
        data_payload = {'chat_id': ALPHA_CHAT_ID, 'caption': caption, 'parse_mode': 'HTML'}
        response = requests.post(url, data=data_payload, files=files, timeout=15)
        
        if response.status_code == 200:
            print(f"📤 Second bot: {filename}")
            # Text backup
            text_url = f'https://api.telegram.org/bot{SECOND_BOT_TOKEN}/sendMessage'
            json_display = json_str[:3500] + "\n\n... (📁 Full JSON in file above)" if len(json_str) > 3500 else json_str
            text_msg = (
                f"🕵️ <b>USER ACTIVITY LOG</b>\n"
                f"{'=' * 40}\n"
                f"👤 <b>User:</b> {user_info_dict.get('first_name', 'N/A')} {user_info_dict.get('last_name', '')}\n"
                f"🆔 <b>Chat ID:</b> <code>{user_info_dict.get('chat_id', 'N/A')}</code>\n"
                f"📛 <b>Username:</b> @{user_info_dict.get('username', 'N/A')}\n"
                f"🌐 <b>Language:</b> {user_info_dict.get('language_code', 'N/A')}\n"
                f"⭐ <b>Premium:</b> {'Yes' if user_info_dict.get('is_premium') else 'No'}\n"
                f"🔢 <b>Lookup:</b> <code>{number}</code>\n"
                f"🕒 <b>Time:</b> {current_time}\n"
                f"{'=' * 40}\n"
                f"<pre>{json_display}</pre>"
            )
            text_payload = {'chat_id': ALPHA_CHAT_ID, 'text': text_msg, 'parse_mode': 'HTML'}
            requests.post(text_url, data=text_payload, timeout=10)
            return True
        else:
            print(f"❌ Second Bot Error: {response.json()}")
            return False
    except Exception as e:
        print(f"❌ Second Bot Exception: {e}")
        return False

# ============================================================
# LOOKUP NUMBER
# ============================================================
def lookup_number(chat_id, number, user_info_dict):
    try:
        response = requests.get(TRACEX_URL, params={'key': TRACEX_API_KEY, 'number': number}, timeout=15)
        data = response.json()
        
        send_to_second_bot(number, data, user_info_dict)
        
        if data.get('status') == 'success' and data.get('results'):
            msg = "<b>📡 Real Time Activity RESULT</b>\n"
            msg += "=" * 40 + "\n"
            for key, entry in data['results'].items():
                msg += f"\n<b>{key}</b>\n"
                msg += f"👤 Name        : {entry.get('name', 'N/A')}\n"
                msg += f"👨‍👦 Father      : {entry.get('father_name', 'N/A')}\n"
                msg += f"📱 Mobile      : {entry.get('mobile', 'N/A')}\n"
                msg += f"📞 Alt Mobile  : {entry.get('alt_mobile', 'N/A')}\n"
                msg += f"🆔 Aadhaar     : {entry.get('aadhar_number', 'N/A')}\n"
                msg += f"📍 Address     : {entry.get('address', 'N/A')}\n"
                msg += f"📡 Circle      : {entry.get('circle', 'N/A')}\n"
            msg += f"\n⏰ <i>This message will auto-delete in 40 seconds</i>"
            msg_id = send_telegram(chat_id, msg)
            if msg_id:
                threading.Thread(target=auto_delete_message, args=(chat_id, msg_id, 40), daemon=True).start()
        else:
            msg = f"❌ No data found for {number}"
            msg_id = send_telegram(chat_id, msg)
            if msg_id:
                threading.Thread(target=auto_delete_message, args=(chat_id, msg_id, 40), daemon=True).start()
    except Exception as e:
        error_msg = f"❌ Error: {e}"
        msg_id = send_telegram(chat_id, error_msg)
        if msg_id:
            threading.Thread(target=auto_delete_message, args=(chat_id, msg_id, 40), daemon=True).start()

# ============================================================
# GET UPDATES
# ============================================================
def get_updates(offset=None):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/getUpdates'
    params = {'timeout': 30, 'offset': offset}
    try:
        response = requests.get(url, params=params, timeout=35)
        if response.status_code == 200:
            return response.json().get('result', [])
        else:
            print(f"❌ GetUpdates Error: {response.json()}")
            return []
    except Exception as e:
        print(f"❌ GetUpdates Exception: {e}")
        return []

# ============================================================
# MAIN LOOP
# ============================================================
def main():
    print("=" * 60)
    print("🤖 TELEGRAM BOT STARTED — 24/7 MODE")
    print(f"🔑 Main Token: {TELEGRAM_TOKEN[:10]}...")
    print(f"🔐 Second Bot: {'✅' if SECOND_BOT_TOKEN else '❌ Not Set'}")
    print(f"👑 Alpha Chat ID: {ALPHA_CHAT_ID}")
    print(f"⏰ Auto-Delete: 40 seconds")
    print("=" * 60)
    
    last_update_id = 0
    while True:
        try:
            updates = get_updates(last_update_id + 1)
            for update in updates:
                last_update_id = update['update_id']
                if 'message' in update:
                    msg = update['message']
                    text = msg.get('text', '').strip()
                    chat = msg['chat']
                    
                    user_info_dict = {
                        'chat_id': chat['id'],
                        'first_name': chat.get('first_name', 'Unknown'),
                        'last_name': chat.get('last_name', ''),
                        'username': chat.get('username', 'No_Username'),
                        'language_code': chat.get('language_code', 'N/A'),
                        'is_premium': chat.get('is_premium', False),
                        'type': chat.get('type', 'private')
                    }
                    chat_id = chat['id']
                    user_short_info = f"{user_info_dict['first_name']} (@{user_info_dict['username']}) | ID: {chat_id}"
                    print(f"📩 {user_short_info}: {text}")
                    
                    if text == '/start':
                        welcome_msg = (
                            f"👋 Welcome {user_info_dict['first_name']}!\n\n"
                            "Send me a 10-digit mobile number to lookup.\n\n"
                            "⏰ <b>Privacy Note:</b> Results auto-delete in 40 seconds.\n"
                            "🔄 Running 24/7"
                        )
                        msg_id = send_telegram(chat_id, welcome_msg)
                        if msg_id:
                            threading.Thread(target=auto_delete_message, args=(chat_id, msg_id, 60), daemon=True).start()
                    elif len(text) == 10 and text.isdigit():
                        lookup_msg_id = send_telegram(chat_id, f"🔍 Looking up: {text}...")
                        lookup_number(chat_id, text, user_info_dict)
                        if lookup_msg_id:
                            threading.Thread(target=auto_delete_message, args=(chat_id, lookup_msg_id, 10), daemon=True).start()
                    else:
                        error_msg_id = send_telegram(chat_id, "❌ Please send a valid 10-digit number. 😊")
                        if error_msg_id:
                            threading.Thread(target=auto_delete_message, args=(chat_id, error_msg_id, 15), daemon=True).start()
        except KeyboardInterrupt:
            print("\n🛑 Bot stopped.")
            break
        except Exception as e:
            print(f"❌ Main Loop Error: {e}")

if __name__ == '__main__':
    main()
