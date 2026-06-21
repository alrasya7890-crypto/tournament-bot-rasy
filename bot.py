import telebot
import json
import os
from datetime import datetime, timedelta

# Mengambil variabel dari Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID_ENV = os.getenv("OWNER_ID")
SUPER_ADMIN_ID = int(OWNER_ID_ENV) if (OWNER_ID_ENV and OWNER_ID_ENV.isdigit()) else 0

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

# 🔥 JAMU ANTI-TIMEOUT: Set global timeout di apihelper biar ga crash get_updates di Railway
telebot.apihelper.CONNECT_TIMEOUT = 90
telebot.apihelper.READ_TIMEOUT = 90

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
            return json.load(f)
    except:
        return {
            "pembeli_list": [],      
            "owner_settings": {},    
            "brackets": {}           
        }

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

db = load()

def get_group_owner_settings(chat_id):
    fallback_settings = get_default_owner_settings(SUPER_ADMIN_ID, "@rrassyaaaa")
    try:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            admin_id_str = str(admin.user.id)
            if admin_id_str in db["pembeli_list"] or admin.user.id == SUPER_ADMIN_ID:
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
    global db
    
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

        if msg_lower.startswith(("addpembeli", "delpembeli")) or msg_lower == "listpembeli":
            if user_id != SUPER_ADMIN_ID: 
                return bot.reply_to(message, "❌ Cuma Rasya yang bisa akses lisensi global!")
            
            parts = msg_text.split()
            if msg_lower.startswith("addpembeli"):
                if len(parts) < 2: return bot.reply_to(message, "❌ Format salah. Contoh: addpembeli 123456")
                try:
                    tid = int(parts[1])
                    if tid not in db["pembeli_list"]: db["pembeli_list"].append(tid)
                    if str(tid) not in db["owner_settings"]: db["owner_settings"][str(tid)] = get_default_owner_settings(tid)
                    save(db)
                    return bot.reply_to(message, f"✅ ID `{tid}` sukses jadi pembeli resmi!")
                except ValueError: return bot.reply_to(message, "❌ ID harus angka, Sya!")
                    
            if msg_lower.startswith("delpembeli"):
                if len(parts) < 2: return bot.reply_to(message, "❌ Format salah. Contoh: delpembeli 123456")
                try:
                    tid = int(parts[1])
                    if tid in db["pembeli_list"]: db["pembeli_list"].remove(tid)
                    save(db)
                    return bot.reply_to(message, f"❌ Lisensi ID `{tid}` dicabut!")
                except ValueError: return bot.reply_to(message, "❌ ID harus angka, Sya!")
                    
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

        return bot.reply_to(message, "ℹ️ *MENU SETTING OWNER (PC)*\n\nLu bisa setting profil lu di sini:\n• `settitle [Judul]` \n• `setowner [Nama/Tele]` \n• `setpay [Link Pay]` \n• `setrules [Link Rules]`", parse_mode="Markdown")

    # ─── B. ROOM GRUP CHAT ───
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
    # Ditambah long_polling_timeout 60 detik biar stabil di internal apihelper
    bot.infinity_polling(skip_pending=True, timeout=60, long_polling_timeout=60)
    
