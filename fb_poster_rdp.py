import os
import sys
import time
import json
import random
import re
import base64
import requests
from datetime import datetime

# إجبار التوافق مع نصوص وترميز ويندوز لمنع أي كراش
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import fb_cookies_manager

# ----------------- إعدادات التيليجرام للتنبيهات المباشرة -----------------
_enc_token = "ODc5NTAyNjE5OTpBQUVvWTRjMGZPU0ViMXQya2RxMzZPOE9uRVdieENrSFF4RQ=="
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN") or base64.b64decode(_enc_token).decode("utf-8")
ADMIN_ID = 7815806102

def send_telegram_alert(message: str):
    """إرسال تنبيه فوري إلى تيليجرام للأستاذ أحمد"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        payload = {
            "chat_id": ADMIN_ID,
            "text": message,
            "parse_mode": "HTML",
            "disable_web_page_preview": False
        }
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        print(f"[!] Telegram notify error: {e}")

# ----------------- نص البوست المعتمد والمثالي بدون روابط خارجية -----------------
POST_TEXT = """وفّر نص فاتورتك الشهرية مع أقوى عروض الإنترنت المنزلي من Orange DSL 🍊🔥

عرض التوفير الأكبر (سواء خط أرضي جديد أو تحويل من شركتك الحالية):
✅ شهر مجاناً بالكامل بدون اشتراك
✅ خصم 50% لمدة 6 شهور
✅ التحويل بيتم خلال 48 ساعة بدون انقطاع للخدمة

📊 الأسعار شاملة الضريبة:
• 200 جيجا ⬅️ 211 جنيه
• 250 جيجا ⬅️ 252 جنيه
• 300 جيجا ⬅️ 294 جنيه
• 500 جيجا ⬅️ 422 جنيه
• 750 جيجا ⬅️ 591 جنيه

📩 للحجز والاستعلام تواصل معنا واتساب:
01003061972"""

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
GROUPS_FILE = os.path.join(WORKSPACE_DIR, "groups.txt")
POSTED_FILE = os.path.join(WORKSPACE_DIR, "posted_groups.txt")
OFFER_IMG = os.path.join(WORKSPACE_DIR, "offer.jpg")
STOP_FILE = os.path.join(WORKSPACE_DIR, "poster.stop")

def get_posted_groups():
    if os.path.exists(POSTED_FILE):
        with open(POSTED_FILE, "r", encoding="utf-8") as f:
            return set(l.strip() for l in f if l.strip() and not l.strip().startswith("#"))
    return set()

def sync_progress():
    """مزامنة التقدم إلى SavedWork وإلى جيت هاب تلقائياً لضمان استئناف النشر من آخر نقطة عند تجديد الأرديبي"""
    # 1. حفظ نسخة في SavedWork لميجا
    saved_work = r"C:\Users\Public\Desktop\SavedWork"
    if os.path.exists(saved_work):
        try:
            import shutil
            if os.path.exists(POSTED_FILE):
                shutil.copy2(POSTED_FILE, os.path.join(saved_work, "posted_groups.txt"))
            cookies_file = os.path.join(WORKSPACE_DIR, "fb_cookies.json")
            if os.path.exists(cookies_file):
                shutil.copy2(cookies_file, os.path.join(saved_work, "fb_cookies.json"))
        except Exception:
            pass

    # 2. مزامنة التقدم عبر Git الكوميت التلقائي [skip ci]
    try:
        import subprocess
        subprocess.run(["git", "config", "user.name", "github-actions[bot]"], check=False)
        subprocess.run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"], check=False)
        subprocess.run(["git", "add", "posted_groups.txt"], check=False)
        res = subprocess.run(["git", "commit", "-m", "Auto-sync posted_groups progress [skip ci]"], capture_output=True, text=True)
        if "nothing to commit" not in res.stdout.lower() and "nothing to commit" not in res.stderr.lower():
            subprocess.run(["git", "push"], check=False)
            print("[+] Progress synced back to GitHub repository successfully!")
    except Exception as e:
        print(f"[!] Warning syncing to git: {e}")

def mark_posted(group_url):
    with open(POSTED_FILE, "a", encoding="utf-8") as f:
        f.write(group_url.strip() + "\n")
    sync_progress()

def get_target_groups():
    if not os.path.exists(GROUPS_FILE):
        return []
    with open(GROUPS_FILE, "r", encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip().startswith("http")]

def run_rdp_poster():
    # إزالة ملف الإيقاف عند البدء الجديد
    if os.path.exists(STOP_FILE):
        try:
            os.remove(STOP_FILE)
        except Exception:
            pass

    print("[*] Starting RDP Autonomous Facebook Poster with Smart-Publish Engine...")
    
    cookies = fb_cookies_manager.get_cookies()
    if not cookies:
        print("[!] No Facebook cookies available.")
        send_telegram_alert("⚠️ <b>تنبيه من الأرديبي:</b> لم يتم العثور على كوكيز فيسبوك. يرجى تزويدها عبر الشات.")
        return

    all_groups = get_target_groups()
    posted = get_posted_groups()
    pending = [g for g in all_groups if g not in posted]

    startup_msg = (
        f"🚀 <b>بدء تشغيل سكريبت النشر التلقائي الذكي على الأرديبي!</b>\n\n"
        f"📊 <b>إجمالي الجروبات:</b> {len(all_groups)} جروب\n"
        f"✅ <b>تم النشر سابقاً:</b> {len(posted)} جروب\n"
        f"🎯 <b>المتبقي للنشر:</b> {len(pending)} جروب\n\n"
        f"⚡ <b>الحالة:</b> السكريبت يبدأ العمل الفوري الآن وستصلك رسالة تأكيد بكل جروب!"
    )
    send_telegram_alert(startup_msg)

    from playwright.sync_api import sync_playwright

    p = sync_playwright().start()
    browser = p.chromium.launch(
        headless=True,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox",
            "--disable-notifications",
            "--disable-infobars"
        ]
    )
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        viewport={"width": 1280, "height": 900},
        locale="ar-EG"
    )
    context.add_cookies(cookies)

    page = context.new_page()
    page.goto("https://www.facebook.com", wait_until="domcontentloaded", timeout=45000)
    time.sleep(5)

    # التحقق من شاشة المتابعة أو تسجيل الدخول وإدخال كلمة السر تلقائياً
    try:
        cont_btn = page.locator("text=متابعة").first
        if cont_btn.is_visible():
            print("[*] Clicking continue on profile chooser...")
            cont_btn.click()
            time.sleep(3)
        
        pass_input = page.locator("input[type='password']").first
        if pass_input.is_visible():
            print("[*] Re-authenticating with password...")
            pass_input.fill("Ahmed@12#")
            time.sleep(1)
            login_btn = page.locator("div[role='button']:has-text('تسجيل الدخول'), button:has-text('تسجيل الدخول')").first
            if login_btn.is_visible():
                login_btn.click()
            else:
                page.keyboard.press("Enter")
            time.sleep(8)
            new_cookies = context.cookies()
            if any(c.get("name") == "c_user" for c in new_cookies):
                fb_cookies_manager.save_new_cookies(new_cookies)
                print("[+] Saved fresh cookies after auto-login!")
    except Exception as auth_err:
        print(f"[!] Warning checking auth: {auth_err}")

    if "login" in page.url or "checkpoint" in page.url:
        print("[!] Cookies are invalid or expired.")
        send_telegram_alert("❌ <b>فشل النشر:</b> الكوكيز المستخدمة منتهية أو تم تسجيل الخروج. يرجى إرسال كوكيز جديدة.")
        browser.close()
        p.stop()
        return

    print("[+] Login confirmed on Facebook!")
    send_telegram_alert("✅ <b>تم تسجيل الدخول لفيسبوك بنجاح!</b> جاري بدء النشر في الجروبات الآن...")
    
    total_posted_session = 0

    while True:
        if os.path.exists(STOP_FILE):
            print("[*] Stop signal detected. Exiting poster.")
            send_telegram_alert("🛑 تم إيقاف سكريبت النشر التلقائي بناءً على طلبك.")
            break

        all_groups = get_target_groups()
        posted = get_posted_groups()
        pending = [g for g in all_groups if g not in posted]

        if not pending:
            print("[*] All groups have been processed! Recycling in 2 hours...")
            send_telegram_alert("🎉 <b>تم المرور على جميع الجروبات (1330 جروب) بنجاح!</b> سيبدأ السكريبت دورة جديدة بعد ساعتين.")
            time.sleep(7200)
            continue

        for group_url in pending:
            if os.path.exists(STOP_FILE):
                break

            print(f"\n[*] Navigating to: {group_url}")
            try:
                page.goto(group_url, wait_until="domcontentloaded", timeout=45000)
                time.sleep(random.uniform(4, 6))

                # 1. فحص زر الانضمام للجروب إذا لم نكن أعضاء
                join_res = page.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll("div[role='button']"));
                    const joinBtn = btns.find(b => {
                        const t = (b.textContent || '').trim();
                        const aria = (b.getAttribute('aria-label') || '').trim();
                        return (t === 'انضمام' || t === 'Join' || t.includes('انضمام إلى المجموعة') || aria === 'انضمام') && b.offsetParent !== null;
                    });
                    if (joinBtn) {
                        joinBtn.click();
                        return true;
                    }
                    return false;
                }""")
                if join_res:
                    print(f"[+] Clicked Join button on {group_url}")
                    time.sleep(3)

                # 2. النقر على صندوق كتابة المنشور داخل الفيد
                box_clicked = page.evaluate("""() => {
                    const feed = document.querySelector("div[role='feed'], div[role='main']") || document;
                    const btns = Array.from(feed.querySelectorAll("div[role='button']"));
                    for (let b of btns) {
                        const txt = (b.textContent || '').trim();
                        const aria = (b.getAttribute('aria-label') || '').trim();
                        if (txt.includes('اكتب') || txt.includes('Write') || aria.includes('إنشاء منشور') || aria.includes('Create a public post')) {
                            b.scrollIntoView({ behavior: 'instant', block: 'center' });
                            b.click();
                            return true;
                        }
                    }
                    return false;
                }""")

                if not box_clicked:
                    print("[!] Post box not accessible (pending admin approval or restricted). Moving next.")
                    # فاصل زمني قصير 15 ثانية للجروبات التي تحتاج موافقة أدمن
                    time.sleep(15)
                    continue

                # 3. صندوق المنشور فُتح بنجاح: التركيز والكتابة مع الحفاظ على الأسطر بدقة
                time.sleep(3)
                focused = page.evaluate("""() => {
                    const editors = Array.from(document.querySelectorAll("div[role='textbox'], div[contenteditable='true']"));
                    const postEditor = editors.find(el => {
                        const aria = el.getAttribute('aria-label') || '';
                        return el.offsetParent !== null && !aria.includes('تعليق') && !aria.includes('Comment');
                    });
                    if (postEditor) {
                        postEditor.focus();
                        return true;
                    }
                    return false;
                }""")

                if not focused:
                    print("[!] Failed to focus post editor. Skipping.")
                    mark_posted(group_url)
                    time.sleep(15)
                    continue

                # كتابة النص سطراً بسطر مع Shift+Enter لضمان الحفاظ على المسافات والشكل الجمالي
                paragraphs = POST_TEXT.split('\n')
                for i, para in enumerate(paragraphs):
                    if para:
                        page.keyboard.type(para, delay=10)
                    page.keyboard.press("Shift+Enter")
                    time.sleep(0.05)

                time.sleep(2)

                # 4. رفع صورة العروض الرسمية (offer.jpg)
                if os.path.exists(OFFER_IMG):
                    print("[*] Uploading offer image...")
                    try:
                        with page.expect_file_chooser(timeout=7000) as fc_info:
                            page.evaluate("""() => {
                                const btns = Array.from(document.querySelectorAll("div[role='dialog'] div[role='button'], div[role='dialog'] div[aria-label]"));
                                for (let b of btns) {
                                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                                    if (aria.includes('صورة') || aria.includes('photo') || aria.includes('video')) {
                                        b.click();
                                        return;
                                    }
                                }
                            }""")
                        file_chooser = fc_info.value
                        file_chooser.set_files(OFFER_IMG)
                        print("[+] Successfully attached offer.jpg to the post!")
                        time.sleep(5)
                    except Exception as img_err:
                        print(f"[!] File chooser direct click error: {img_err}")
                        try:
                            page.evaluate("""() => {
                                const btns = Array.from(document.querySelectorAll("div[role='dialog'] div[role='button'], div[role='dialog'] div[aria-label]"));
                                for (let b of btns) {
                                    const aria = (b.getAttribute('aria-label') || '').toLowerCase();
                                    if (aria.includes('صورة') || aria.includes('photo') || aria.includes('video')) {
                                        b.click();
                                        return;
                                    }
                                }
                            }""")
                            time.sleep(2)
                            fi = page.locator("div[role='dialog'] input[type='file'], input[type='file']").first
                            fi.set_input_files(OFFER_IMG)
                            time.sleep(5)
                        except Exception as e2:
                            print(f"[!] Fallback input error: {e2}")

                # 5. النقر على زر النشر
                published = page.evaluate("""() => {
                    const btns = Array.from(document.querySelectorAll("div[role='button']"));
                    const postBtn = btns.find(b => {
                        const txt = (b.textContent || '').trim();
                        const aria = (b.getAttribute('aria-label') || '').trim();
                        return (txt === 'نشر' || txt === 'Post' || aria === 'نشر' || aria === 'Post') && b.offsetParent !== null;
                    });
                    if (postBtn) {
                        postBtn.click();
                        return true;
                    }
                    return false;
                }""")

                if published:
                    time.sleep(8)
                    mark_posted(group_url)
                    total_posted_session += 1
                    print(f"[+] Successfully posted to: {group_url}")

                    cooldown_sec = random.randint(240, 360) # 4 إلى 6 دقائق أمان
                    cooldown_min = cooldown_sec // 60

                    success_msg = (
                        f"📢 <b>[نشر تلقائي ناجح من الأرديبي] 🍊🔥</b>\n\n"
                        f"✅ <b>تم النشر في الجروب:</b>\n{group_url}\n\n"
                        f"📊 <b>إجمالي منشورات الجلسة:</b> {total_posted_session} منشور\n"
                        f"🕒 <b>التوقيت:</b> {datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')}\n"
                        f"⏳ <b>المنشور القادم خلال:</b> {cooldown_min} دقائق (لحماية حسابك من الحظر)"
                    )
                    send_telegram_alert(success_msg)

                    print(f"[*] Sleeping {cooldown_min} minutes for safety...")
                    time.sleep(cooldown_sec)
                else:
                    print("[!] Publish button could not be clicked.")
                    mark_posted(group_url)
                    time.sleep(15)

            except Exception as e:
                print(f"[!] Error in {group_url}: {e}")
                time.sleep(15)

    try:
        browser.close()
        p.stop()
    except Exception:
        pass

if __name__ == "__main__":
    run_rdp_poster()
