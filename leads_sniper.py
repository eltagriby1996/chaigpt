import sys, os, time, json, urllib.parse, base64, requests
sys.path.append(r"e:\my\My_Project\ChaiGpt")
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from playwright.sync_api import sync_playwright
import fb_cookies_manager

# إعدادات التيليجرام للتنبيهات الفورية
_enc_token = "ODc5NTAyNjE5OTpBQUVvWTRjMGZPU0ViMXQya2RxMzZPOE9uRVdieENrSFF4RQ=="
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or base64.b64decode(_enc_token).decode("utf-8")
ADMIN_ID = 7815806102

def send_telegram_alert(message: str):
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        requests.post(url, json=payload, timeout=10)
    except Exception:
        pass

# الكلمات المفتاحية الأكثر طلباً وتحويلاً في مصر
SNIPER_QUERIES = [
    "احول من وي",
    "عايز احول لاورانج",
    "نت وي وحش",
    "راوتر ارضي اورنج",
    "تقديم نت ارضي",
    "عروض النت المنزلي اورنج"
]

COMMENT_TEMPLATE = """لو بتفكر تحول أو تقدم جديد، حالياً أقوى عرض في مصر من Orange DSL 🍊🔥
✅ خصم 50% لمدة 6 شهور
✅ شهر مجاناً بالكامل بدون اشتراك
✅ التحويل بيتم خلال 48 ساعة فقط بدون انقطاع للخدمة وبنفس رقمك الأرضي
📊 باقة الـ 200 جيجا بـ 211 جنيه فقط شاملة الضريبة الرسمية.

📩 تقدر تتواصل وتحجز مباشرة واتساب بضغطة واحدة:
https://wa.me/201003061972
أو اتصال: 01003061972"""

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
COMMENTED_FILE = os.path.join(WORKSPACE_DIR, "commented_leads.txt")

def get_commented_leads():
    if os.path.exists(COMMENTED_FILE):
        with open(COMMENTED_FILE, "r", encoding="utf-8") as f:
            return set(l.strip() for l in f if l.strip())
    return set()

def mark_lead_commented(url):
    with open(COMMENTED_FILE, "a", encoding="utf-8") as f:
        f.write(url.strip() + "\n")

def run_sniper(max_comments=10):
    print("[*] Starting Facebook Hot Leads Sniper Engine...")
    commented_leads = get_commented_leads()

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

    leads_found = []

    for q in SNIPER_QUERIES:
        search_url = f"https://www.facebook.com/search/posts/?q={urllib.parse.quote(q)}"
        print(f"\n[*] Sniping query: '{q}' ...")
        try:
            page.goto(search_url, wait_until="domcontentloaded", timeout=25000)
            time.sleep(4)
            page.mouse.wheel(0, 1500)
            time.sleep(2)

            posts_data = page.evaluate("""() => {
                const results = [];
                const feed = document.querySelector('div[role="feed"]') || document.body;
                const articles = Array.from(feed.querySelectorAll('div[role="article"]'));
                for (const a of articles) {
                    const text = a.innerText.split('\\n').filter(Boolean);
                    const link = a.querySelector('a[href*="/posts/"], a[href*="/permalink/"], a[href*="story_fbid"]');
                    if (link && text.length > 2) {
                        results.push({
                            title: text[0],
                            snippet: text.slice(0, 4).join(' -- '),
                            url: link.href
                        });
                    }
                }
                return results;
            }""")

            print(f" -> Found {len(posts_data)} relevant posts for '{q}'")
            for p_item in posts_data:
                clean_url = p_item["url"].split('?')[0]
                if clean_url not in commented_leads and clean_url not in [l["url"] for l in leads_found]:
                    p_item["url"] = clean_url
                    p_item["query"] = q
                    leads_found.append(p_item)
        except Exception as e:
            print(f" -> Error searching '{q}': {e}")

    print(f"\n[+] Total New Target Leads to Engage: {len(leads_found)}")

    comments_count = 0
    for lead in leads_found:
        if comments_count >= max_comments:
            break
        print(f"\n[*] Navigating to lead post: {lead['url']}")
        try:
            page.goto(lead["url"], wait_until="domcontentloaded", timeout=25000)
            time.sleep(4)

            # Check if comment box is available
            box_found = page.evaluate("""() => {
                const boxes = Array.from(document.querySelectorAll("div[role='textbox'], div[contenteditable='true']"));
                const cbox = boxes.find(b => {
                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                    return aria.includes('تعليق') || aria.includes('comment') || aria.includes('اكتب تعليق');
                });
                if (cbox) {
                    cbox.focus();
                    return true;
                }
                return false;
            }""")

            if box_found:
                page.keyboard.type(COMMENT_TEMPLATE, delay=8)
                time.sleep(1)
                page.keyboard.press("Enter")
                time.sleep(4)
                mark_lead_commented(lead["url"])
                comments_count += 1
                print(f"[+] Successfully commented on lead post: {lead['url']}")

                alert_msg = (
                    f"🎯 <b>[صيد عميل جديد - Leads Sniper] 🍊🔥</b>\n\n"
                    f"💬 <b>استفسار العميل:</b>\n{lead.get('snippet', '')[:120]}...\n\n"
                    f"🔗 <b>رابط البوست:</b>\n{lead['url']}\n\n"
                    f"✅ تم الرد بتفاصيل العرض والتحويل في 48 ساعة ورابط الواتساب المباشر!"
                )
                send_telegram_alert(alert_msg)
                time.sleep(20) # فاصل زمني آمن بين كل تعليق
            else:
                print("[!] Comment box not accessible for this post. Moving next.")
                mark_lead_commented(lead["url"])
        except Exception as e:
            print(f"[!] Error commenting on {lead['url']}: {e}")
            mark_lead_commented(lead["url"])

    browser.close()
    p.stop()
    print(f"\n[+] Finished Sniper session! Total comments posted: {comments_count}")

if __name__ == "__main__":
    run_sniper()
