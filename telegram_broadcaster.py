import os, sys, time, json, requests, base64

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

# توكن البوت المشفر
_enc_token = "ODgzMjYxMDYxOTpBQUgxUGxUSHFHdVQ0SnQ2OHR6eDE5VkxXclFYZmM0MHhrTQ=="
BOT_TOKEN = os.getenv("ORANGE_BOT_TOKEN") or base64.b64decode(_enc_token).decode("utf-8")
ADMIN_ID = 7815806102
WHATSAPP_LINK = "https://wa.me/201003061972?text=أهلاً%20عايز%20استفسر%20عن%20عرض%20الإنترنت%20المنزلي%20Orange%20DSL"
BOT_LINK = "https://t.me/OrangeDsI_bot"

OFFER_CAPTION = """🔥 <b>عرض التوفير الأكبر للإنترنت المنزلي من Orange DSL</b> 🍊

لو بتدور على نت منزلي طلقة أو عايز توفر نص فاتورتك الشهرية:
✅ <b>شهر مجاناً بالكامل</b> بدون أي اشتراك
✅ <b>خصم 50%</b> لمدة 6 شهور متواصلة
✅ <b>التحويل بيتم خلال 48 ساعة فقط</b> وبدون انقطاع للخدمة وبنفس رقمك الأرضي الحالي

📊 <b>الأسعار شاملة ضريبة القيمة المضافة:</b>
• 200 جيجا ⬅️ <b>211 جنيه فقط</b>
• 250 جيجا ⬅️ <b>252 جنيه</b>
• 300 جيجا ⬅️ <b>294 جنيه</b>
• 500 جيجا ⬅️ <b>422 جنيه</b>

📩 <i>التعاقد يتم أونلاين بصورة البطاقة دون الحاجة للذهاب للفرع.</i>
اضغط على الأزرار بالأسفل للحجز والتواصل الفوري 👇"""

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
OFFER_IMG = os.path.join(WORKSPACE_DIR, "offer.jpg")

# قنوات وجروبات تيليجرام المصرية المستهدفة
TARGET_CHANNELS_FILE = os.path.join(WORKSPACE_DIR, "telegram_targets.txt")

DEFAULT_TARGETS = [
    # قنوات خدمات وعروض عامة في مصر
    "@souq_masr_free",
    "@egypt_offers_online",
    "@cairo_services_market",
    "@alex_market_offers",
    "@october_zayed_services",
    "@mansoura_services_souq"
]

def init_targets():
    if not os.path.exists(TARGET_CHANNELS_FILE):
        with open(TARGET_CHANNELS_FILE, "w", encoding="utf-8") as f:
            for t in DEFAULT_TARGETS:
                f.write(t + "\n")

def get_targets():
    init_targets()
    with open(TARGET_CHANNELS_FILE, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.startswith("#")]

def send_telegram_broadcast(target_chat):
    """إرسال العرض مع الصورة وأزرار التفاعل المباشرة"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "💬 احجز واتساب بضغطة واحدة", "url": WHATSAPP_LINK}
            ],
            [
                {"text": "🤖 تحدث مع بوت المبيعات أونلاين", "url": BOT_LINK}
            ]
        ]
    }
    
    try:
        if os.path.exists(OFFER_IMG):
            with open(OFFER_IMG, "rb") as img_file:
                payload = {
                    "chat_id": target_chat,
                    "caption": OFFER_CAPTION,
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps(reply_markup)
                }
                files = {"photo": img_file}
                res = requests.post(url, data=payload, files=files, timeout=15)
                return res.json()
        else:
            # fallback to text message
            msg_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {
                "chat_id": target_chat,
                "text": OFFER_CAPTION,
                "parse_mode": "HTML",
                "reply_markup": json.dumps(reply_markup)
            }
            res = requests.post(msg_url, json=payload, timeout=15)
            return res.json()
    except Exception as e:
        return {"ok": False, "error": str(e)}

def run_broadcast():
    print("[*] Starting Telegram Regional Broadcaster...")
    targets = get_targets()
    print(f"[+] Loaded {len(targets)} Telegram target channels/groups.")

    # 1. إرسال نسخة تجريبية فورية للأستاذ أحمد لمعاينة شكل العرض الفاخر
    print(f"[*] Sending test preview to Admin ({ADMIN_ID})...")
    admin_res = send_telegram_broadcast(ADMIN_ID)
    if admin_res.get("ok"):
        print("[+] Test broadcast delivered successfully to Admin Telegram!")
    else:
        print(f"[!] Admin test error: {admin_res}")

    success_count = 0
    for t in targets:
        print(f"[*] Broadcasting to: {t} ...")
        res = send_telegram_broadcast(t)
        if res.get("ok"):
            print(f"[+] Success on {t}!")
            success_count += 1
        else:
            err_desc = res.get("description", str(res))
            print(f"[*] Note on {t}: {err_desc}")
        time.sleep(3)

    print(f"\n[+] Telegram broadcast cycle completed! Delivered to {success_count} destinations.")

if __name__ == "__main__":
    run_broadcast()
