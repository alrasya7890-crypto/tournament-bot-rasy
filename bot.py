import telebot
import json
import os
from datetime import datetime, timedelta

# Mengambil variabel berdasarkan "KEY" yang lu input di tab Variables Railway
TOKEN = os.getenv("TELEGRAM_TOKEN")
SUPER_ADMIN_ID = int(os.getenv("OWNER_ID")) # ID Lu (Rasya) dikunci sebagai pembuat bot

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "data.json"

# Variabel memori sementara untuk mencatat ID pesan utama paling baru (fitur Auto Broadcast)
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

# Memastikan key baru selalu ada di database lama biar gak error
if "title" not in data: data["title"] = "DONE OPEN FT CS RASY"
if "open_by" not in data: data["open_by"] = "@rrassyaaaa"
if "pay_link" not in data: data["pay_link"] = "https://t.me/+r-dDf3CxAHgzNGVl"
if "rules_link" not in data: data["rules_link"] = "https://t.me/+LHr8jRVQHsszZGJl"
if "owners" not in data: data["owners"] = []
save(data)

# Fungsi cek apakah user adalah Super Admin (Lu) atau Owner Tambahan (Pembeli)
def is_authorized_owner(message):
    user_id = message.from_user.id
    return user_id == SUPER_ADMIN_ID or user_id in data.get("owners", [])

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

# Fungsi untuk generate tampilan bracket estetik dinamis sesuai settingan
def generate_bracket_text():
    semi = data["semi"]
    final = data["final"]
    winner = data["winner"]
    last_update = data.get("last_update", "Belum pernah diupdate")
    title = data.get("title", "DONE OPEN FT CS RASY")
    open_by = data.get("open_by", "@rrassyaaaa")
    
    text = f"""🏆  {title}  🏆
━━━━━━━━━━━━━━━━━━━━

🕒 WAKTU UPDATE
└ {last_update}

👑 OPEN BY
└ {open_by}

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
by {open_by}"""
    return text

# ========== WELCOME CHAT MEMBER ==========

@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(
            message.chat.id,
            f"👋 Welcome {user.first_name}\nngentot stay cokkk fastt inii 🔥"
        )

# ========== HANDLER SEMUA PERINTAH BERBASIS TEKS (MENDUKUNG CHANNEL & GRUP) ==========

@bot.channel_post_handler(func=lambda message: True) # Menangkap chat jika bot ditaruh di Saluran/Channel
@bot.message_handler(func=lambda message: True)       # Menangkap chat di Grup atau PC
def handle_text(message):
    global data, last_main_message_id  
    
    msg_text = message.text.strip() if message.text else ""
    msg_lower = msg_text.lower()
    user_id = message.from_user.id if message.from_user else None
    
    # ─── FITUR AUTOMATION TRIGGER BROADCAST (ANTI SPAM & AUTO TARGET) ───
    # Jika ada pesan teks/media masuk yang BUKAN perintah pemicu, simpan ID-nya sebagai target pesan utama terbaru
    if msg_lower != 'p' and msg_lower != '/bc' and msg_text != '':
        last_main_message_id = message.message_id
        # Biarkan proses berlanjut ke bawah untuk mengecek command turnamen lainnya
    
    # Eksekusi pemicu otomatis jika LU (Super Admin) ketik 'p'
    if msg_lower == 'p':
        # Fitur ini di-lock khusus untuk ID lu agar member/orang lain gak bisa sembarangan nge-trigger
        if user_id and user_id != SUPER_ADMIN_ID:
            return
            
        if last_main_message_id is not None:
            try:
                # Kirim teks /bc tepat dengan me-reply pesan utama yang sudah dikunci
                bot.send_message(
                    chat_id=message.chat.id,
                    text="/bc",
                    reply_to_message_id=last_main_message_id
                )
                # Hapus huruf 'p' yang lu ketik biar saluran tetap rapi dan bersih
                bot.delete_message(message.chat.id, message.message_id)
            except Exception as e:
                print(f"Gagal memproses auto-reply /bc: {e}")
        return # Keluar dari fungsi agar tidak memicu error perintah di bawah

    # ─── 1. PERINTAH UMUM (Bisa diakses siapapun di grup) ───
    if msg_lower == "pot":
        return bot.reply_to(message, generate_bracket_text())
    elif msg_lower == "pay":
        return bot.reply_to(message, f"𝐏𝐀𝐘𝐌𝐄𝐍𝐓!! : {data['pay_link']}")
    elif msg_lower == "rules":
        return bot.reply_to(message, f"𝐑𝐔𝐋𝐄𝐒 𝐁𝐘 𝐑𝐀𝐒𝐘 : {data['rules_link']}")

    # ─── 2. PERINTAH KHUSUS SUPER ADMIN ONLY (Cuma Lu/Rasya yang bisa pake) ───
    if msg_lower.startswith("addowner "):
        if user_id != SUPER_ADMIN_ID:
            return bot.reply_to(message, "❌ Perintah ini cuma bisa dipake sama Developer utama (Rasya) cok!")
        try:
            target_id = int(msg_text[9:].strip())
            if target_id not in data["owners"]:
                data["owners"].append(target_id)
                save(data)
                return bot.reply_to(message, f"✅ Sukses! ID `{target_id}` sekarang resmi jadi Owner bot.", parse_mode="Markdown")
            else:
                return bot.reply_to(message, "ℹ️ ID itu udah terdaftar jadi owner sebelumnya.")
        except ValueError:
            return bot.reply_to(message, "❌ Format salah. Contoh: `addowner 12345678`")

    elif msg_lower.startswith("delowner "):
        if user_id != SUPER_ADMIN_ID:
            return bot.reply_to(message, "❌ Perintah ini cuma bisa dipake sama Developer utama (Rasya) cok!")
        try:
            target_id = int(msg_text[9:].strip())
            if target_id in data["owners"]:
                data["owners"].remove(target_id)
                save(data)
                return bot.reply_to(message, f"❌ Akses Owner untuk ID `{target_id}` berhasil dicabut!", parse_mode="Markdown")
            else:
                return bot.reply_to(message, "ℹ️ ID tersebut emang gak ada di daftar owner.")
        except ValueError:
            return bot.reply_to(message, "❌ Format salah. Contoh: `delowner 12345678`")

    elif msg_lower == "listowner":
        if user_id != SUPER_ADMIN_ID:
            return bot.reply_to(message, "❌ Perintah ini cuma bisa dipake sama Developer utama (Rasya) cok!")
        list_id = "\n".join([f"├ `{oid}`" for oid in data["owners"]])
        return bot.reply_to(message, f"👑 *DAFTAR OWNER AKTIF*:\n├ `{SUPER_ADMIN_ID}` (Dev Utama)\n{list_id or '├ Gak ada owner tambahan'}", parse_mode="Markdown")

    # ─── 3. PERINTAH KHUSUS OWNER (Lu + Pembeli Lu yang udah di-addowner) ───
    if not is_authorized_owner(message):
        if msg_lower in ["d1", "d2", "d3", "d4", "f1", "f2", "win", "clear"] or msg_lower.startswith(("settitle ", "setowner ", "setpay ", "setrules ")):
            return bot.reply_to(message, "❌ Cuma owner yang bisa pake fitur ini cok!!")
        return

    # Logika FITUR SETTING / SETFITUR via Chat
    if msg_lower.startswith("settitle "):
        new_title = msg_text[9:].strip()
        data["title"] = new_title
        save(data)
        return bot.reply_to(message, f"✅ Judul turnamen berhasil diubah jadi:\n`{new_title}`", parse_mode="Markdown")

    elif msg_lower.startswith("setowner "):
        new_owner = msg_text[9:].strip()
        data["open_by"] = new_owner
        save(data)
        return bot.reply_to(message, f"✅ Owner di bracket berhasil diubah jadi:\n`{new_owner}`", parse_mode="Markdown")

    elif msg_lower.startswith("setpay "):
        new_pay = msg_text[7:].strip()
        data["pay_link"] = new_pay
        save(data)
        return bot.reply_to(message, f"✅ Link payment berhasil diubah jadi:\n{new_pay}")

    elif msg_lower.startswith("setrules "):
        new_rules = msg_text[9:].strip()
        data["rules_link"] = new_rules
        save(data)
        return bot.reply_to(message, f"✅ Link rules berhasil diubah jadi:\n{new_rules}")

    # Validasi Reply untuk input player turnamen
    if msg_lower in ["d1", "d2", "d3", "d4", "f1", "f2", "win"] and not message.reply_to_message:
        return bot.reply_to(message, f"❌ Reply dulu player buat ngisi {msg_text.upper()} blok!!")

    # Eksekusi reset bracket
    if msg_lower == "clear":
        data["semi"] = [None, None, None, None]
        data["final"] = [None, None]
        data["winner"] = None
        data["last_update"] = get_wib_time()
        save(data)
        return bot.reply_to(message, "✅ Bracket turnamen berhasil di-reset total jadi kosong!")

    # Jalankan update data player berdasarkan input owner
    name = get_player_name(message.reply_to_message)
    data["last_update"] = get_wib_time()

    if msg_lower == "d1":
        data["semi"][0] = name
        save(data)
        p1 = data["semi"][0] or "?"
        p2 = data["semi"][1] or "?"
        bot.reply_to(message, f"🏆 POT 1: {p1} vs {p2}")

    elif msg_lower == "d2":
        data["semi"][1] = name
        save(data)
        p1 = data["semi"][0] or "?"
        p2 = data["semi"][1] or "?"
        bot.reply_to(message, f"🏆 POT 1: {p1} vs {p2}")

    elif msg_lower == "d3":
        data["semi"][2] = name
        save(data)
        p3 = data["semi"][2] or "?"
        p4 = data["semi"][3] or "?"
        bot.reply_to(message, f"🏆 POT 2: {p3} vs {p4}")

    elif msg_lower == "d4":
        data["semi"][3] = name
        save(data)
        p3 = data["semi"][2] or "?"
        p4 = data["semi"][3] or "?"
        bot.reply_to(message, f"🏆 POT 2: {p3} vs {p4}")

    elif msg_lower == "f1":
        data["final"][0] = name
        save(data)
        f1_p = data["final"][0] or "?"
        f2_p = data["final"][1] or "?"
        bot.reply_to(message, f"🔥 FINAL: {f1_p} vs {f2_p}")

    elif msg_lower == "f2":
        data["final"][1] = name
        save(data)
        f1_p = data["final"][0] or "?"
        f2_p = data["final"][1] or "?"
        bot.reply_to(message, f"🔥 FINAL: {f1_p} vs {f2_p}")

    elif msg_lower == "win":
        data["winner"] = name
        save(data)
        bot.reply_to(message, f"👑 PEMENANG TURNAMEN MALAM INI: {name} !! 🔥")

print("Bot aktif...")
bot.infinity_polling()
        
