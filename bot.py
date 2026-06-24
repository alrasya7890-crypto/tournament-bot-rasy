import telebot
import json
import os
import asyncio
import threading
from datetime import datetime, timedelta
from telethon import TelegramClient
from telethon.sessions import StringSession

# ════════════════════════════════════════════
#           BAGIAN 1: KONFIGURASI AWAL
# ════════════════════════════════════════════
TOKEN = os.getenv("TELEGRAM_TOKEN")
OWNER_ID_ENV = os.getenv("OWNER_ID")
SUPER_ADMIN_ID = int(OWNER_ID_ENV) if (OWNER_ID_ENV and OWNER_ID_ENV.isdigit()) else 0

API_ID = int(os.getenv("API_ID", 0))
API_HASH = os.getenv("API_HASH")
SESSION_STRING = os.getenv("SESSION_STRING")

bot = telebot.TeleBot(TOKEN)
DATA_FILE = "data.json"

telebot.apihelper.CONNECT_TIMEOUT = 90
telebot.apihelper.READ_TIMEOUT = 90

# ════════════════════════════════════════════
#        BAGIAN 2: VARIABEL GLOBAL SPAM
# ════════════════════════════════════════════
auto_spam_aktif = False
pesan_bc = ""
foto_bc = None  # File ID foto yang mau di-spam (None = mode teks aja)

# ════════════════════════════════════════════
#        BAGIAN 3: DEFAULT SETTINGS OWNER
#   (Edit di sini buat ganti nilai default
#    judul, link pay, dan link rules awal)
# ════════════════════════════════════════════
def get_default_owner_settings(user_id, username="@"):
    return {
        "title": "DONE OPEN FT CS RASY",    # ← Ganti judul default di sini
        "open_by": username,
        "pay_link": "https://t.me/+r-dDf3CxAHgzNGVl",    # ← Ganti link pay default
        "rules_link": "https://t.me/+LHr8jRVQHsszZGJl",  # ← Ganti link rules default
    }

# ════════════════════════════════════════════
#        BAGIAN 4: DEFAULT DATA BRACKET
#   (Struktur awal bracket turnamen per grup)
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
#   (Semua data disimpen di data.json lokal)
# ════════════════════════════════════════════
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
            "brackets": {},
            "target_bots": []
        }

def save(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

db = load()

# ════════════════════════════════════════════
#     BAGIAN 6: DOWNLOAD FOTO UNTUK SPAM
#   (Ambil foto dari Telegram jadi bytes
#    sebelum dikirim ke bot-bot target)
# ════════════════════════════════════════════
async def download_foto_bytes(file_id):
    try:
        file_info = bot.get_file(file_id)
        file_url = f"https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}"
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                return await resp.read()
    except Exception as e:
        print(f"[Userbot] Gagal download foto: {e}")
        return None

# ════════════════════════════════════════════
#      BAGIAN 7: LOOP UTAMA AUTO-SPAM
#   (Jalan di thread terpisah, kirim pesan/
#    foto ke semua bot target tiap 3 detik,
#    otomatis mati setelah 10 menit,         ← DIUBAH: 5 → 10 menit
#    lalu kirim notif ke Rasya)
# ════════════════════════════════════════════
async def run_userbot_loop():
    global auto_spam_aktif, pesan_bc, foto_bc, db, bot 

    client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
    await client.connect()

    waktu_selesai = datetime.now() + timedelta(minutes=10)
    print(f"[Userbot] Spam dimulai. Akan mati pada: {waktu_selesai.strftime('%H:%M:%S')}")

    # Download foto sekali di awal biar hemat bandwidth
    foto_bytes = None
    if foto_bc:
        foto_bytes = await download_foto_bytes(foto_bc)
        if foto_bytes:
            print("[Userbot] Foto berhasil didownload, siap dikirim!")
        else:
            print("[Userbot] Foto gagal didownload, fallback ke teks.")

    jumlah_terkirim = 0

        while auto_spam_aktif:
        if datetime.now() >= waktu_selesai:
            print("[Userbot] Waktu 10 menit habis! Auto-shutdown.")
            auto_spam_aktif = False

            # --- GANTI BLOK NOTIF YANG LAMA SAMA INI ---
            try:
                import requests
                print(f"[DEBUG] Admin ID yang terdeteksi: {SUPER_ADMIN_ID}") # Biar kita tau ID-nya bener apa nggak
                
                notif_text = (
                    f"✅ *SPAM SELESAI OTOMATIS!*\n\n"
                    f"⏱ Durasi: 10 menit penuh\n"
                    f"📨 Total terkirim: {jumlah_terkirim} pesan\n"
                    f"🕐 Selesai pada: {datetime.now().strftime('%H:%M:%S')}"
                )
                
                resp = requests.post(
                    f"https://api.telegram.org/bot{TOKEN}/sendMessage",
                    data={
                        "chat_id": SUPER_ADMIN_ID,
                        "text": notif_text,
                        "parse_mode": "Markdown"
                    },
                    timeout=15
                )
                print(f"[DEBUG] Respon Telegram: {resp.status_code} - {resp.text}")
            except Exception as e:
                print(f"[Notif] Gagal total! Error: {e}")
            # -------------------------------------------
            break

            
        db = load()
        daftar_bot = db.get("target_bots", [])

        if not daftar_bot:
            print("[Userbot] Daftar bot kosong, menunggu 5 detik...")
            await asyncio.sleep(5)
            continue

        for bot_username in daftar_bot:
            if datetime.now() >= waktu_selesai or not auto_spam_aktif:
                auto_spam_aktif = False
                break

            try:
                # Tahap 1: Kirim Foto (tanpa caption)
                if foto_bytes:
                    import io
                    bio = io.BytesIO(foto_bytes)
                    bio.name = "image.jpg"
                    await client.send_file(bot_username, file=bio, caption=None, force_document=False)
                    await asyncio.sleep(2) # Jeda manusiawi setelah kirim foto

                # Tahap 2: Kirim Perintah Teks
                await client.send_message(bot_username, f"/bc {pesan_bc}")
                print(f"[Userbot] Sukses spam ke {bot_username}")
                jumlah_terkirim += 1 

            except Exception as e:
                print(f"[Userbot] Gagal spam ke {bot_username}: {e}")

            await asyncio.sleep(5) # 5 Detik Min Jeda antar bot biar nggak kena Flood Wait

    await client.disconnect()
    print("[Userbot] Koneksi dimatikan, stand-by.")


def start_timer_thread():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_userbot_loop())
    loop.close()
    

    

# ════════════════════════════════════════════
#     BAGIAN 8: AMBIL SETTINGS OWNER GRUP
#   (Cek admin grup, ambil settings yang
#    udah diset pemilik bot di grup itu)
# ════════════════════════════════════════════
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

# ════════════════════════════════════════════
#        BAGIAN 9: WELCOME NEW MEMBER
# ════════════════════════════════════════════
@bot.message_handler(content_types=['new_chat_members'])
def welcome(message):
    for user in message.new_chat_members:
        bot.send_message(message.chat.id, f"👋 Welcome {user.first_name}\nngentot stay cokkk fastt inii 🔥")

# ════════════════════════════════════════════
#      BAGIAN 10: HANDLER FOTO (SET FOTO BC)
#   (Kirim foto + caption "setfoto" di PC
#    bot buat set foto yang mau di-spam)
# ════════════════════════════════════════════
@bot.message_handler(content_types=['photo'])
def handle_foto(message):
    global foto_bc
    if message.chat.type != "private": return
    if message.from_user.id != SUPER_ADMIN_ID: return

    caption = message.caption.strip().lower() if message.caption else ""
    if caption == "setfoto":
        foto_bc = message.photo[-1].file_id
        return bot.reply_to(message, "✅ Foto BC berhasil diset! `start_auto` sekarang bakal kirim foto ini.")

# ════════════════════════════════════════════
#     BAGIAN 11: HANDLER PESAN TEKS UTAMA
#   (Semua logika perintah teks ada di sini,
#    dibagi antara private chat dan grup)
# ════════════════════════════════════════════
@bot.message_handler(content_types=['text', 'sticker', 'video', 'document', 'animation'])
def handle_text(message):
    global db, auto_spam_aktif, pesan_bc, foto_bc

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

    # ── 11A. PRIVATE CHAT (PC BOT) ──────────────────
    if message.chat.type == "private":
        if user_id != SUPER_ADMIN_ID and user_id not in db["pembeli_list"]:
            return bot.reply_to(message, "❌ Lu belum punya lisensi pembeli. Hubungi Rasya buat sewa bot! 😉")

        if str_user_id not in db["owner_settings"]:
            username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            db["owner_settings"][str_user_id] = get_default_owner_settings(user_id, username)
            save(db)

        # ── PERINTAH: FITUR (daftar semua fitur bot) ──
        if msg_lower == "fitur":
            teks_fitur = (
                "📋 *DAFTAR FITUR & CARA PAKAI BOT*\n"
                "━━━━━━━━━━━━━━━━━━━━\n\n"

                "🖼 *SPAM FOTO / TEKS KE BOT TARGET*\n"
                "┌ Kirim foto + caption `setfoto` → Set foto yang mau di-spam\n"
                "├ `start_auto [teks]` → Mulai spam foto+teks ke semua bot target\n"
                "├ `start_auto` → Mulai spam teks kosong (atau foto aja kalau udah diset)\n"
                "├ `stop_auto` → Hentikan spam paksa sebelum 10 menit\n"
                "└ `clearfoto` → Hapus foto, balik ke mode teks aja\n\n"

                "🤖 *MANAJEMEN BOT TARGET*\n"
                "┌ `addtargetbot @username` → Tambah bot target ke daftar\n"
                "├ `deltargetbot @username` → Hapus bot target dari daftar\n"
                "└ `listtargetbot` → Lihat semua bot target yang terdaftar\n\n"

                "👑 *MANAJEMEN LISENSI PEMBELI*\n"
                "┌ `addlisensi [ID]` → Tambah pembeli baru pake Telegram ID\n"
                "├ `dellisensi [ID]` → Cabut lisensi pembeli\n"
                "└ `listlisensi` → Lihat semua pembeli aktif\n\n"

                "⚙️ *SETTING PROFIL OWNER*\n"
                "┌ `settitle [teks]` → Ganti judul di tampilan POT\n"
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
                "└ Reply player + `win` → Set pemenang\n\n"

                "━━━━━━━━━━━━━━━━━━━━\n"
                "ℹ️ Spam otomatis berhenti setelah 10 menit dan lo akan dinotif."
            )
            return bot.reply_to(message, teks_fitur, parse_mode="Markdown")

        # ── PERINTAH: START AUTO SPAM ──
        if msg_lower.startswith("start_auto"):
            if user_id != SUPER_ADMIN_ID:
                return bot.reply_to(message, "❌ Perintah ini khusus buat Rasya!")
            parts = msg_text.split(" ", 1)
            if not db.get("target_bots"):
                return bot.reply_to(message, "❌ Daftar bot target kosong! Tambah dulu pake `addtargetbot`.")
            if auto_spam_aktif:
                return bot.reply_to(message, "⚠️ Spam lagi jalan. Ketik `stop_auto` dulu.")

            pesan_bc = parts[1] if len(parts) > 1 else ""
            auto_spam_aktif = True
            threading.Thread(target=start_timer_thread, daemon=True).start()

            if foto_bc:
                return bot.reply_to(message, f"🚀 *SPAM FOTO+TEKS AKTIF!*\n📝 Caption: `/bc {pesan_bc}`\n🖼 Mode: Foto + Caption\n⏱ Jeda: 3 detik\n🛑 Durasi: 10 menit lalu auto-mati.\n\n📬 Lo bakal dinotif otomatis kalau udah selesai!", parse_mode="Markdown")
            else:
                return bot.reply_to(message, f"🚀 *SPAM TEKS AKTIF!*\n📝 Teks: `/bc {pesan_bc}`\n🖼 Mode: Teks aja\n⏱ Jeda: 3 detik\n🛑 Durasi: 10 menit lalu auto-mati.\n\n📬 Lo bakal dinotif otomatis kalau udah selesai!", parse_mode="Markdown")

        # ── PERINTAH: STOP AUTO SPAM ──
        if msg_lower == "stop_auto":
            if user_id != SUPER_ADMIN_ID: return bot.reply_to(message, "❌ Khusus buat Rasya!")
            if not auto_spam_aktif: return bot.reply_to(message, "⚠️ Spam emang lagi gak aktif.")
            auto_spam_aktif = False
            return bot.reply_to(message, "🛑 *Spam berhasil dihentikan paksa!*", parse_mode="Markdown")

        # ── PERINTAH: CLEAR FOTO BC ──
        if msg_lower == "clearfoto":
            if user_id != SUPER_ADMIN_ID: return bot.reply_to(message, "❌ Khusus buat Rasya!")
            foto_bc = None
            return bot.reply_to(message, "🗑 Foto BC dihapus. Spam balik ke mode teks aja.")

        # ── PERINTAH: MANAJEMEN BOT TARGET ──
        if msg_lower.startswith(("addtargetbot", "deltargetbot")) or msg_lower == "listtargetbot":
            if user_id != SUPER_ADMIN_ID: return bot.reply_to(message, "❌ Khusus buat Rasya!")
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

        # ── PERINTAH: MANAJEMEN LISENSI PEMBELI ──
        if msg_lower.startswith(("addpembeli", "delpembeli", "addlisensi", "dellisensi")) or msg_lower in ["listpembeli", "listlisensi"]:
            if user_id != SUPER_ADMIN_ID:
                return bot.reply_to(message, "❌ Cuma Rasya yang bisa akses lisensi!")

            parts = msg_text.split()

            if msg_lower.startswith(("addpembeli", "addlisensi")):
                if len(parts) < 2: return bot.reply_to(message, f"❌ Contoh: {parts[0]} 123456789")
                try:
                    tid = int(parts[1])
                    if tid not in db["pembeli_list"]: db["pembeli_list"].append(tid)
                    if str(tid) not in db["owner_settings"]: db["owner_settings"][str(tid)] = get_default_owner_settings(tid)
                    save(db)
                    return bot.reply_to(message, f"✅ ID `{tid}` sukses jadi pembeli resmi!")
                except ValueError: return bot.reply_to(message, "❌ ID harus angka!")

            if msg_lower.startswith(("delpembeli", "dellisensi")):
                if len(parts) < 2: return bot.reply_to(message, f"❌ Contoh: {parts[0]} 123456789")
                try:
                    tid = int(parts[1])
                    if tid in db["pembeli_list"]: db["pembeli_list"].remove(tid)
                    save(db)
                    return bot.reply_to(message, f"❌ Lisensi ID `{tid}` dicabut!")
                except ValueError: return bot.reply_to(message, "❌ ID harus angka!")

            return bot.reply_to(message, "👑 *PEMBELI AKTIF*:\n" + "\n".join([f"├ `{oid}`" for oid in db["pembeli_list"]]), parse_mode="Markdown")

        # ── PERINTAH: SETTING PROFIL OWNER ──
        if msg_lower.startswith("set"):
            parts = msg_text.split(" ", 1)
            if len(parts) > 1:
                cmd, val = parts[0], parts[1]
                if cmd == "settitle": db["owner_settings"][str_user_id]["title"] = val
                elif cmd == "setowner": db["owner_settings"][str_user_id]["open_by"] = val
                elif cmd == "setpay": db["owner_settings"][str_user_id]["pay_link"] = val
                elif cmd == "setrules": db["owner_settings"][str_user_id]["rules_link"] = val
                save(db)
                return bot.reply_to(message, f"✅ Setting `{cmd}` berhasil diupdate!")

        # ── PERINTAH: MENU HELP ──
        if msg_lower in ["/start", "/help", "menu", "help"]:
            return bot.reply_to(message, "ℹ️ Ketik `fitur` buat lihat semua fitur dan cara pakainya!", parse_mode="Markdown")

        return

            # ── 11B. GRUP CHAT ───────────────────────────────
    oset = get_group_owner_settings(chat_id)
    bdata = db["brackets"][str_chat_id]

    # ── PERINTAH GRUP: POT (tampilkan bracket) ──
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

    # ── PERINTAH GRUP: PAY & RULES ──
    if msg_lower == "pay": return bot.reply_to(message, f"𝐏𝐀𝐘𝐌𝐄𝐍𝐓!! : {oset['pay_link']}")
    if msg_lower == "rules": return bot.reply_to(message, f"𝐑𝐔𝐋𝐄𝐒 𝐁𝐘 𝐑𝐀𝐒𝐘 : {oset['rules_link']}")

    is_pembeli = user_id in db["pembeli_list"] or user_id == SUPER_ADMIN_ID
    if not is_pembeli: return

    # ── PERINTAH GRUP: CLEAR BRACKET ──
    if msg_lower == "clear":
        db["brackets"][str_chat_id] = get_default_bracket_data()
        save(db)
        return bot.reply_to(message, "✅ Bracket grup ini berhasil dikosongkan!")

    # ── PERINTAH GRUP: INPUT SLOT BRACKET ──
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

# ════════════════════════════════════════════
#        BAGIAN 12: RUNNING BOT
# ════════════════════════════════════════════
if __name__ == "__main__":
    print("Bot aktif...")
    try:
        bot.remove_webhook() # Ini buat matiin jalur webhook lama
        bot.infinity_polling(skip_pending=True) # skip_pending=True itu kunci biar pesan lama gak numpuk
    except Exception as e:
        print(f"Error saat polling: {e}")
        
