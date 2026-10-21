import os
import sys
import time
import asyncio
import base64
import requests

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.contacts import SearchRequest
from telethon.tl.types import Channel, Chat

# إعدادات Telegram API (Official Telegram Desktop Client ID)
API_ID = int(os.getenv("TG_API_ID", "2040"))
API_HASH = os.getenv("TG_API_HASH", "b18441a1ff607e10a989891a5462e627")

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(WORKSPACE_DIR, "userbot")
OFFER_IMG = os.path.join(WORKSPACE_DIR, "offer.jpg")
POSTED_FILE = os.path.join(WORKSPACE_DIR, "tg_posted_groups.txt")

# إعدادات التنبيهات على التيليجرام
_enc_token = "ODc5NTAyNjE5OTpBQUVvWTRjMGZPU0ViMXQya2RxMzZPOE9uRVdieENrSFF4RQ=="
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or base64.b64decode(_enc_token).decode("utf-8")
ADMIN_ID = 7815806102

def send_telegram_alert(message: str):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {"chat_id": ADMIN_ID, "text": message, "parse_mode": "HTML"}
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

TG_POST_TEXT = """🔥 <b>عرض التوفير الأكبر للإنترنت المنزلي من Orange DSL</b> 🍊

لو بتدور على نت منزلي طلقة أو عايز توفر نص فاتورتك الشهرية:
✅ <b>شهر مجاناً بالكامل</b> بدون أي اشتراك
✅ <b>خصم 50%</b> لمدة 6 شهور متواصلة
✅ <b>التحويل بيتم خلال 48 ساعة فقط</b> بدون انقطاع للخدمة وبنفس رقمك الأرضي الحالي

📊 <b>الأسعار شاملة ضريبة القيمة المضافة:</b>
• 200 جيجا ⬅️ <b>211 جنيه فقط</b>
• 250 جيجا ⬅️ <b>252 جنيه</b>
• 300 جيجا ⬅️ <b>294 جنيه</b>
• 500 جيجا ⬅️ <b>422 جنيه</b>
• 750 جيجا ⬅️ <b>591 جنيه</b>

📩 <b>للحجز والاستعلام السريع تواصل معنا واتساب مباشرة بضغطة واحدة:</b>
👉 https://wa.me/201003061972
📞 أو اتصال هاتفي على: <code>01003061972</code>"""

# الكلمات المفتاحية للبحث عن الجروبات المفتوحة في مصر
SEARCH_KEYWORDS = [
    "عروض نت مصر",
    "راوترات مصر",
    "سوق مصر المفتوح",
    "سوق القاهرة المفتوح",
    "سوق اسكندرية المفتوح",
    "خدمات 6 اكتوبر",
    "دليل التجمع الخامس",
    "اعلانات مصر",
    "سوق المنصورة",
    "سوق طنطا",
    "سوق العاشر من رمضان",
    "عقارات مصر بيع وشراء"
]

def get_posted_groups():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(l.strip() for l in f if l.strip())
    return set()

def mark_posted(group_id_str):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(str(group_id_str).strip() + "\n")

async def search_and_harvest_groups(client):
    """البحث العالمي داخل تيليجرام واستخراج السوبر جروبات المفتوحة"""
    found_groups = []
    seen_ids = set()

    for kw in SEARCH_KEYWORDS:
        print(f"[*] Searching Telegram for keyword: '{kw}' ...")
        try:
            res = await client(SearchRequest(q=kw, limit=20))
            for chat in res.chats:
                # التأكد من أنه جروب أو قناة فائقة مفتوحة (Megagroup/Supergroup)
                if isinstance(chat, Channel) and chat.megagroup and not chat.broadcast:
                    if chat.id not in seen_ids:
                        seen_ids.add(chat.id)
                        found_groups.append(chat)
                        print(f" -> Found Open Group: {chat.title} (@{chat.username or 'private'})")
                elif isinstance(chat, Chat):
                    if chat.id not in seen_ids:
                        seen_ids.add(chat.id)
                        found_groups.append(chat)
                        print(f" -> Found Group: {chat.title}")
            await asyncio.sleep(2)
        except Exception as e:
            print(f"[!] Search error for '{kw}': {e}")
            await asyncio.sleep(2)

    return found_groups

async def run_poster(phone=None, code_callback=None):
    client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        if phone:
            print(f"[*] Sending code request for {phone} ...")
            sent = await client.send_code_request(phone)
            print("[+] Code sent to your Telegram app!")
            if code_callback:
                code = code_callback()
                await client.sign_in(phone, code)
                print("[+] Successfully signed in and created userbot.session!")
            else:
                print("[!] No code callback provided. Please run interactively.")
                return False
        else:
            print("[!] Client not authorized and no phone provided.")
            return False

    me = await client.get_me()
    print(f"\n[+] Logged in as: {me.first_name} (@{me.username or me.phone})")
    send_telegram_alert(f"🚀 <b>تم تفعيل ناشر تيليجرام التلقائي (Userbot) بنجاح!</b>\nالحساب: {me.first_name}")

    # البحث عن الجروبات
    groups = await search_and_harvest_groups(client)
    posted = get_posted_groups()
    pending = [g for g in groups if str(g.id) not in posted]

    print(f"\n[+] Total Discovered Groups: {len(groups)}")
    print(f"[+] Previously Posted: {len(posted)}")
    print(f"[+] Pending to Post: {len(pending)}")

    posted_count = 0
    for g in pending:
        try:
            print(f"\n[*] Processing group: {g.title} (ID: {g.id}) ...")
            # 1. الانضمام إلى الجروب إن لم يكن منضماً
            try:
                await client(JoinChannelRequest(g))
                await asyncio.sleep(3)
            except Exception:
                pass

            # 2. إرسال البوست مع الصورة ورابط الواتساب
            if os.path.exists(OFFER_IMG):
                await client.send_file(
                    g,
                    OFFER_IMG,
                    caption=TG_POST_TEXT,
                    parse_mode="html"
                )
            else:
                await client.send_message(
                    g,
                    TG_POST_TEXT,
                    parse_mode="html"
                )

            mark_posted(g.id)
            posted_count += 1
            print(f"[+] Successfully posted to Telegram group: {g.title}")

            alert = (
                f"📢 <b>[نشر تلقائي ناجح على تيليجرام] 🍊🔥</b>\n\n"
                f"✅ <b>الجروب:</b> {g.title}\n"
                f"👤 <b>المعرف:</b> @{g.username or 'رابط خاص'}\n"
                f"📊 <b>إجمالي الجروبات المنشورة:</b> {posted_count}\n"
                f"⏳ فاصل أمان دقيقة لمنع قيود تيليجرام..."
            )
            send_telegram_alert(alert)

            # فاصل زمني آمن بين كل جروب وجروب (60 إلى 90 ثانية)
            await asyncio.sleep(60)

        except Exception as e:
            print(f"[!] Error posting to {g.title}: {e}")
            mark_posted(g.id)
            await asyncio.sleep(10)

    print(f"\n[+] Finished Telegram broadcasting cycle! Posted to {posted_count} groups.")
    await client.disconnect()
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--auth":
        phone = input("Enter Phone Number (e.g. +2010xxxxxxx): ")
        client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
        client.start(phone)
        print("[+] Session created successfully! Now you can run autonomous posting.")
    else:
        asyncio.run(run_poster())
