import sys, os, time, base64, requests
sys.path.append(r"e:\my\My_Project\ChaiGpt")
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from playwright.sync_api import sync_playwright
import fb_cookies_manager

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

COMMENT_TEXT = """لو النت عندك فيه مشاكل أو بتدور على أعلى توفير واستقرار، حالياً أقوى عروض الإنترنت المنزلي من Orange DSL 🍊🔥

✅ خصم 50% لمدة 6 شهور
✅ شهر مجاناً بالكامل بدون اشتراك
✅ التحويل بيتم خلال 48 ساعة فقط بدون انقطاع للخدمة وبنفس رقمك الأرضي
📊 الأسعار شاملة الضريبة:
• 200 جيجا ⬅️ 211 جنيه
• 250 جيجا ⬅️ 252 جنيه
• 300 جيجا ⬅️ 294 جنيه
• 500 جيجا ⬅️ 422 جنيه

📩 للحجز والاستعلام تواصل معنا واتساب مباشرة بضغطة واحدة:
https://wa.me/201003061972
أو اتصال: 01003061972"""

def post_on_we_page():
    print("[*] Starting WE Official Page Sniper...")
    p = sync_playwright().start()
    browser = p.chromium.launch(headless=True)
    ctx = browser.new_context(locale="ar-EG", viewport={"width": 1280, "height": 900})
    ctx.add_cookies(fb_cookies_manager.get_cookies())
    page = ctx.new_page()

    page.goto("https://www.facebook.com", wait_until="domcontentloaded")
    time.sleep(3)
    try:
        if page.locator("text=متابعة").first.is_visible():
            page.locator("text=متابعة").first.click()
            time.sleep(3)
        pwd = page.locator("input[type='password']")
        if pwd.first.is_visible():
            pwd.first.fill("Ahmed@12#")
            time.sleep(1)
            page.keyboard.press("Enter")
            time.sleep(6)
    except Exception:
        pass

    print("[*] Navigating to Telecom Egypt page...")
    page.goto("https://www.facebook.com/telecomegypt", wait_until="domcontentloaded")
    time.sleep(5)

    # Scroll down to reveal the first post and its comment box
    page.mouse.wheel(0, 800)
    time.sleep(3)

    # Find the comment box on the latest post
    box_focused = page.evaluate("""() => {
        const boxes = Array.from(document.querySelectorAll("div[role='textbox'], div[contenteditable='true']"));
        const commentBox = boxes.find(b => {
            const aria = (b.getAttribute('aria-label') || '').toLowerCase();
            return aria.includes('تعليق') || aria.includes('comment') || aria.includes('اكتب تعليق');
        });
        if (commentBox) {
            commentBox.scrollIntoView({ behavior: 'instant', block: 'center' });
            commentBox.focus();
            return true;
        }
        return false;
    }""")

    if box_focused:
        print("[*] Found comment box on WE's latest post! Typing offer comment...")
        paragraphs = COMMENT_TEXT.split('\n')
        for para in paragraphs:
            if para:
                page.keyboard.type(para, delay=8)
            page.keyboard.press("Shift+Enter")
            time.sleep(0.05)

        time.sleep(1)
        page.keyboard.press("Enter")
        time.sleep(5)
        print("[+] COMMENT POSTED ON TELECOM EGYPT OFFICIAL POST!")

        page.screenshot(path=r"C:\Users\HD\.gemini\antigravity-ide\brain\06543a0e-89a7-42c1-ba02-a1b1f466b010\we_comment_posted.png")

        alert_msg = (
            f"🎯 <b>[صيد عملاء وي - Telecom Egypt] 🍊🔥</b>\n\n"
            f"✅ تم نشر تعليق العرض بنجاح على أحدث منشور في الصفحة الرسمية لـ WE!\n"
            f"🔗 رابط الصفحة: https://www.facebook.com/telecomegypt\n\n"
            f"💬 التعليق يظهر لمئات العملاء الغاضبين من بطء النت ويتضمن رابط الواتساب المباشر."
        )
        send_telegram_alert(alert_msg)
    else:
        print("[!] Could not focus comment box on WE page.")

    browser.close()
    p.stop()
    print("[+] Done WE Page run!")

if __name__ == "__main__":
    post_on_we_page()
