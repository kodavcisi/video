import os
from os import environ
from dotenv import load_dotenv
from pyrogram import Client, enums
from pyrogram.errors import AuthKeyUnregistered, UserDeactivated, SessionPasswordNeeded
import logging

logging.basicConfig(
    format='%(name)s - %(levelname)s - %(message)s',
    handlers=[logging.FileHandler('log.txt'),
              logging.StreamHandler()],
    level=logging.INFO
)

LOGGER = logging

if os.path.exists('config.env'):
    load_dotenv('config.env')

quee = []

APP_ID = int(environ.get("APP_ID"))
API_HASH = environ.get("API_HASH")
BOT_TOKEN = environ.get("BOT_TOKEN")

DOWNLOAD_DIR = environ.get("DOWNLOAD_DIR", "downloads")
ENCODE_DIR = environ.get("ENCODE_DIR", "encodes")
SUDO_USERS = list(set(int(x) for x in environ.get("SUDO_USERS").split()))
PRE_LOG = environ.get("PRE_LOG", "")
STRING_SESSION = environ.get('STRING_SESSION', '')

# Userbot'un aktif olup olmadığını kontrol etmek için bir değişken
USERBOT_IS_ACTIVE = False

userbot = Client(
    name='userbot', 
    api_id=APP_ID, 
    api_hash=API_HASH, 
    session_string=STRING_SESSION
)

# Mantık: Session varsa başlatmayı dene, hata verirse veya session yoksa pas geç
if STRING_SESSION:
    try:
        userbot.start()
        USERBOT_IS_ACTIVE = True
        print("✅ Userbot Başlatıldı: 4 GB yükleme aktif.")
    except (AuthKeyUnregistered, UserDeactivated):
        print("⚠️ Userbot Session süresi dolmuş veya geçersiz! Userbot devre dışı.")
    except Exception as e:
        print(f"❌ Userbot başlatılırken hata oluştu: {e}")
else:
    print("ℹ️ STRING_SESSION bulunamadı. Userbot (4GB özelliği) devre dışı bırakıldı.")

# Eğer userbot çalışmazsa bile kod buradan aşağıya akmaya devam eder.
