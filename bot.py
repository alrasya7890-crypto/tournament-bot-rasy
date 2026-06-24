import telebot
import json
import os
import asyncio
import threading  # 🔥 Biar loop timer jalan di background, bot pot gak macet
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession

# Mengambil variabel dari Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID_ENV = os.getenv("OWNER_ID")
SUPER_ADMIN_ID = int(OWNER_ID_ENV) if (OWNER_ID_ENV and OWNER_ID_ENV.isdigit()) else 0

# 🔥 VARIABEL UNTUK SYSTEM USERBOT (TEMBAK PC)
API_ID = int(os.getenv("API_ID", 0))          
API_HASH = os.getenv("API_HASH")              
SESSION_STRING = os.getenv("SESSION_STRING")  

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

# 🔥 JAMU ANTI-TIMEOUT
telebot.apihelper.CONNECT_TIMEOUT = 90
telebot.apihelper.READ_TIMEOUT = 90

# Global control variable buat auto-spam timer
auto_spam_aktif = False
pesan_bc = ""

def get_default_owner_settings(user_id, username="@"):
    return {
        "title": "DONE OPEN FT CS RASY",
        "open_by": username,
        "pay_link": "https://t.me/+r-dDf3CxAHgzNGVl",
        "rules_link": "https://t.me/+LHr8jRVQHsszZGJl",
    }

def get_default_bracket_data():
    return {
        "semi": [None, None, None, None],
        "final": [None, None],
        "winner": None,
        "last_update": "Belum pernah diupdate"
    }

def load():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if "pembeli_list" not in data: data["pembeli_list"] = []
            if "owner_settings" not in data: data["owner_settings"] = {}
            if "brackets" not in data: data["brackets"] = {}
            if "target_bots" not in data: data["target_bots"] = []
            return data
    except:
        return {
            "pembeli_list": [],      
            "owner_settings": {},    
            "brackets": {} ,
            "target_bots": []      
        }

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load()

# ─── LOGIKA SAKTI TIMER SPAM BRUTAL (10 DETIK SEKALI SELAMA 5 MENIT) ───
async def run_userbot_loop():
    global auto_spam_aktif, pesan_bc, db
    
    # Konek pake akun utama lu via session string Telethon
    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.connect()
    
    # Catat waktu mulai dan tentukan waktu selesai (5 menit dari sekarang)
    waktu_selesai = datetime.now() + timedelta(minutes=5)
    print(f"[Userbot] Spam dimulai. Akan otomatis mati pada: {waktu_selesai.strftime('%H:%M:%S')}")
    
    while auto_spam_aktif:
        # Cek apakah durasi 5 menit udah habis
        if datetime.now() >= waktu_selesai:
            print("[Userbot] Waktu durasi 5 menit sudah habis! Auto-shutdown aktif.")
            auto_spam_aktif = False
            break
            
        # Reload db biar dapet list bot terupdate
        db = load()
        daftar_bot = db.get("target_bots", [])
        
        if not daftar_bot:
            print("[Userbot] Daftar bot kosong. Menunggu 10 detik...")
            await asyncio.sleep(10)
            continue
            
        for bot_username in daftar_bot:
            # Cek waktu lagi di tengah antrean bot
            if datetime.now() >= waktu_selesai or not auto_spam_aktif:
                auto_spam_aktif = False
                break
                
            try:
                # Akun lu otomatis PC ke bot target yang terdaftar
                await client.send_message(bot_username, f"/bc {pesan_bc}")
                print(f"[Userbot] Sukses spam ke {bot_username}")
            except Exception as e:
                print(f"[Userbot] Gagal spam ke {bot_username}: {e}")
            
            # 🔥 JEDA 10 DETIK SEKALI antar target bot sesuai request lu, Sya!
            await asyncio.sleep(3)
            
    await client.disconnect()
    print("[Userbot] Koneksi dimatikan, sistem stand-by kembali.")

def start_timer_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_userbot_loop())
    loop.close()


def get_group_owner_settings(chat_id):
    fallback_settings = get_default_owner_settings(SUPER_ADMIN_ID, "@rrassyaaaa")
    try:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id in db["pembeli_list"] or admin.user.id == SUPER_ADMIN_ID:
                admin_id_str = str(admin.user.id)
                if admin_id_str not in db["owner_settings"]:
                    username = f"@{admin.user.username}" if admin.user.username else admin.user.first_name
                    db["owner_settings"][admin_id_str] = get_default_owner_settings(admin.user.id, username)
                    save(db)
                return db["owner_settings"][admin_id_str]
    except:
        pass
    return fallback_settings

# ─── 1. HANDLER WELCOME MESSAGE ───
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id, f"👋 Welcome {user.first_name}\nngentot stay cokkk fastt inii 🔥")

# ─── 2. HANDLER UTAMA CHAT & PERINTAH ───
@bot.message_handler(content_types=['text', 'photo', 'sticker', 'video', 'document', 'animation'])
def handle_text(message):
    global db, auto_spam_aktif, pesan_bc
    
    if not message.text: return 

    chat_id = message.chat.id
    str_chat_id = str(chat_id)
    user_id = message.from_user.id if message.from_user else 0
    str_user_id = str(user_id)
    msg_text = message.text.strip()
    msg_lower = msg_text.lower()
    
    if str_chat_id not in db["brackets"]:
        db["brackets"][str_chat_id] = get_default_bracket_data()
        save(db)

    # ─── A. ROOM PRIVATE CHAT (PC BOT) ───
    if message.chat.type == "private":
        if user_id != SUPER_ADMIN_ID and user_id not in db["pembeli_list"]:
            return bot.reply_to(message, "❌ Lu belum punya lisensi pembeli. Hubungi Rasya buat sewa bot! 😉")

        if str_user_id not in db["owner_settings"]:
            username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            db["owner_settings"][str_user_id] = get_default_owner_settings(user_id, username)
            save(db)

        # 🔥 UPDATE FITUR CONTROLLER: JALAN 10 DETIK SEKALI SELAMA 5 MENIT MAXIMUM
        if msg_lower.startswith("start_auto"):
            if user_id != SUPER_ADMIN_ID:
                return bot.reply_to(message, "❌ Perintah ini khusus buat Rasya murni!")
            parts = msg_text.split(" ", 1)
            if len(parts) < 2:
                return bot.reply_to(message, "❌ Format salah! Contoh: `start_auto TEXT PESAN BC LU`")
            if not db.get("target_bots"):
                return bot.reply_to(message, "❌ Gagal! Daftar bot target kosong, Sya. Input dulu pake perintah `addtargetbot`!")
            if auto_spam_aktif:
                return bot.reply_to(message, "⚠️ Auto-spam lagi jalan, Sya. Ketik `stop_auto` dulu kalau mau paksa mati tengah jalan.")
            
            pesan_bc = parts[1]
            auto_spam_aktif = True
            
            # Run di thread terpisah biar ga crash/freeze bot-nya
            threading.Thread(target=start_timer_thread, daemon=True).start()
            return bot.reply_to(message, f"🚀 **SPAM BRUTAL AKTIF!**\n📝 Teks: `/bc {pesan_bc}`\n⏱️ Jeda: Tiap 10 detik sekali\n🛑 Durasi: Otomatis mati setelah 5 menit.")

        if msg_lower == "stop_auto":
            if user_id != SUPER_ADMIN_ID: return bot.reply_to(message, "❌ Khusus buat Rasya!")
            if not auto_spam_aktif: return bot.reply_to(message, "⚠️ Emang lagi gak aktif, Sya.")
            auto_spam_aktif = False
            return bot.reply_to(message, "🛑 **Paksa berhenti sukses! Sistem spam dimatikan.**")

        # FITUR MANAJEMEN BOT TARGET VIA CHAT (Khusus Rasya)
        if msg_lower.startswith(("addtargetbot", "deltargetbot")) or msg_lower == "listtargetbot":
            if user_id != SUPER_ADMIN_ID: return bot.reply_to(message, "❌ Khusus buat Rasya!")
            parts = msg_text.split()
            
            if msg_lower.startswith("addtargetbot"):
                if len(parts) < 2: return bot.reply_to(message, "❌ Contoh: `addtargetbot @username_bot_target`")
                b_user = parts[1] if parts[1].startswith("@") else f"@{parts[1]}"
                if b_user not in db["target_bots"]:
                    db["target_bots"].append(b_user)
                    save(db)
                    return bot.reply_to(message, f"✅ Sukses nambah `{b_user}` ke target PC!")
                return bot.reply_to(message, "⚠️ Bot itu udah ada di daftar, Sya.")

            if msg_lower.startswith("deltargetbot"):
                if len(parts) < 2: return bot.reply_to(message, "❌ Contoh: `deltargetbot @username_bot_target`")
                b_user = parts[1] if parts[1].startswith("@") else f"@{parts[1]}"
                if b_user in db["target_bots"]:
                    db["target_bots"].remove(b_user)
                    save(db)
                    return bot.reply_to(message, f"❌ `{b_user}` dihapus dari database!")
                return bot.reply_to(message, "❌ Bot itu emang gak ada di daftar.")

            if not db["target_bots"]: return bot.reply_to(message, "🤖 Target bot masih kosong.")
            return bot.reply_to(message, "🤖 **TARGET BOT SAKTI**:\n" + "\n".join([f"├ `{b}`" for b in db["target_bots"]]), parse_mode="Markdown")

        # Fitur Lisensi Pembeli (addlisensi / addpembeli)
        if msg_lower.startswith(("addpembeli", "delpembeli", "addlisensi", "dellisensi")) or msg_lower in ["listpembeli", "listlisensi"]:
            if user_id != SUPER_ADMIN_ID: 
                return bot.reply_to(message, "❌ Cuma Rasya yang bisa akses lisensi global!")
            
            parts = msg_text.split()
            
            if msg_lower.startswith(("addpembeli", "addlisensi")):
                if len(parts) < 2: return bot.reply_to(message, f"❌ Format salah. Contoh: {parts[0]} 123456")
                try:
                    tid = int(parts[1])
                    if tid not in db["pembeli_list"]: db["pembeli_list"].append(tid)
                    if str(tid) not in db["owner_settings"]: db["owner_settings"][str(tid)] = get_default_owner_settings(tid)
                    save(db)
                    return bot.reply_to(message, f"✅ ID `{tid}` sukses jadi pembeli resmi, Sya!")
                except ValueError: return bot.reply_to(message, "❌ ID harus angka murni, Sya!")
                    
            if msg_lower.startswith(("delpembeli", "dellisensi")):
                if len(parts) < 2: return bot.reply_to(message, f"❌ Format salah. Contoh: {parts[0]} 123456")
                try:
                    tid = int(parts[1])
                    if tid in db["pembeli_list"]: db["pembeli_list"].remove(tid)
                    save(db)
                    return bot.reply_to(message, f"❌ Lisensi ID `{tid}` berhasil dicabut!")
                except ValueError: return bot.reply_to(message, "❌ ID harus angka murni, Sya!")
                    
            return bot.reply_to(message, "👑 *PEMBELI AKTIF*:\n" + "\n".join([f"├ `{oid}`" for oid in db["pembeli_list"]]), parse_mode="Markdown")

        if msg_lower.startswith("set"):
            parts = msg_text.split(" ", 1)
            if len(parts) > 1:
                cmd, val = parts[0], parts[1]
                if cmd == "settitle": db["owner_settings"][str_user_id]["title"] = val
                elif cmd == "setowner": db["owner_settings"][str_user_id]["open_by"] = val
                elif cmd == "setpay": db["owner_settings"][str_user_id]["pay_link"] = val
                elif cmd == "setrules": db["owner_settings"][str_user_id]["rules_link"] = val
                save(db)
                return bot.reply_to(message, f"✅ Sukses update settingan profile PC lu: {cmd}")
            
        # 🔥 FIX JALUR: Kalau ada command khusus di atas, menu petunjuk setting ini ga bakal keluar ganggu lu lagi!
        if msg_lower in ["/start", "/help", "menu", "help"]:
            return bot.reply_to(message, "ℹ️ *MENU SETTING OWNER (PC)*\n\nLu bisa setting profil lu di sini:\n• `settitle [Judul]` \n• `setowner [Nama/Tele]` \n• `setpay [Link Pay]` \n• `setrules [Link Rules]`", parse_mode="Markdown")
        
        # Kalau cuma ketik chat random di PC, abaikan aja biar ga spam menu owner terus
        return

    # ─── B. ROOM GRUP CHAT (LOGIKA BOT POT) ───
    oset = get_group_owner_settings(chat_id)
    bdata = db["brackets"][str_chat_id]

    if msg_lower == "pot":
        semi, final, winner = bdata["semi"], bdata["final"], bdata["winner"]
        text = f"""🏆  {oset['title']}  🏆
━━━━━━━━━━━━━━━━━━━━
🕒 WAKTU UPDATE
└ {bdata.get('last_update', 'Belum pernah diupdate')}

👑 OPEN BY
└ {oset['open_by']}

━━━━━━━━━━━━━━━━━━━━
📊 BRACKET TURNAMEN
━━━━━━━━━━━━━━━━━━━━
🔴 SEMI FINAL
1️⃣ {semi[0] or "?"}  vs  {semi[1] or "?"}
2️⃣ {semi[2] or "?"}  vs  {semi[3] or "?"}

🔥 FINAL
🏆 {final[0] or "?"}  vs  {final[1] or "?"}

━━━━━━━━━━━━━━━━━━━━
🏅 PEMENANG
👑  【 {winner or "?"} 】
━━━━━━━━━━━━━━━━━━━━
by {oset['open_by']}"""
        return bot.reply_to(message, text)

    if msg_lower == "pay": return bot.reply_to(message, f"𝐏𝐀𝐘𝐌𝐄𝐍𝐓!! : {oset['pay_link']}")
    if msg_lower == "rules": return bot.reply_to(message, f"𝐑𝐔𝐋𝐄𝐒 𝐁𝐘 𝐑𝐀𝐒𝐘 : {oset['rules_link']}")

    is_pembeli = user_id in db["pembeli_list"] or user_id == SUPER_ADMIN_ID
    if not is_pembeli: return

    if msg_lower == "clear":
        db["brackets"][str_chat_id] = get_default_bracket_data()
        save(db)
        return bot.reply_to(message, "✅ Bracket grup ini berhasil dikosongkan!")

    if msg_lower in ["d1", "d2", "d3", "d4", "f1", "f2", "win"]:
        if not message.reply_to_message: return bot.reply_to(message, "❌ Reply player dulu!")
        
        p_user = message.reply_to_message.from_user
        name = f"@{p_user.username}" if p_user.username else p_user.first_name
        
        utc_now = datetime.utcnow()
        wib_now = utc_now + timedelta(hours=7)
        days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
        bdata["last_update"] = wib_now.strftime(f"{days[wib_now.weekday()]}! %d-%m-%Y %H:%M WIB")
        
        idx = {"d1": 0, "d2": 1, "d3": 2, "d4": 3}
        if msg_lower in idx: bdata["semi"][idx[msg_lower]] = name
        elif msg_lower == "f1": bdata["final"][0] = name
        elif msg_lower == "f2": bdata["final"][1] = name
        elif msg_lower == "win": bdata["winner"] = name
        
        db["brackets"][str_chat_id] = bdata
        save(db)
        
        semi = bdata["semi"]
        if msg_lower in ["d1", "d2"] and semi[0] and semi[1]:
            bot.reply_to(message, f"✅ Data Updated!\n\n🔴 **SEMI FINAL SLOT 1 READY**:\n👉 {semi[0]}  vs  {semi[1]}")
        elif msg_lower in ["d3", "d4"] and semi[2] and semi[3]:
            bot.reply_to(message, f"✅ Data Updated!\n\n🔴 **SEMI FINAL SLOT 2 READY**:\n👉 {semi[2]}  vs  {semi[3]}")
        else:
            bot.reply_to(message, "✅ Data Bracket Grup Diupdate!")

if __name__ == "__main__":
    print("Bot aktif...")
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
        
