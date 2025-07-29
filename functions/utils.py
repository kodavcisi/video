import os
import time
import shutil
from config import DOWNLOAD_DIR
from pyrogram.types import Message
from functions.ffmpeg import encode, get_codec, get_thumbnail, get_duration, get_width_height
from functions.progress import progress_for_pyrogram
from pyrogram.errors import FloodWait, MessageNotModified, MessageIdInvalid
from config import quee, PRE_LOG, SUDO_USERS, userbot

async def on_task_complete(app, message: Message):
    if quee:
        del quee[0]
    if quee:
        await add_task(app, quee[0])

async def add_task(app, message: Message):
    download_dir = None
    try:
        user_id = str(message.from_user.id)
        c_time = time.time()
        random_id = str(int(c_time))
        
        # Dosya adını belirle
        if message.video:
            file_name = message.video.file_name
        elif message.document:
            file_name = message.document.file_name
        elif message.audio:
            file_name = message.audio.file_name
        else:
            file_name = f"file_{user_id}_{random_id}"
        
        # Mesajı yanıtla
        msg = await message.reply_text(
            "`🟡 Video İşleme Alındı... 🟡\n\n⚙ Motor: Pyrogram\n\n#indirme`", 
            quote=True
        )
        
        # İndirme dizinini oluştur
        download_dir = os.path.join(DOWNLOAD_DIR, user_id, random_id)
        os.makedirs(download_dir, exist_ok=True)
        file_path = os.path.join(download_dir, file_name)
        
        # Dosyayı indir
        file_path = await message.download(
            file_name=file_path,
            progress=progress_for_pyrogram,
            progress_args=("`📥 İndiriliyor...`", msg, c_time)
        )
        
        # Kodlama işlemi
        await msg.edit("`🟣 Video Kodlanıyor... 🟣\n\n⚙ Motor: FFMPEG\n\n#kodlama`")
        encoded_file = await encode(file_path)  # Encode çıktısı aynı dizine
        
        if not encoded_file:
            await msg.edit_text("<code>❌ Dosya kodlanırken hata oluştu!</code>")
            return
            
        # Yükleme işlemi
        await msg.edit("`🟢 Video Kodlandı, Veriler Alınıyor... 🟢`")
        await handle_upload(app, encoded_file, message, msg, download_dir)
        await msg.edit_text("`✅ Başarıyla Tamamlandı!`")
        
    except MessageNotModified:
        pass
    except MessageIdInvalid:
        await msg.edit_text('❌ İndirme İptal Edildi!')
    except FloodWait as e:
        print(f"⏳ FloodWait beklemesi: {e.value}s")
        time.sleep(e.value)
    except Exception as e:
        error_msg = f"<code>❌ Kritik Hata: {str(e)}</code>"
        await msg.edit_text(error_msg)
        print(error_msg)
    finally:
        # Tüm geçici dosyaları temizle
        if download_dir and os.path.exists(download_dir):
            shutil.rmtree(download_dir, ignore_errors=True)
        await on_task_complete(app, message)

async def handle_upload(app, file_path, message, msg, temp_dir):
    try:
        user_id = str(message.from_user.id)
        c_time = time.time()
        
        # Kalıcı thumbnail yolu
        persistent_thumb = os.path.join(DOWNLOAD_DIR, user_id, f"{user_id}.jpg")
        
        # Medya meta verileri
        duration = get_duration(file_path)
        width, height = get_width_height(file_path)
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        audio_codec = get_codec(file_path, channel='a:0')
        
        # Thumbnail oluştur (kalıcı yoksa)
        if os.path.exists(persistent_thumb):
            thumb = persistent_thumb
        else:
            thumb = get_thumbnail(file_path, temp_dir, duration / 4)
        
        # Başlık oluştur
        caption = message.caption or f"<code>{file_name}</code>"
        
        # 2GB üstü dosyalar için özel işlem
        if file_size > 2_000_000_000:  # 2GB
            await app.send_message(PRE_LOG, "⚠️ 2GB+ video yükleniyor...")
            
            # Userbot ile log kanalına yükle
            video_msg = await userbot.send_video(
                chat_id=PRE_LOG,
                video=file_path,
                caption=caption,
                thumb=thumb,
                duration=duration,
                width=width,
                height=height,
                supports_streaming=True,
                progress=progress_for_pyrogram,
                progress_args=("`🌐 Log Kanalına Yükleniyor...`", msg, c_time)
            )
            
            # Kullanıcıya forwardla
            await app.copy_message(
                chat_id=message.chat.id,
                from_chat_id=PRE_LOG,
                message_id=video_msg.id
            )
        else:
            # Doğrudan kullanıcıya yükle
            await app.send_video(
                chat_id=message.chat.id,
                video=file_path,
                caption=caption,
                thumb=thumb,
                duration=duration,
                width=width,
                height=height,
                supports_streaming=True,
                progress=progress_for_pyrogram,
                progress_args=("`📤 Yükleniyor...`", msg, c_time)
            )
        
        # Ses kontrolü uyarısı
        if not audio_codec:
            await message.reply("`🔇 Ses bulunamadı, video sessiz kodlandı.\n\n#bilgilendirme`")
            
    except Exception as upload_error:
        error_msg = f"<code>❌ Yükleme Hatası: {str(upload_error)}</code>"
        await msg.edit_text(error_msg)
        print(error_msg)
    finally:
        # Geçici thumbnail'i temizle (kalıcı değilse)
        if thumb != persistent_thumb and os.path.exists(thumb):
            os.remove(thumb)
# --- Video Silme Fonksiyonu ---

async def delete_video(file_path):
    """
    Belirtilen video dosyasını siler.
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"{file_path} başarıyla silindi.")
            return True
        else:
            print(f"{file_path} bulunamadı.")
            return False
    except Exception as e:
        print(f"Dosya silinirken hata oluştu: {e}")
        return False
