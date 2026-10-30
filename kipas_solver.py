import os
import sys
import time
import re
import io
import zipfile
import requests
from playwright.sync_api import sync_playwright

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
UBLOCK_DIR = os.path.join(WORKSPACE_DIR, "ublock_extension", "uBlock0.chromium")
USER_DATA_DIR = os.path.join(WORKSPACE_DIR, "kipas_browser_profile")

def ensure_ublock():
    """Ensure uBlock Origin extension is downloaded and ready"""
    if os.path.exists(os.path.join(UBLOCK_DIR, "manifest.json")):
        return UBLOCK_DIR
    
    os.makedirs(os.path.dirname(UBLOCK_DIR), exist_ok=True)
    print("[*] Downloading uBlock Origin extension for ad-blocking...")
    url = "https://github.com/gorhill/uBlock/releases/download/1.75.0/uBlock0_1.75.0.chromium.zip"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
            z.extractall(os.path.join(WORKSPACE_DIR, "ublock_extension"))
        print("[+] uBlock Origin downloaded & extracted successfully.")
        return UBLOCK_DIR
    except Exception as e:
        print(f"[!] Warning: Failed to download uBlock: {e}. Will continue without extension.")
        return None

def solve_kipas_verification(url: str, update_callback=None) -> dict:
    """
    Automates Kipas Football verification with ad-blocking and auto-click.
    """
    def log(msg: str):
        print(f"[*] {msg}")
        if update_callback:
            try:
                update_callback(msg)
            except Exception:
                pass

    log("بدء تشغيل المتصفح المحمي بمانع الإعلانات...")
    ublock_path = ensure_ublock()

    launch_args = [
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--disable-blink-features=AutomationControlled",
    ]
    if ublock_path and os.path.exists(ublock_path):
        launch_args.extend([
            f"--disable-extensions-except={ublock_path}",
            f"--load-extension={ublock_path}",
        ])

    screenshot_path = os.path.join(WORKSPACE_DIR, f"kipas_result_{int(time.time())}.png")
    result = {
        "success": False,
        "player": "",
        "player_id": "",
        "valid_until": "",
        "message": "",
        "screenshot": ""
    }

    try:
        with sync_playwright() as p:
            # We use launch_persistent_context to allow extension loading
            context = p.chromium.launch_persistent_context(
                user_data_dir=USER_DATA_DIR,
                headless=False,  # Visible or seamless
                args=launch_args,
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            # Auto-close any ad popups / new tabs opened by scripts
            def on_page_open(new_page):
                try:
                    time.sleep(0.5)
                    log("تم كشف نافذة إعلانية منبثقة وتم إغلاقها فوراً.")
                    new_page.close()
                except Exception:
                    pass

            context.on("page", on_page_open)

            page = context.pages[0] if context.pages else context.new_page()
            
            # Block known ad domains as an extra layer of defense
            def block_ads(route):
                req_url = route.request.url.lower()
                ad_keywords = [
                    "doubleclick", "adsterra", "popads", "onclickads", "monetag",
                    "hilltopads", "propellerads", "exoclick", "google-analytics",
                    "googlesyndication", "adservice"
                ]
                if any(kw in req_url for kw in ad_keywords):
                    route.abort()
                else:
                    route.continue_()

            try:
                page.route("**/*", block_ads)
            except Exception:
                pass

            log(f"جاري فتح رابط التحقق...")
            page.goto(url, wait_until="domcontentloaded", timeout=45000)
            time.sleep(3)

            # Max 5 iterations to go through Step 1, Step 2, Step 3 -> Success
            max_rounds = 6
            for round_num in range(1, max_rounds + 1):
                page.bring_to_front()
                content = page.content()

                # Check if already verified
                if "Account verified" in content or "تم التحقق" in content:
                    log("🎉 ظهرت شاشة التحقق بنجاح!")
                    result["success"] = True
                    break

                # Extract current step or state if available
                step_match = re.search(r"Step\s*(\d)\s*of\s*(\d)", content, re.IGNORECASE)
                step_text = f"خطوة {step_match.group(1)} من {step_match.group(2)}" if step_match else f"مرحلة {round_num}"

                log(f"جاري معالجة {step_text}...")

                # Look for the active verification button (Continue / Verify / متابعة / تحقق)
                button_selectors = [
                    "button:has-text('Continue')",
                    "button:has-text('متابعة')",
                    "button:has-text('Verify')",
                    "button:has-text('تحقق')",
                    "a:has-text('Continue')",
                    "a:has-text('Verify')",
                    "a:has-text('متابعة')",
                    "a:has-text('تحقق')",
                    "button.btn-primary",
                    "button[type='submit']"
                ]

                # Wait for any countdown timer to finish (up to 25 seconds)
                btn = None
                timer_waited = 0
                while timer_waited < 25:
                    for sel in button_selectors:
                        loc = page.locator(sel).first
                        if loc.count() > 0 and loc.is_visible():
                            # Check if button is disabled or still showing countdown text
                            btn_text = loc.inner_text().strip()
                            is_disabled = loc.is_disabled() or "wait" in btn_text.lower() or "انتظر" in btn_text or re.search(r"\d+s?", btn_text)
                            if not is_disabled:
                                btn = loc
                                break
                    if btn:
                        break
                    time.sleep(1)
                    timer_waited += 1

                if not btn:
                    # Try finding any visible button inside the main container
                    for sel in button_selectors:
                        loc = page.locator(sel).first
                        if loc.count() > 0 and loc.is_visible():
                            btn = loc
                            break

                if btn:
                    btn_text = btn.inner_text().strip()
                    log(f"تم العثور على الزر ({btn_text})، جاري النقر...")
                    
                    # Scroll into view and click
                    try:
                        btn.scroll_into_view_if_needed(timeout=3000)
                    except Exception:
                        pass

                    try:
                        btn.click(timeout=5000)
                    except Exception:
                        # Fallback click via JS
                        page.evaluate("(el) => el.click()", btn.element_handle())

                    log(f"تم الضغط على ({btn_text}). بانتظار استجابة الصفحة...")
                    time.sleep(4)
                else:
                    log("لم يتم العثور على زر مباشر، جاري الانتظار 3 ثوانٍ...")
                    time.sleep(3)

            # Final check and screenshot
            page.bring_to_front()
            time.sleep(2)
            page.screenshot(path=screenshot_path, full_page=False)
            result["screenshot"] = screenshot_path

            final_text = page.inner_text("body")
            if "Account verified" in final_text or "verified" in final_text.lower():
                result["success"] = True

                # Extract player details
                p_match = re.search(r"Player\s+([^\s·]+)\s*·\s*ID\s*(\d+)", final_text, re.IGNORECASE)
                if p_match:
                    result["player"] = p_match.group(1)
                    result["player_id"] = p_match.group(2)

                valid_match = re.search(r"Login is allowed until[^\.]+\.", final_text, re.IGNORECASE)
                if valid_match:
                    result["valid_until"] = valid_match.group(0)

                result["message"] = (
                    "✅ <b>تم التحقق وتوثيق الحساب بنجاح!</b>\n\n"
                    f"👤 <b>اسم اللاعب:</b> <code>{result['player']}</code>\n"
                    f"🆔 <b>معرف الحساب (ID):</b> <code>{result['player_id']}</code>\n"
                    f"⏱ <b>الصلاحية:</b> {result['valid_until'] or '40 دقيقة'}\n\n"
                    "🎮 يمكنك الآن فتح اللعبة وسيسجل الدخول تلقائياً."
                )
            else:
                result["message"] = (
                    "⚠️ انتهت المحاولة ولكن الصفحة لم تؤكد التحقق بنجاح بعد.\n"
                    "يرجى مراجعة الصورة المرفقة لمعرفة حالة الصفحة."
                )

            context.close()

    except Exception as ex:
        result["message"] = f"❌ حدث خطأ أثناء تنفيذ التحقق: {ex}"
        log(f"Error: {ex}")

    return result

if __name__ == "__main__":
    test_url = sys.argv[1] if len(sys.argv) > 1 else ""
    if test_url:
        print(f"Testing Kipas Solver on: {test_url}")
        res = solve_kipas_verification(test_url)
        print("Result:", res["message"])
        print("Screenshot:", res["screenshot"])
    else:
        print("Usage: python kipas_solver.py <verify_url>")
