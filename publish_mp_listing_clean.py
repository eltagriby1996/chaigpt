import sys, os, time
sys.path.append(r"e:\my\My_Project\ChaiGpt")
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
from playwright.sync_api import sync_playwright
import fb_cookies_manager

OFFER_IMG = r"e:\my\My_Project\ChaiGpt\offer.jpg"

MP_DESCRIPTION = """أقوى عروض الإنترنت المنزلي من Orange DSL 🍊🔥
عرض التوفير الأكبر (خط جديد أو تحويل من شركتك الحالية):
✅ شهر مجاناً بالكامل بدون اشتراك
✅ خصم 50% لمدة 6 شهور
✅ التحويل بيتم خلال 48 ساعة بدون انقطاع للخدمة وبنفس رقمك

📊 الأسعار شاملة الضريبة:
• 200 جيجا ⬅️ 211 جنيه
• 250 جيجا ⬅️ 252 جنيه
• 300 جيجا ⬅️ 294 جنيه
• 500 جيجا ⬅️ 422 جنيه
• 750 جيجا ⬅️ 591 جنيه

📩 للحجز والاستعلام تواصل معنا واتساب مباشرة:
wa.me/201003061972
أو اتصال: 01003061972"""

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

print("[*] Navigating to Marketplace create page...")
page.goto("https://www.facebook.com/marketplace/create/item", wait_until="domcontentloaded")
time.sleep(5)

# 1. Upload photo
print("[*] Uploading offer photo...")
file_input = page.locator("input[type='file']").first
file_input.set_input_files(OFFER_IMG)
time.sleep(4)

# 2. Title
print("[*] Filling Title...")
page.locator("label:has-text('العنوان') input, input[type='text']").nth(0).fill("راوتر ونت منزلي Orange DSL - خصم 50% وشهر مجاناً")
time.sleep(1)

# 3. Price
print("[*] Filling Price...")
page.locator("label:has-text('السعر') input, input[type='text']").nth(1).fill("211")
time.sleep(1)

# 4. Category
print("[*] Selecting Category...")
try:
    cat_box = page.locator("label:has-text('الفئة')").first
    cat_box.click()
    time.sleep(2)
    # Click first available category (like أدوات or أجهزة)
    page.locator("div[role='option'], div[role='menuitem']").first.click()
    time.sleep(2)
    print("[+] Category clicked!")
except Exception as e:
    print("[!] Cat error:", e)

# 5. Condition
print("[*] Selecting Condition...")
try:
    cond_box = page.locator("label:has-text('الحالة')").first
    cond_box.click()
    time.sleep(2)
    # Click first option which is usually 'جديد' (New)
    page.locator("div[role='option']").first.click()
    time.sleep(2)
    print("[+] Condition clicked!")
except Exception as e:
    print("[!] Cond error:", e)

# 6. Description
print("[*] Filling Description...")
try:
    page.locator("label:has-text('الوصف') textarea, textarea").first.fill(MP_DESCRIPTION)
    time.sleep(2)
except Exception as e:
    print("[!] Desc error:", e)

page.screenshot(path=r"C:\Users\HD\.gemini\antigravity-ide\brain\06543a0e-89a7-42c1-ba02-a1b1f466b010\mp_ready_publish.png")

# 7. Next Button
next_btn = page.locator("div[role='button']:has-text('التالي'), button:has-text('التالي')").first
if next_btn.is_visible():
    print("[*] Clicking 'التالي' (Next)...")
    next_btn.click()
    time.sleep(4)
    page.screenshot(path=r"C:\Users\HD\.gemini\antigravity-ide\brain\06543a0e-89a7-42c1-ba02-a1b1f466b010\mp_step2_ready.png")

    # 8. Publish Button
    pub_btn = page.locator("div[role='button']:has-text('نشر'), button:has-text('نشر')").first
    if pub_btn.is_visible():
        print("[*] Found 'نشر' button! Clicking Publish...")
        pub_btn.click()
        time.sleep(7)
        page.screenshot(path=r"C:\Users\HD\.gemini\antigravity-ide\brain\06543a0e-89a7-42c1-ba02-a1b1f466b010\mp_published_final.png")
        print("[+] SUCCESS! MARKETPLACE LISTING IS LIVE!")

browser.close()
p.stop()
print("Finished!")
