import sys, os, time, json, urllib.parse
sys.path.append(r"e:\my\My_Project\ChaiGpt")
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
from playwright.sync_api import sync_playwright
import fb_cookies_manager

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

تقدر تتواصل وتحجز مباشرة واتساب: 01003061972"""

def run_sniper(max_posts_per_query=5):
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
            for p_item in posts_data[:max_posts_per_query]:
                p_item["query"] = q
                leads_found.append(p_item)
        except Exception as e:
            print(f" -> Error searching '{q}': {e}")

    output_path = r"C:\Users\HD\.gemini\antigravity-ide\brain\06543a0e-89a7-42c1-ba02-a1b1f466b010\hot_leads.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(leads_found, f, ensure_ascii=False, indent=2)

    print(f"\n[+] Total Hot Leads Harvested: {len(leads_found)}")
    browser.close()
    p.stop()
    return leads_found

if __name__ == "__main__":
    run_sniper()
