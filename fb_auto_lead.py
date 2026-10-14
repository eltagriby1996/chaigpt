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
    browser = p.chromium.launch_persistent_context(
        user_data_dir=PROFILE_DIR,
        headless=headless,
        channel="chrome" if os.path.exists("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe") else None,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-notifications"
        ],
        viewport={"width": 1280, "height": 800}
    )
    return p, browser

def login_mode():
    print("\n[+] جاري فتح المتصفح لتسجيل الدخول فيسبوك...")
    print("[!] برجاء تسجيل الدخول لحسابك وإغلاق المتصفح عند الانتهاء (سيتم حفظ الجلسة دائماً).\n")
    p, context = run_browser(headless=False)
    page = context.new_page()
    page.goto("https://www.facebook.com")
    print("[*] المتصفح مفتوح الآن أمامك.. سجل دخولك واضغط Enter في هذه الشاشة عند الانتهاء.")
    input("[اضغط Enter هنا بعد إتمام تسجيل الدخول] > ")
    context.close()
    p.stop()
    print("[✓] تم حفظ بيانات تسجيل الدخول بنجاح!")

def search_groups_mode():
    print("\n[+] بدء البحث الذكي والتلقائي عن جروبات قرى ومراكز بني سويف...")
    p, context = run_browser(headless=False)
    page = context.new_page()
    
    # التأكد من تسجيل الدخول
    page.goto("https://www.facebook.com")
    time.sleep(3)
    if "login" in page.url or "checkpoint" in page.url:
        print("[!] يبدو أنك لم تسجل الدخول بعد.. يرجى تسجيل الدخول أولاً من خيار (1).")
        context.close()
        p.stop()
        return

    discovered = set(get_saved_groups())
    
    for idx, target in enumerate(BENI_SUEF_TARGETS, 1):
        print(f"\n[*] [{idx}/{len(BENI_SUEF_TARGETS)}] جاري البحث عن: '{target}'...")
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
                                print(f"  [+] تم العثور على جروب جديد: {group_link}")

            # حفظ فوري
            save_groups(discovered)
        except Exception as e:
            print(f"  [!] خطأ أثناء البحث عن {target}: {e}")

    context.close()
    p.stop()
    print(f"\n[✓] اكتمل البحث! تم تجميع {len(discovered)} جروب في ملف groups.txt")

def auto_post_mode():
    groups = get_saved_groups()
    if not groups:
        print("[!] لا توجد جروبات في ملف groups.txt. ابدأ أولاً بالبحث عن الجروبات خيار (2).")
        return

    print(f"\n[+] بدء النشر التلقائي في {len(groups)} جروب مع الفواصل الآمنة...")
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
        print(f"\n[*] [{idx}/{len(groups)}] جاري الدخول للجروب: {group_url}")
        try:
            page.goto(group_url, wait_until="domcontentloaded")
            time.sleep(random.uniform(5, 8))

            # البحث عن صندوق إنشاء البوست
            # فيسبوك يدعم Write something... أو اكتب شيئاً...
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
                # محاولة الضغط على منطقة الكتابة
                feed_box = page.locator("div[role='region'] div[role='button']").first
                if feed_box.is_visible():
                    feed_box.click()
                    clicked = True

            if clicked:
                time.sleep(3)
                # كتابة البوست
                text_input = page.locator("div[role='dialog'] div[contenteditable='true']").first
                if text_input.is_visible():
                    text_input.fill(POST_TEXT)
                    time.sleep(2)

                    # رفع الصورة إن وجدت
                    if image_path:
                        try:
                            file_input = page.locator("input[type='file'][accept*='image']").first
                            if file_input.is_attached():
                                file_input.set_input_files(image_path)
                                time.sleep(4)
                        except Exception:
                            pass

                    # زر النشر (Post / نشر)
                    post_btn = page.locator("div[role='dialog'] div[role='button']:has-text('نشر'), div[role='dialog'] div[role='button']:has-text('Post')").first
                    if post_btn.is_visible():
                        post_btn.click()
                        success_count += 1
                        print(f"  [✓] تم النشر بنجاح في الجروب!")
                    else:
                        print("  [!] لم يتم العثور على زر النشر.")
            else:
                print("  [ℹ] لم يتم فتح صندوق الكتابة (قد تحتاج للموافقة على الانضمام أولاً).")

            # فاصل زمني آمن لتجنب حظر فيسبوك (من 3 إلى 5 دقائق)
            delay = random.randint(180, 300)
            print(f"  [⏳] انتظار أمان لمدة {delay // 60} دقيقة و {delay % 60} ثانية قبل الجروب التالي...")
            time.sleep(delay)

        except Exception as ex:
            print(f"  [!] خطأ في الجروب: {ex}")

    context.close()
    p.stop()
    print(f"\n[✓] انتهت عملية النشر! تم النشر في {success_count} جروب بنجاح.")

def main_menu():
    while True:
        print("\n" + "="*50)
        print("🚀 نظام أتمتة فيسبوك الشامل لمبيعات Orange DSL")
        print("="*50)
        print("1. تسجيل الدخول في فيسبوك لأول مرة (حفظ الجلسة)")
        print("2. البحث التلقائي عن جروبات قرى ومراكز بني سويف وتجميعها")
        print("3. بدء النشر التلقائي للبوست في كل الجروبات المجمعة")
        print("4. خروج")
        print("="*50)
        choice = input("اختر رقم العملية (1-4): ").strip()
        
        if choice == "1":
            login_mode()
        elif choice == "2":
            search_groups_mode()
        elif choice == "3":
            auto_post_mode()
        elif choice == "4":
            print("بالتوفيق يا كبير! مع السلامة 🫡")
            break
        else:
            print("اختيار غير صحيح، جرب تاني.")

if __name__ == "__main__":
    main_menu()
