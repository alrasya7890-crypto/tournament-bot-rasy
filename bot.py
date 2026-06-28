import telebot
import json
import os
import asyncio
import threading
import requests
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon import events

# ════════════════════════════════════════════
#           BAGIAN 1: KONFIGURASI AWAL
#
# Isi di Railway > Variables:
#   TELEGRAM_TOKEN  → token bot dari @BotFather
#   OWNER_ID        → Telegram ID lo (angka)
#   API_ID          → dari my.telegram.org
#   API_HASH        → dari my.telegram.org
#   SESSION_STRING  → string sesi Telethon akun lo
#   CHANNEL_ID      → username/ID saluran lo (contoh: @namasaluran)
# ════════════════════════════════════════════
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID_ENV = os.getenv("OWNER_ID")
SUPER_ADMIN_ID = int(OWNER_ID_ENV) if (OWNER_ID_ENV and OWNER_ID_ENV.isdigit()) else 0

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")
CHANNEL_ID = os.getenv("CHANNEL_ID")  # ← username/ID saluran lo, isi di Railway Variables

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

telebot.apihelper.CONNECT_TIMEOUT = 90
telebot.apihelper.READ_TIMEOUT = 90

# ════════════════════════════════════════════
#        BAGIAN 2: VARIABEL GLOBAL SPAM & AUTOBC
#
# auto_spam_aktif → on/off fitur spam BC ke bot target
# pesan_bc        → teks yang dikirim ke bot target
# autobc_aktif    → on/off fitur auto-reply di saluran
# teks_autobc     → teks yang direply ke setiap pesan di saluran
# autobc_client   → instance Telethon yang lagi jalan untuk autobc
# ════════════════════════════════════════════
auto_spam_aktif = False
pesan_bc = ""

autobc_aktif = False
teks_autobc = ""
autobc_client = None  # Simpan client Telethon autobc biar bisa dimatiin dari luar

# ════════════════════════════════════════════
#        BAGIAN 3: DEFAULT SETTINGS TAMPILAN
#
# Nilai awal tampilan POT di grup.
# Ganti langsung di sini kalau mau ubah default:
#   title      → judul yang muncul di atas tampilan POT
#   open_by    → nama yang muncul di "OPEN BY"
#   pay_link   → link grup/channel pembayaran
#   rules_link → link grup/channel rules
# ════════════════════════════════════════════
def get_default_owner_settings(user_id, username="@"):
    return {
        "title": "DONE OPEN FT CS RASY",
        "open_by": username,
        "pay_link": "https://t.me/+r-dDf3CxAHgzNGVl",
        "rules_link": "https://t.me/+LHr8jRVQHsszZGJl",
    }

# ════════════════════════════════════════════
#        BAGIAN 4: DEFAULT DATA BRACKET
#
# Struktur awal bracket per grup.
# semi  → 4 slot [d1, d2, d3, d4]
# final → 2 slot [f1, f2]
# winner → pemenang [win]
# ════════════════════════════════════════════
def get_default_bracket_data():
    return {
        "semi": [None, None, None, None],
        "final": [None, None],
        "winner": None,
        "last_update": "Belum pernah diupdate"
    }

# ════════════════════════════════════════════
#        BAGIAN 5: DATABASE (LOAD & SAVE)
#
# Data disimpan di data.json lokal.
# CATATAN: Reset tiap redeploy di Railway.
# ════════════════════════════════════════════
def load():
    try:
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            if "owner_settings" not in data: data["owner_settings"] = {}
            if "brackets" not in data: data["brackets"] = {}
            if "target_bots" not in data: data["target_bots"] = []
            return data
    except:
        return {"owner_settings": {}, "brackets": {}, "target_bots": []}

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load()

# ════════════════════════════════════════════
#      BAGIAN 6: LOOP UTAMA AUTO-SPAM BC
#
# Kirim "/bc [pesan]" ke semua bot target tiap 3 detik.
# Otomatis mati setelah 20 menit dan kirim notif ke lo.
#
# Ubah timedelta(minutes=20) → ganti durasi
# Ubah asyncio.sleep(3) → ganti jeda antar kiriman
# ════════════════════════════════════════════
async def run_userbot_loop():
    global auto_spam_aktif, pesan_bc, db

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.connect()

    waktu_selesai = datetime.now() + timedelta(minutes=20)  # ← Ganti durasi spam di sini
    print(f"[Spam] Dimulai. Mati pada: {waktu_selesai.strftime('%H:%M:%S')}")

    jumlah_terkirim = 0

    while auto_spam_aktif:
        if datetime.now() >= waktu_selesai:
            auto_spam_aktif = False
            try:
                notif_text = (
                    f"✅ *SPAM SELESAI OTOMATIS!*\n\n"
                    f"⏱ Durasi: 20 menit penuh\n"
                    f"📨 Total terkirim: {jumlah_terkirim} pesan\n"
                    f"🕐 Selesai: {datetime.now().strftime('%H:%M:%S')}"
                )
                requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={"chat_id": SUPER_ADMIN_ID, "text": notif_text, "parse_mode": "Markdown"},
                    timeout=15
                )
            except Exception as e:
                print(f"[Notif] Gagal: {e}")
            break

        db = load()
        daftar_bot = db.get("target_bots", [])

        if not daftar_bot:
            await asyncio.sleep(5)
            continue

        for bot_username in daftar_bot:
            if datetime.now() >= waktu_selesai or not auto_spam_aktif:
                auto_spam_aktif = False
                break
            try:
                await client.send_message(bot_username, f"/bc {pesan_bc}")
                print(f"[Spam] Sukses ke {bot_username}")
                jumlah_terkirim += 1
            except Exception as e:
                print(f"[Spam] Gagal ke {bot_username}: {e}")
            await asyncio.sleep(3)  # ← Ganti jeda antar bot di sini

    await client.disconnect()
    print("[Spam] Selesai, disconnect.")

def start_timer_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_userbot_loop())
    loop.close()

# ════════════════════════════════════════════
#      BAGIAN 7: AUTOBC — MONITOR SALURAN
#
# Userbot monitor saluran CHANNEL_ID.
# Kalau lo reply pesan di saluran dengan "autobc",
# userbot reply pesan itu dengan /bc tiap 3 detik
# selama 20 menit lalu notif lo.
#
# Ubah timedelta(minutes=20) → ganti durasi
# Ubah asyncio.sleep(3) → ganti jeda antar reply
# ════════════════════════════════════════════
async def run_autobc_loop():
    global autobc_aktif, teks_autobc

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.connect()

    print(f"[AutoBC] Userbot standby monitor saluran {CHANNEL_ID}...")

    @client.on(events.NewMessage(chats=CHANNEL_ID))
    async def handler(event):
        global autobc_aktif, teks_autobc

        # Cek kalau pesan itu reply dari lo dan isinya "autobc"
        if not event.is_reply: return
        if event.sender_id != SUPER_ADMIN_ID: return

        msg = event.message.message.strip()
        if not msg.lower().startswith("autobc"): return
        if autobc_aktif: return

        parts = msg.split(" ", 1)
        teks_autobc = parts[1] if len(parts) > 1 else pesan_bc

        # Ambil ID pesan yang di-reply
        reply_msg = await event.get_reply_message()
        target_message_id = reply_msg.id

        autobc_aktif = True
        waktu_selesai = datetime.now() + timedelta(minutes=20)  # ← Ganti durasi di sini
        jumlah_reply = 0

        print(f"[AutoBC] Triggered! Mulai reply ke message_id {target_message_id}")

        # Kirim notif mulai ke lo
        try:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={
                    "chat_id": SUPER_ADMIN_ID,
                    "text": f"📣 *AUTOBC AKTIF!*\n💬 Teks: `/bc {teks_autobc}`\n⏱ Jeda: 3 detik\n🛑 Durasi: 20 menit",
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
        except: pass

        while autobc_aktif and datetime.now() < waktu_selesai:
            try:
                await client.send_message(
                    CHANNEL_ID,
                    f"/bc {teks_autobc}",
                    reply_to=target_message_id
                )
                jumlah_reply += 1
                print(f"[AutoBC] Reply ke-{jumlah_reply} terkirim")
            except Exception as e:
                print(f"[AutoBC] Gagal: {e}")

            await asyncio.sleep(5)  # ← Ganti jeda di sini

        autobc_aktif = False

        # Notif selesai
        try:
            requests.post(
                f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                data={
                    "chat_id": SUPER_ADMIN_ID,
                    "text": f"✅ *AUTOBC SELESAI!*\n💬 Total reply: {jumlah_reply}\n🕐 Selesai: {datetime.now().strftime('%H:%M:%S')}",
                    "parse_mode": "Markdown"
                },
                timeout=10
            )
        except: pass

    await client.run_until_disconnected()
    await client.disconnect()

def start_autobc_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_autobc_loop())
    loop.close()

# ════════════════════════════════════════════
#     BAGIAN 8: AMBIL SETTINGS OWNER GRUP
# ════════════════════════════════════════════
def get_group_owner_settings(chat_id):
    fallback_settings = get_default_owner_settings(SUPER_ADMIN_ID, "@rrassyaaaa")
    try:
        admins = bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id == SUPER_ADMIN_ID:
                admin_id_str = str(admin.user.id)
                if admin_id_str not in db["owner_settings"]:
                    username = f"@{admin.user.username}" if admin.user.username else admin.user.first_name
                    db["owner_settings"][admin_id_str] = get_default_owner_settings(admin.user.id, username)
                    save(db)
                return db["owner_settings"][admin_id_str]
    except:
        pass
    return fallback_settings

# ════════════════════════════════════════════
#        BAGIAN 9: WELCOME NEW MEMBER
#
# Ganti teks di bot.send_message buat ubah pesan welcome.
# ════════════════════════════════════════════
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id, f"👋 Welcome {user.first_name}\nngentot stay cokkk fastt inii 🔥")

# ════════════════════════════════════════════
#     BAGIAN 10: HANDLER PESAN TEKS UTAMA
# ════════════════════════════════════════════
@bot.message_handler(content_types=['text', 'sticker', 'video', 'document', 'animation', 'photo'])
def handle_text(message):
    global db, auto_spam_aktif, pesan_bc, autobc_aktif, teks_autobc

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

    # ── PRIVATE CHAT ─────────────────────────────────
    if message.chat.type == "private":

        if user_id != SUPER_ADMIN_ID:
            return bot.reply_to(message, "❌ Bot ini private, khusus owner aja.")

        # ── PERINTAH: FITUR
        if msg_lower == "fitur":
            teks_fitur = (
                "📋 *DAFTAR FITUR & CARA PAKAI BOT*\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "📢 *SPAM BC KE BOT TARGET*\n"
                "┌ `start_auto [teks]` → Mulai spam ke semua bot target\n"
                "├ `stop_auto` → Hentikan spam paksa\n"
                "└ Auto berhenti & notif setelah 20 menit\n\n"

                "📣 *AUTO-REPLY DI SALURAN*\n"
                "┌ `startautobc` → Aktifkan userbot standby monitor saluran\n"
                "├ Reply pesan di saluran dengan `autobc` → userbot reply /bc tiap 3 detik\n"
                "├ `stopautobc` → Hentikan autobc paksa\n"
                "└ Auto berhenti & notif setelah 20 menit\n\n"

                "🤖 *MANAJEMEN BOT TARGET*\n"
                "┌ `addtargetbot @username` → Tambah bot target\n"
                "├ `deltargetbot @username` → Hapus bot target\n"
                "└ `listtargetbot` → Lihat semua bot target\n\n"

                "⚙️ *SETTING TAMPILAN POT DI GRUP*\n"
                "┌ `settitle [teks]` → Ganti judul POT\n"
                "├ `setowner [nama]` → Ganti nama open by\n"
                "├ `setpay [link]` → Ganti link pembayaran\n"
                "└ `setrules [link]` → Ganti link rules\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n"
                "📊 *PERINTAH DI GRUP*\n"
                "┌ `pot` → Tampilkan bracket turnamen\n"
                "├ `pay` → Tampilkan link pembayaran\n"
                "├ `rules` → Tampilkan link rules\n"
                "├ `clear` → Reset bracket grup\n"
                "├ Reply player + `d1`/`d2`/`d3`/`d4` → Set slot semi final\n"
                "├ Reply player + `f1`/`f2` → Set slot final\n"
                "└ Reply player + `win` → Set pemenang"
            )
            return bot.reply_to(message, teks_fitur, parse_mode="Markdown")

        # ── PERINTAH: START AUTO SPAM BC
        if msg_lower.startswith("start_auto"):
            parts = msg_text.split(" ", 1)
            if not db.get("target_bots"):
                return bot.reply_to(message, "❌ Daftar bot target kosong! Tambah dulu pake `addtargetbot`.")
            if auto_spam_aktif:
                return bot.reply_to(message, "⚠️ Spam lagi jalan. Ketik `stop_auto` dulu.")
            pesan_bc = parts[1] if len(parts) > 1 else ""
            auto_spam_aktif = True
            threading.Thread(target=start_timer_thread, daemon=True).start()
            return bot.reply_to(message,
                f"🚀 *SPAM AKTIF!*\n"
                f"📝 Teks: `/bc {pesan_bc}`\n"
                f"⏱ Jeda: 3 detik antar bot\n"
                f"🛑 Durasi: 20 menit lalu auto-mati\n"
                f"📬 Lo bakal dinotif otomatis kalau udah selesai!",
                parse_mode="Markdown"
            )

        # ── PERINTAH: STOP AUTO SPAM BC
        if msg_lower == "stop_auto":
            if not auto_spam_aktif:
                return bot.reply_to(message, "⚠️ Spam emang lagi gak aktif.")
            auto_spam_aktif = False
            return bot.reply_to(message, "🛑 *Spam berhasil dihentikan paksa!*", parse_mode="Markdown")

        # ── PERINTAH: STARTAUTOBC
        # Jalankan userbot standby monitor saluran.
        # Setelah aktif, reply pesan di saluran dengan "autobc"
        # buat trigger userbot reply /bc ke pesan itu tiap 3 detik
        if msg_lower == "startautobc":
            if autobc_aktif:
                return bot.reply_to(message, "⚠️ AutoBC lagi jalan.")
            threading.Thread(target=start_autobc_thread, daemon=True).start()
            return bot.reply_to(message,
                "📡 *Userbot standby monitor saluran!*\n\n"
                "Sekarang pergi ke saluran, reply pesan yang mau di-BC dengan `autobc` buat mulai.",
                parse_mode="Markdown"
            )

        # ── PERINTAH: STOPAUTOBC
        # Hentikan autobc paksa sebelum 20 menit habis
        if msg_lower == "stopautobc":
            if not autobc_aktif:
                return bot.reply_to(message, "⚠️ AutoBC emang lagi gak aktif.")
            autobc_aktif = False
            return bot.reply_to(message, "🛑 *AutoBC dihentikan paksa!*", parse_mode="Markdown")

        # ── PERINTAH: MANAJEMEN BOT TARGET
        if msg_lower.startswith(("addtargetbot", "deltargetbot")) or msg_lower == "listtargetbot":
            parts = msg_text.split()

            if msg_lower.startswith("addtargetbot"):
                if len(parts) < 2: return bot.reply_to(message, "❌ Contoh: `addtargetbot @username_bot`")
                b_user = parts[1] if parts[1].startswith("@") else f"@{parts[1]}"
                if b_user not in db["target_bots"]:
                    db["target_bots"].append(b_user)
                    save(db)
                    return bot.reply_to(message, f"✅ `{b_user}` berhasil ditambah ke target!")
                return bot.reply_to(message, "⚠️ Bot itu udah ada di daftar.")

            if msg_lower.startswith("deltargetbot"):
                if len(parts) < 2: return bot.reply_to(message, "❌ Contoh: `deltargetbot @username_bot`")
                b_user = parts[1] if parts[1].startswith("@") else f"@{parts[1]}"
                if b_user in db["target_bots"]:
                    db["target_bots"].remove(b_user)
                    save(db)
                    return bot.reply_to(message, f"❌ `{b_user}` dihapus dari target!")
                return bot.reply_to(message, "❌ Bot itu gak ada di daftar.")

            if not db["target_bots"]: return bot.reply_to(message, "🤖 Target bot masih kosong.")
            return bot.reply_to(message, "🤖 *TARGET BOT*:\n" + "\n".join([f"├ `{b}`" for b in db["target_bots"]]), parse_mode="Markdown")

        # ── PERINTAH: SETTING TAMPILAN POT
        if msg_lower.startswith("set"):
            parts = msg_text.split(" ", 1)
            if len(parts) > 1:
                cmd, val = parts[0], parts[1]
                if str_user_id not in db["owner_settings"]:
                    db["owner_settings"][str_user_id] = get_default_owner_settings(user_id)
                if cmd == "settitle": db["owner_settings"][str_user_id]["title"] = val
                elif cmd == "setowner": db["owner_settings"][str_user_id]["open_by"] = val
                elif cmd == "setpay": db["owner_settings"][str_user_id]["pay_link"] = val
                elif cmd == "setrules": db["owner_settings"][str_user_id]["rules_link"] = val
                save(db)
                return bot.reply_to(message, f"✅ Setting `{cmd}` berhasil diupdate!")

        # ── PERINTAH: HELP
        if msg_lower in ["/start", "/help", "menu", "help"]:
            return bot.reply_to(message, "ℹ️ Ketik `fitur` buat lihat semua perintah!", parse_mode="Markdown")

        return

    # ── GRUP CHAT ────────────────────────────────────
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

    if user_id != SUPER_ADMIN_ID: return

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
            bot.reply_to(message, f"✅ Data Updated!\n\n🔴 *SEMI FINAL SLOT 1 READY*:\n👉 {semi[0]}  vs  {semi[1]}", parse_mode="Markdown")
        elif msg_lower in ["d3", "d4"] and semi[2] and semi[3]:
            bot.reply_to(message, f"✅ Data Updated!\n\n🔴 *SEMI FINAL SLOT 2 READY*:\n👉 {semi[2]}  vs  {semi[3]}", parse_mode="Markdown")
        else:
            bot.reply_to(message, "✅ Data Bracket Diupdate!")

# ════════════════════════════════════════════
#        BAGIAN 11: JALANKAN BOT
# ════════════════════════════════════════════
if __name__ == "__main__":
    print("Bot aktif...")
    try:
        bot.remove_webhook()
        bot.infinity_polling(skip_pending=True)
    except Exception as e:
        print(f"Error saat polling: {e}")

