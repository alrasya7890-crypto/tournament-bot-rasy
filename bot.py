import telebot
import json
import os
from datetime import datetime, timedelta

# Mengambil variabel dari Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("OWNER_ID"))

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"
last_main_message_id = None

def load():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "semi": [None, None, None, None],
            "final": [None, None],
            "winner": None,
            "last_update": "Belum pernah diupdate",
            "title": "DONE OPEN FT CS RASY",
            "open_by": "@rrassyaaaa",
            "pay_link": "https://t.me/+r-dDf3CxAHgzNGVl",
            "rules_link": "https://t.me/+LHr8jRVQHsszZGJl",
            "owners": [] 
        }

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load()

# Setup default keys
if "title" not in data: data["title"] = "DONE OPEN FT CS RASY"
if "open_by" not in data: data["open_by"] = "@rrassyaaaa"
if "pay_link" not in data: data["pay_link"] = "https://t.me/+r-dDf3CxAHgzNGVl"
if "rules_link" not in data: data["rules_link"] = "https://t.me/+LHr8jRVQHsszZGJl"
if "owners" not in data: data["owners"] = []
save(data)

def is_authorized_owner(message):
    user_id = message.from_user.id if message.from_user else 0
    return user_id == SUPER_ADMIN_ID or user_id in data.get("owners", [])

def get_player_name(reply_message):
    user = reply_message.from_user
    if user.username:
        return f"@{user.username}"
    return user.first_name

def get_wib_time():
    utc_now = datetime.utcnow()
    wib_now = utc_now + timedelta(hours=7)
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    return wib_now.strftime(f"{days[wib_now.weekday()]}, %d-%m-%Y %H:%M WIB")

def generate_bracket_text():
    semi, final, winner = data["semi"], data["final"], data["winner"]
    return f"""🏆  {data['title']}  🏆
━━━━━━━━━━━━━━━━━━━━
🕒 WAKTU UPDATE
└ {data.get('last_update', 'Belum pernah diupdate')}

👑 OPEN BY
└ {data['open_by']}

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
by {data['open_by']}"""

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id, f"👋 Welcome {user.first_name}\nngentot stay cokkk fastt inii 🔥")

@bot.channel_post_handler(func=lambda message: True)
@bot.message_handler(func=lambda message: True)
def handle_text(message):
    global data, last_main_message_id
    
    msg_text = message.text.strip() if message.text else ""
    msg_lower = msg_text.lower()
    user_id = message.from_user.id if message.from_user else 0
    
    # ─── FITUR AUTOMATION TRIGGER BROADCAST ───
    if msg_lower != 'p' and msg_lower != '/bc' and msg_text != '':
        last_main_message_id = message.message_id
    
    if msg_lower == 'p':
        if user_id != 0 and user_id != SUPER_ADMIN_ID: return
        if last_main_message_id is not None:
            try:
                bot.send_message(message.chat.id, "/bc", reply_to_message_id=last_main_message_id)
                bot.delete_message(message.chat.id, message.message_id)
            except: pass
        return

    # ─── COMMANDS ───
    if msg_lower == "pot": return bot.reply_to(message, generate_bracket_text())
    if msg_lower == "pay": return bot.reply_to(message, f"𝐏𝐀𝐘𝐌𝐄𝐍𝐓!! : {data['pay_link']}")
    if msg_lower == "rules": return bot.reply_to(message, f"𝐑𝐔𝐋𝐄𝐒 𝐁𝐘 𝐑𝐀𝐒𝐘 : {data['rules_link']}")

    if msg_lower.startswith(("addowner ", "delowner ")) or msg_lower == "listowner":
        if user_id != SUPER_ADMIN_ID: return bot.reply_to(message, "❌ Cuma Rasya yang bisa pake ini!")
        if msg_lower.startswith("addowner "):
            tid = int(msg_text.split()[1])
            if tid not in data["owners"]: data["owners"].append(tid); save(data)
            return bot.reply_to(message, "✅ Sukses!")
        if msg_lower.startswith("delowner "):
            tid = int(msg_text.split()[1])
            if tid in data["owners"]: data["owners"].remove(tid); save(data)
            return bot.reply_to(message, "❌ Akses dicabut!")
        return bot.reply_to(message, f"👑 *OWNERS*:\n├ `{SUPER_ADMIN_ID}`\n" + "\n".join([f"├ `{oid}`" for oid in data["owners"]]), parse_mode="Markdown")

    if not is_authorized_owner(message): return

    if msg_lower.startswith("set"):
        parts = msg_text.split(" ", 1)
        if len(parts) > 1:
            cmd, val = parts[0], parts[1]
            if cmd == "settitle": data["title"] = val
            elif cmd == "setowner": data["open_by"] = val
            elif cmd == "setpay": data["pay_link"] = val
            elif cmd == "setrules": data["rules_link"] = val
            save(data)
            return bot.reply_to(message, f"✅ Updated: {cmd}")

    if msg_lower == "clear":
        data["semi"] = [None]*4; data["final"] = [None]*2; data["winner"] = None; data["last_update"] = get_wib_time(); save(data)
        return bot.reply_to(message, "✅ Reset!")

    if msg_lower in ["d1", "d2", "d3", "d4", "f1", "f2", "win"]:
        if not message.reply_to_message: return bot.reply_to(message, "❌ Reply player dulu!")
        name = get_player_name(message.reply_to_message)
        data["last_update"] = get_wib_time()
        idx = {"d1": 0, "d2": 1, "d3": 2, "d4": 3}
        if msg_lower in idx: data["semi"][idx[msg_lower]] = name
        elif msg_lower == "f1": data["final"][0] = name
        elif msg_lower == "f2": data["final"][1] = name
        elif msg_lower == "win": data["winner"] = name
        save(data)
        bot.reply_to(message, "✅ Data diupdate!")

print("Bot aktif...")
bot.infinity_polling()
        
