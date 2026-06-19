import telebot
import json
import os

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
            "winner": None
        }

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

data = load()

def is_owner(message):
    return message.from_user.id == OWNER_ID

# ========== D1 - D4 (OWNER ONLY, REPLY) ==========

@bot.message_handler(commands=['d1'])
def d1(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Belum pay cok!!")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply dulu blok!!")

    name = message.reply_to_message.from_user.first_name
    data["semi"][0] = name
    save(data)
    bot.reply_to(message, f"🏆 {name} POT 1 PLAYER 1")

@bot.message_handler(commands=['d2'])
def d2(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Belum pay cok!!")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply dulu cok!!")

    name = message.reply_to_message.from_user.first_name
    data["semi"][1] = name
    save(data)
    bot.reply_to(message, f"🏆 {name} POT 1 PLAYER 2")

@bot.message_handler(commands=['d3'])
def d3(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Belum pay cok!!")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply dulu su!!")

    name = message.reply_to_message.from_user.first_name
    data["semi"][2] = name
    save(data)
    bot.reply_to(message, f"🏆 {name} POT 2 PLAYER 1")

@bot.message_handler(commands=['d4'])
def d4(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Belum pay cok!!")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply player")

    name = message.reply_to_message.from_user.first_name
    data["semi"][3] = name
    save(data)
    bot.reply_to(message, f"🏆 {name} POT 2 PLAYER 2")

# ========== FINAL ==========

@bot.message_handler(commands=['f1'])
def f1(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Cuma owner")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply player")

    name = message.reply_to_message.from_user.first_name
    data["final"][0] = name
    save(data)
    bot.reply_to(message, f"🔥 {name} FINAL PLAYER 1")

@bot.message_handler(commands=['f2'])
def f2(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Cuma owner")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply player")

    name = message.reply_to_message.from_user.first_name
    data["final"][1] = name
    save(data)
    bot.reply_to(message, f"🔥 {name} FINAL PLAYER 2")

# ========== WIN ==========

@bot.message_handler(commands=['win'])
def win(message):
    if not is_owner(message):
        return bot.reply_to(message, "❌ Cuma owner")

    if not message.reply_to_message:
        return bot.reply_to(message, "❌ Reply pemenang")

    winner = message.reply_to_message.from_user.first_name
    data["winner"] = winner
    save(data)

    bot.reply_to(message, f"🏆 {winner} MENANG!! 🔥")

# ========== POT VIEW ==========

@bot.message_handler(commands=['pot'])
def pot(message):
    semi = data["semi"]
    final = data["final"]

    # Dihapus validasi strict-nya biar bracket kosong tetep bisa diintip isinya
    text = f"""🏆 TOURNAMENT BRACKET

SEMI FINAL:
1️⃣ {semi[0] or "Belum ada"} vs {semi[1] or "Belum ada"}
2️⃣ {semi[2] or "Belum ada"} vs {semi[3] or "Belum ada"}

FINAL:
🔥 {final[0] or "Winner SF1"} vs {final[1] or "Winner SF2"}

WINNER:
👑 {data["winner"] or "???"}"""
    bot.reply_to(message, text)

# ========== WELCOME ==========

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(
            message.chat.id,
            f"👋 Welcome ngentod {user.first_name}\nStay cokkk fastt inii 🔥"
        )

print("Bot aktif...")
bot.infinity_polling()
