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

[ 🔴 **SEMI FINAL** ]
1️⃣ {semi[0] or "?"}  vs  {semi[1] or "?"}
2️⃣ {semi[2] or "?"}  vs  {semi[3] or "?"}

[ 🔥 **FINAL** ]
🏆 {final[0] or "Winner SF1"}  vs  {final[1] or "Winner SF2"}

──────────────────────

🏅 **PEMENANG**
👑  【 {winner or "?"} 】

╚══════════════════════════╝
*by @rrassyaaaa*"""
    return text

# ========== OWNER ONLY: CLEAR / RESET TOTAL ==========

@bot.message_handler(commands=['clear'])
def clear_bracket(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Cuma owner")
        
    global data
    data = {
        "semi": [None, None, None, None],
        "final": [None, None],
        "winner": None,
        "last_update": get_wib_time()
    }
    save(data)
    bot.reply_to(message, "✅ **Bracket turnamen berhasil di-reset total jadi kosong, Sya!**")

# ========== D1 - D4 (OWNER ONLY, REPLY) ==========

@bot.message_handler(commands=['d1'])
def d1(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Belum pay cok!!")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply dulu blok!!")

    name = get_player_name(message.reply_to_message)
    data["semi"][0] = name
    data["last_update"] = get_wib_time()
    save(data)
    bot.reply_to(message, f"🏆 {name} POT 1 PLAYER 1")

@bot.message_handler(commands=['d2'])
def d2(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Belum pay cok!!")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply dulu cok!!")

    name = get_player_name(message.reply_to_message)
    data["semi"][1] = name
    data["last_update"] = get_wib_time()
    save(data)
    bot.reply_to(message, f"🏆 {name} POT 1 PLAYER 2")

@bot.message_handler(commands=['d3'])
def d3(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Belum pay cok!!")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply dulu su!!")

    name = get_player_name(message.reply_to_message)
    data["semi"][2] = name
    data["last_update"] = get_wib_time()
    save(data)
    bot.reply_to(message, f"🏆 {name} POT 2 PLAYER 1")

@bot.message_handler(commands=['d4'])
def d4(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Belum pay cok!!")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply player")

    name = get_player_name(message.reply_to_message)
    data["semi"][3] = name
    data["last_update"] = get_wib_time()
    save(data)
    bot.reply_to(message, f"🏆 {name} POT 2 PLAYER 2")

# ========== FINAL ==========

@bot.message_handler(commands=['f1'])
def f1(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Cuma owner")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply player")

    name = get_player_name(message.reply_to_message)
    data["final"][0] = name
    data["last_update"] = get_wib_time()
    save(data)
    bot.reply_to(message, f"🔥 {name} FINAL PLAYER 1")

@bot.message_handler(commands=['f2'])
def f2(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Cuma owner")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply player")

    name = get_player_name(message.reply_to_message)
    data["final"][1] = name
    data["last_update"] = get_wib_time()
    save(data)
    bot.reply_to(message, f"🔥 {name} FINAL PLAYER 2")

# ========== WIN ==========

@bot.message_handler(commands=['win'])
def win(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Cuma owner")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply pemenang")

    winner = get_player_name(message.reply_to_message)
    data["winner"] = winner
    data["last_update"] = get_wib_time()
    save(data)

    bot.reply_to(message, f"🏆 {winner} MENANG!! 🔥")

# ========== SUPPORT /pot COMMAND ==========
@bot.message_handler(commands=['pot'])
def pot_command(message):
    bot.reply_to(message, generate_bracket_text(), parse_mode="Markdown")

# ========== WELCOME CHAT MEMBER ==========

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(
            message.chat.id,
            f"👋 Welcome ngentod {user.first_name}\nStay cokkk fastt inii 🔥"
        )

# ========== TEXT TRIGGER (POT TANPA /, PAY, RULES, & CUSTOM BACUTAN) ==========

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    msg_text = message.text.lower().strip()
    
    # 1. Custom Trigger buat kata "gc" berdasarkan kondisi isi POT
    if msg_text == "gc":
        # Kondisi A: Owner yang ngetik "gc" atau "f"
        if is_owner(message):
            return bot.reply_to(message, "GC TF COK CEPET MAIN ASU HAMA F -1 TINGGAL LU DOANG")
            
        # Kondisi B: Player umum yang ngetik "gc"
        semi = data["semi"]
        if semi[0] is None or semi[1] is None:
            # d1 dan d2 belum terisi penuh
            bot.reply_to(message, "lu kira atmin daritadi lagi ngapain? nyoli?")
        elif semi[2] is None or semi[3] is None:
            # d1 dan d2 sudah isi, tapi d3 atau d4 (pot 2) belum penuh
            bot.reply_to(message, "ya sabar tai, nunggu pot 2 -1 cok")
        else:
            # Semua d1 sampai d4 sudah terisi penuh
            bot.reply_to(message, "sabar kontol, memek lu")
            
    # 2. Kondisi tambahan kalau Owner ketik "f" doang
    elif msg_text == "f" and is_owner(message):
        bot.reply_to(message, "GC TF COK CEPET MAIN ASU HAMA F -1 TINGGAL LU DOANG")
        
    # 3. Trigger bawaan lama
    elif msg_text == "pot":
        bot.reply_to(message, generate_bracket_text(), parse_mode="Markdown")
    elif msg_text == "pay":
        bot.reply_to(message, "𝐏𝐀𝐘𝐌𝐄𝐍𝐓!! : https://t.me/+r-dDf3CxAHgzNGVl")
    elif msg_text == "rules":
        bot.reply_to(message, "𝐑𝐔𝐋𝐄𝐒 𝐁𝐘 𝐑𝐀𝐒𝐘 : https://t.me/+LHr8jRVQHsszZGJl")

print("Bot aktif...")
bot.infinity_polling()
    
