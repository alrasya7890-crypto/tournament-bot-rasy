import telebot
import json
import os
from datetime import datetime, timedelta

# Mengambil variabel berdasarkan "KEY" yang lu input di tab Variables Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID = int(os.getenv("OWNER_ID"))

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

def load():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "semi": [None, None, None, None],
            "final": [None, None],
            "winner": None,
            "last_update": "Belum pernah diupdate"
        }

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load()

def is_owner(message):
    return message.from_user.id == OWNER_ID

# Fungsi pembantu untuk mengambil username atau first_name player
def get_player_name(reply_message):
    user = reply_message.from_user
    if user.username:
        return f"@{user.username}"
    return user.first_name

# Fungsi mengambil waktu WIB (UTC +7) untuk info jam update
def get_wib_time():
    utc_now = datetime.utcnow()
    wib_now = utc_now + timedelta(hours=7)
    days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
    day_name = days[wib_now.weekday()]
    return wib_now.strftime(f"{day_name}, %d-%m-%Y %H:%M WIB")

# Fungsi untuk generate tampilan bracket estetik FT CS RASY
def generate_bracket_text():
    semi = data["semi"]
    final = data["final"]
    winner = data["winner"]
    last_update = data.get("last_update", "Belum pernah diupdate")
    
    text = f"""╔══════════════════════════╗
║ 🏆  『 **DONE OPEN FT CS RASY** 』  🏆 ║
╚══════════════════════════╝

🕒 **WAKTU UPDATE**
├ {last_update}

👑 **OPEN BY**
├ @rrassyaaaa

──────────────────────
📊 **BRACKET TURNAMEN**
──────────────────────

🔴 **SEMI FINAL**
1️⃣ {semi[0] or "?"}  vs  {semi[1] or "?"}
2️⃣ {semi[2] or "?"}  vs  {semi[3] or "?"}

🔥 **FINAL**
🏆 {final[0] or "?"}  vs  {final[1] or "?"}

──────────────────────

🏅 **PEMENANG**
👑  【 {winner or "?"} 】

╚══════════════════════════╝
*by @rrassyaaaa*"""
    return text

# ========== WELCOME CHAT MEMBER ==========

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(
            message.chat.id,
            f"👋 Welcome ngentod {user.first_name}\nStay cokkk fastt inii 🔥"
        )

# ========== HANDLER SEMUA PERINTAH BERBASIS TEKS (TANPA GARIS MIRING) ==========

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    msg_text = message.text.lower().strip()
    
    # 1. PERINTAH UMUM (Bisa diakses siapapun)
    if msg_text == "pot":
        return bot.reply_to(message, generate_bracket_text(), parse_mode="Markdown")
    elif msg_text == "pay":
        return bot.reply_to(message, "𝐏𝐀𝐘𝐌𝐄𝐍𝐓!! : https://t.me/+r-dDf3CxAHgzNGVl")
    elif msg_text == "rules":
        return bot.reply_to(message, "𝐑𝐔𝐋𝐄𝐒 𝐁𝐘 𝐑𝐀𝐒𝐘 : https://t.me/+LHr8jRVQHsszZGJl")

    # 2. PERINTAH KHUSUS OWNER ONLY (Kunci Mutlak)
    if not is_owner(message):
        if msg_text in ["d1", "d2", "d3", "d4", "f1", "f2", "win", "clear"]:
            return bot.reply_to(message, "❌ Cuma owner yang bisa atur bracket cok!!")
        return

    # Validasi Reply untuk input data (Kecuali command clear)
    if msg_text in ["d1", "d2", "d3", "d4", "f1", "f2", "win"] and not message.reply_to_message:
        return bot.reply_to(message, f"❌ Reply dulu player buat ngisi {message.text.upper()} blok!!")

    # Eksekusi logika masing-masing teks command owner
    if msg_text == "clear":
        global data
        data = {
            "semi": [None, None, None, None],
            "final": [None, None],
            "winner": None,
            "last_update": get_wib_time()
        }
        save(data)
        return bot.reply_to(message, "✅ **Bracket turnamen berhasil di-reset total jadi kosong, Sya!**")

    # Jalankan update data berdasarkan input owner
    name = get_player_name(message.reply_to_message)
    data["last_update"] = get_wib_time()

    if msg_text == "d1":
        data["semi"][0] = name
        save(data)
        p1 = data["semi"][0] or "?"
        p2 = data["semi"][1] or "?"
        bot.reply_to(message, f"🏆 **POT 1:** {p1} vs {p2}")

    elif msg_text == "d2":
        data["semi"][1] = name
        save(data)
        p1 = data["semi"][0] or "?"
        p2 = data["semi"][1] or "?"
        bot.reply_to(message, f"🏆 **POT 1:** {p1} vs {p2}")

    elif msg_text == "d3":
        data["semi"][2] = name
        save(data)
        p3 = data["semi"][2] or "?"
        p4 = data["semi"][3] or "?"
        bot.reply_to(message, f"🏆 **POT 2:** {p3} vs {p4}")

    elif msg_text == "d4":
        data["semi"][3] = name
        save(data)
        p3 = data["semi"][2] or "?"
        p4 = data["semi"][3] or "?"
        bot.reply_to(message, f"🏆 **POT 2:** {p3} vs {p4}")

    elif msg_text == "f1":
        data["final"][0] = name
        save(data)
        f1_p = data["final"][0] or "?"
        f2_p = data["final"][1] or "?"
        bot.reply_to(message, f"🔥 **FINAL:** {f1_p} vs {f2_p}")

    elif msg_text == "f2":
        data["final"][1] = name
        save(data)
        f1_p = data["final"][0] or "?"
        f2_p = data["final"][1] or "?"
        bot.reply_to(message, f"🔥 **FINAL:** {f1_p} vs {f2_p}")

    elif msg_text == "win":
        data["winner"] = name
        save(data)
        bot.reply_to(message, f"👑 **PEMENANG FT CS RASY MALAM INI:** {name} !! 🔥")

print("Bot aktif...")
bot.infinity_polling()
