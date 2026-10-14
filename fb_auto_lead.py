import os
import sys
import time
import json
import random
import re

# إجبار التوافق مع نصوص وترميز ويندوز
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

from urllib.parse import quote

# ----------------- نصوص البوست المعتمد -----------------
POST_TEXT = """زهقت من النت اللي بيخلص بسرعة والإشتراكات الغالية؟ 🛑

أقوى عروض الإنترنت المنزلي من Orange DSL (للخطوط الجديدة وللتحويل من أي شركة):

🎁 شهر كامل مجاناً بدون ولا جنيه اشتراك.
🏷 خصم 50% لمدة 6 شهور كاملين على جميع الباقات.
🧾 الأسعار شاملة الضريبة:

• باقة 200 جيجا: 211 ج فقط (بدل 376 ج)
• باقة 250 جيجا: 252 ج فقط (بدل 450 ج)
• باقة 300 جيجا: 294 ج فقط (بدل 524 ج)
• باقة 500 جيجا: 422 ج فقط (بدل 752 ج)
• باقة 750 جيجا: 591 ج فقط (بدل 1054 ج)

⚡ لو خطك في شركة تانية، التحويل بيتم خلال 48 ساعة فقط وبدون انقطاع للخدمة.

📲 للحجز والاستفسار، تواصل معنا فوراً على الواتساب:
01003061972
رابط مباشر للواتساب: wa.me/201003061972"""

# ----------------- قاعدة بيانات قرى ومراكز بني سويف -----------------
BENI_SUEF_TARGETS = [
    # الواسطى
    "الواسطى بني سويف", "سوق الواسطى", "الميمون الواسطى", "قمن العروس", "أطواب الواسطى", "ميدوم الواسطى", "ونا القس", "أبو صير الملق",
    # ناصر (بوش)
    "ناصر بني سويف", "مدينة بوش", "بهبشين ناصر", "دلاص ناصر", "دنديل", "طنسا الملق", "كوم أبو خلاد", "الزيتون ناصر",
    # مركز بني سويف
    "سوق بني سويف", "السوايفة بني سويف", "بيلفيا", "باروط بني سويف", "بني هارون", "تزمنت الشرقية", "إبشنا", "شريف باشا بني سويف", "باها بني سويف",
    # إهناسيا
    "إهناسيا المدينة", "سوق إهناسيا", "قرية قاي", "العواونة إهناسيا", "ميانة إهناسيا", "سدمنت الجبل", "براوة إهناسيا", "النويرة إهناسيا",
    # ببا
    "مركز ببا", "سوق ببا", "قرية هلية", "قرية سدس", "طنسا بني مالو", "صفط راشين ببا", "فاو ببا", "غياضة الشرقية", "زاوية الناوية",
    # الفشن
    "مركز الفشن", "سوق الفشن", "الفنت الفشن", "شنرا الفشن", "قرية تلت", "إقفهص الفشن", "دلهانس الفشن",
    # سمسطا
    "مركز سمسطا", "سوق سمسطا", "دشطوط سمسطا", "مازورة سمسطا", "بدهل سمسطا", "الشنطور سمسطا",
    # شرق النيل
    "شرق النيل بني سويف", "مدينة بني سويف الجديدة", "بياض العرب"
]

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "fb_profile")
GROUPS_FILE = os.path.join(os.path.dirname(__file__), "groups.txt")

def get_saved_groups():
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "r", encoding="utf-8") as f:
            lines = [l.strip() for l in f.readlines() if l.strip().startswith("http")]
            return list(set(lines))
    return []

def save_groups(group_urls):
    current = set(get_saved_groups())
    for u in group_urls:
        current.add(u)
    with open(GROUPS_FILE, "w", encoding="utf-8") as f:
        for u in sorted(current):
            f.write(u + "\n")
    print(f"[+] تم تحديث قائمة الجروبات: إجمالي {len(current)} جروب محفوظ في groups.txt")

def run_browser(headless=False):
    from playwright.sync_api import sync_playwright
    p = sync_playwright().start()
    os.makedirs(PROFILE_DIR, exist_ok=True)
    
    # استخدام متصفح كروم المثبت على جهازك
    chrome_path = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    use_channel = "chrome" if os.path.exists(chrome_path) else None
    
    browser = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=headless,
        channel=use_channel,
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-notifications",
            "--disable-infobars",
            "--start-maximized"
        ],
        no_viewport=True
    )

    # حيل تخطي كشف البوتات لصفحة الأمان والـ 2FA حتى لا تعلق في شاشة بيضاء
    browser.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
        window.navigator.chrome = { runtime: {} };
        Object.defineProperty(navigator, 'languages', {get: () => ['ar', 'en-US', 'en']});
        Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3, 4, 5]});
    """)
    return p, browser

def login_mode():
    print("\n" + "="*55)
    print("  [1] OPENING FACEBOOK LOGIN (تسجيل الدخول)")
    print("="*55)
    print("[*] Chrome will open now.")
    print("[*] Enter your Email & Password in the browser window.")
    print("[*] If Facebook asks for 2-Step verification, approve it.")
    print("="*55 + "\n")
    
    p, context = run_browser(headless=False)
    page = context.new_page()
    page.goto("https://www.facebook.com")
    print("\n[*] Browser is open now. Please complete your login.")
    input("\n>> Press ENTER here AFTER you see your Facebook Feed / Home > ")
    try:
        context.close()
    except Exception:
        pass
    try:
        p.stop()
    except Exception:
        pass
    print("\n[OK] Login session saved successfully! (تم حفظ الجلسة بنجاح)")

def search_groups_mode():
    print("\n" + "="*55)
    print("  [2] SEARCHING BENI SUEF VILLAGE GROUPS (بحث الجروبات)")
    print("="*55)
    p, context = run_browser(headless=False)
    page = context.new_page()
    
    # التأكد من تسجيل الدخول
    page.goto("https://www.facebook.com")
    time.sleep(3)
    if "login" in page.url or "checkpoint" in page.url:
        print("[!] You are not logged in yet. Please choose option (1) first.")
        try:
            context.close()
            p.stop()
        except Exception:
            pass
        return

    discovered = set(get_saved_groups())
    
    for idx, target in enumerate(BENI_SUEF_TARGETS, 1):
        print(f"\n[*] [{idx}/{len(BENI_SUEF_TARGETS)}] Searching: '{target}'...")
        try:
            search_url = f"https://www.facebook.com/search/groups/?q={quote(target)}"
            page.goto(search_url, wait_until="domcontentloaded")
            time.sleep(random.uniform(4, 7))

            # سكرول خفيف لتحميل النتائج
            for _ in range(3):
                page.mouse.wheel(0, 1000)
                time.sleep(1.5)

            # استخراج روابط الجروبات
            links = page.locator("a[href*='/groups/']").all()
            for l in links:
                href = l.get_attribute("href")
                if href and "/groups/" in href:
                    clean_match = re.search(r'(https://www\.facebook\.com/groups/[^/?]+)', href)
                    if clean_match:
                        group_link = clean_match.group(1)
                        if "search" not in group_link and "create" not in group_link:
                            if group_link not in discovered:
                                discovered.add(group_link)
                                print(f"  [+] Found new group: {group_link}")

            # حفظ فوري
            save_groups(discovered)
        except Exception as e:
            print(f"  [!] Error searching {target}: {e}")

    try:
        context.close()
        p.stop()
    except Exception:
        pass
    print(f"\n[OK] Search finished! Total groups in groups.txt: {len(discovered)}")

def auto_post_mode():
    groups = get_saved_groups()
    if not groups:
        print("[!] No groups found in groups.txt. Run option (2) first.")
        return

    print("\n" + "="*55)
    print(f"  [3] AUTO-POSTING TO {len(groups)} GROUPS (النشر التلقائي)")
    print("="*55)
    p, context = run_browser(headless=False)
    page = context.new_page()

    # مسار صورة العرض إذا كانت موجودة
    img_candidates = ["offer.jpg", "offer.png", "orange.jpg"]
    image_path = None
    for cand in img_candidates:
        full_cand = os.path.join(os.path.dirname(__file__), cand)
        if os.path.exists(full_cand):
            image_path = full_cand
            break

    success_count = 0
    for idx, group_url in enumerate(groups, 1):
        print(f"\n[*] [{idx}/{len(groups)}] Opening group: {group_url}")
        try:
            page.goto(group_url, wait_until="domcontentloaded")
            time.sleep(random.uniform(5, 8))

            post_triggers = [
                "div[role='button']:has-text('اكتب شيئاً')",
                "div[role='button']:has-text('Write something')",
                "div[role='button']:has-text('إنشاء منشور عام')",
                "div[role='button']:has-text('Create a public post')"
            ]
            clicked = False
            for trig in post_triggers:
                loc = page.locator(trig).first
                if loc.is_visible():
                    loc.click()
                    clicked = True
                    break

            if not clicked:
                feed_box = page.locator("div[role='region'] div[role='button']").first
                if feed_box.is_visible():
                    feed_box.click()
                    clicked = True

            if clicked:
                time.sleep(3)
                text_input = page.locator("div[role='dialog'] div[contenteditable='true']").first
                if text_input.is_visible():
                    text_input.fill(POST_TEXT)
                    time.sleep(2)

                    if image_path:
                        try:
                            file_input = page.locator("input[type='file'][accept*='image']").first
                            if file_input.is_attached():
                                file_input.set_input_files(image_path)
                                time.sleep(4)
                        except Exception:
                            pass

                    post_btn = page.locator("div[role='dialog'] div[role='button']:has-text('نشر'), div[role='dialog'] div[role='button']:has-text('Post')").first
                    if post_btn.is_visible():
                        post_btn.click()
                        success_count += 1
                        print(f"  [OK] Posted successfully to group!")
                    else:
                        print("  [!] Post button not found.")
            else:
                print("  [!] Could not open post box (maybe needs group membership approval).")

            delay = random.randint(180, 300)
            print(f"  [WAIT] Safe delay: sleeping {delay // 60}m {delay % 60}s before next group...")
            time.sleep(delay)

        except Exception as ex:
            print(f"  [!] Error in group: {ex}")

    try:
        context.close()
        p.stop()
    except Exception:
        pass
    print(f"\n[OK] Posting finished! Successfully posted to {success_count} groups.")

def main_menu():
    while True:
        print("\n" + "="*55)
        print("    ORANGE DSL - FACEBOOK AUTOMATION SYSTEM")
        print("="*55)
        print("  [1] Login to Facebook (تسجيل الدخول وحفظ الجلسة)")
        print("  [2] Search Beni Suef Groups (البحث وتجميع جروبات القرى)")
        print("  [3] Auto-Post to Groups (بدء النشر التلقائي)")
        print("  [4] Exit (خروج)")
        print("="*55)
        choice = input("Select Option (1-4): ").strip()
        
        if choice == "1":
            login_mode()
        elif choice == "2":
            search_groups_mode()
        elif choice == "3":
            auto_post_mode()
        elif choice == "4":
            print("\nGoodbye! بالتوفيق يا كبير 🫡\n")
            break
        else:
            print("[!] Invalid option. Please enter 1, 2, 3, or 4.")

if __name__ == "__main__":
    main_menu()
