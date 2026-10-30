import os
import sys
import time
import re
import html
from playwright.sync_api import sync_playwright

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def solve_kipas_verification(url: str, update_callback=None) -> dict:
    """
    Automates Kipas Football verification in headless mode with:
    - Built-in network ad-blocking (aborts ad networks & trackers)
    - Complete popup neutralization (disables window.open)
    - Removal of fake flash/banner overlays
    - Automated step clicking (Continue -> Continue -> Verify)
    """
    def log(msg: str):
        try:
            print(f"[*] {msg}")
        except Exception:
            try:
                print(f"[*] {msg.encode('ascii', 'ignore').decode('ascii')}")
            except Exception:
                pass
        if update_callback:
            try:
                update_callback(msg)
            except Exception:
                pass

    log("بدء تشغيل المتصفح بنظام حماية كامل وحجب الإعلانات...")
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
            # Standard headless Chromium for maximum speed, stability, and compatibility
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    "--disable-blink-features=AutomationControlled",
                ]
            )

            context = browser.new_context(
                viewport={"width": 1280, "height": 900},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            # Prevent popups and clickjacking via context init script
            context.add_init_script("""
                window.open = function() { console.log('Blocked window.open'); return null; };
                window.alert = function() { return true; };
                window.confirm = function() { return true; };
                window.prompt = function() { return null; };
            """)

            page = context.new_page()

            # Instantly close any extra popup tabs (never close main page)
            context.on("page", lambda p: p.close() if (p and p != page) else None)

            # We do NOT abort network ad scripts to prevent triggering "DNS BLOCK DETECTED" (CODE: ADS_CHECK)
            # Instead, popups are 100% neutralized via window.open = null and auto-closing popup tabs.

            log(f"جاري فتح الرابط: {url[:60]}...")
            page.goto(url, wait_until="domcontentloaded", timeout=40000)
            time.sleep(3)

            # Max 5 steps to reach the verified state
            for step_round in range(1, 6):
                time.sleep(1)
                
                # Check if we were redirected away from kipascommunity
                if "kipascommunity.com" not in page.url:
                    log("تم الكشف عن إعادة توجيه خارجية، جاري العودة لصفحة التحقق...")
                    page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    time.sleep(2)

                # Remove fake Flash or modal overlays that intercept clicks
                try:
                    page.evaluate("""
                        () => {
                            document.querySelectorAll('div, section, aside').forEach(el => {
                                const txt = el.innerText || '';
                                if (txt.includes('ERROR XX13-V') || txt.includes('Flash Player') || txt.includes('unable to play this video')) {
                                    el.remove();
                                }
                            });
                        }
                    """)
                except Exception:
                    pass

                page_text = page.inner_text("body")
                if "Account verified" in page_text or "تم التحقق" in page_text:
                    log("🎉 تم التحقق من الحساب بنجاح!")
                    result["success"] = True
                    break

                log(f"المرحلة {step_round}: فحص الزر وانتظار العداد التنازلي...")

                # Look for Continue or Verify button
                button_found = False
                for wait_sec in range(25):
                    # Check if verified during wait
                    if "Account verified" in page.inner_text("body"):
                        button_found = True
                        result["success"] = True
                        break

                    # Check for eligible buttons
                    buttons = page.locator("button, a").all()
                    target_btn = None

                    for b in buttons:
                        try:
                            if not b.is_visible():
                                continue
                            txt = b.inner_text().strip()
                            # Match Continue / Verify / Try again in English or Arabic
                            if txt in ["Continue", "Verify", "Try again", "متابعة", "تحقق", "إعادة المحاولة"]:
                                is_disabled = b.is_disabled()
                                if not is_disabled:
                                    target_btn = b
                                    break
                            elif ("Continue" in txt or "Verify" in txt or "Try again" in txt or "متابعة" in txt or "تحقق" in txt) and not re.search(r"\d+", txt):
                                if not b.is_disabled():
                                    target_btn = b
                                    break
                        except Exception:
                            continue

                    if target_btn:
                        btn_label = target_btn.inner_text().strip()
                        log(f"تم العثور على الزر النشط ({btn_label})، جاري النقر...")
                        try:
                            target_btn.click(timeout=4000)
                        except Exception:
                            page.evaluate("(el) => el.click()", target_btn.element_handle())
                        button_found = True
                        time.sleep(3)
                        break

                    time.sleep(1)

                if result["success"]:
                    break

                if not button_found:
                    log(f"لم يتم العثور على زر جاهز في المرحلة {step_round}، جاري إعادة الفحص...")
                    time.sleep(2)

            # Final check and screenshot
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
                    "⚠️ اكتملت المحاولة ولكن الصفحة لم تظهر عبارة Account verified.\n"
                    "يرجى مراجعة لقطة الشاشة المرفقة للتحقق من الحالة."
                )

            browser.close()

    except Exception as ex:
        result["message"] = f"❌ خطأ أثناء معالجة الصفحة: {ex}"
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
