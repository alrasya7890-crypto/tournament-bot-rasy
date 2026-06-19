import telebot
import json
import os

TOKEN = os.getenv("8935590480:AAFPrBIZBpLLL5GlGFUrvuOi0zAMGVKwu4o")
OWNER_ID = int(os.getenv("8266296395"))

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
