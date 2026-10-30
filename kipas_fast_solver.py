import os
import sys
import time
import re
import json
from playwright.sync_api import sync_playwright

if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))

def fast_verify(url: str, headless: bool = True, on_progress=None) -> dict:
    """
    Ultra-fast and resilient Kipas Football verification solver:
    - Runs in headless or visible mode
    - Neutralizes popups and fake modals
    - Avoids network aborts so site's anti-adblock check passes
    - Listens for countdown and triggers button clicks instantly upon readiness
    - Detects 'Link already used' immediately
    - Captures final verified screenshot & player info
    """
    def log(msg: str):
        try:
            print(f"[*] {msg}", flush=True)
        except Exception:
            pass
        if on_progress:
            try:
                on_progress(msg)
            except Exception:
                pass

    log(f"بدء المعالجة السريعة للرابط: {url[:60]}...")
    screenshot_path = os.path.join(WORKSPACE_DIR, f"kipas_verified_{int(time.time())}.png")

    result = {
        "success": False,
        "status": "pending",
        "message": "",
        "player": "",
        "player_id": "",
        "valid_until": "",
        "screenshot": ""
    }

    start_time = time.time()

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-blink-features=AutomationControlled",
                ]
            )

            context = browser.new_context(
                viewport={"width": 1280, "height": 800},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            )

            # Block popups without closing the main page
            context.add_init_script("""
                window.open = function() { console.log('Blocked popup window.open'); return null; };
                window.alert = function() { return true; };
                window.confirm = function() { return true; };
            """)

            page = context.new_page()
            context.on("page", lambda p: p.close() if (p and p != page) else None)

            log("جاري تحميل الصفحة وحل كابتشا Cloudflare Turnstile...")
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # Polling loop (max 70 seconds total)
            step_history = []
            max_wait_seconds = 70
            loop_start = time.time()

            while time.time() - loop_start < max_wait_seconds:
                time.sleep(1)

                # Clean fake overlays
                try:
                    page.evaluate("""
                        () => {
                            document.querySelectorAll('div, section, aside').forEach(el => {
                                const t = el.innerText || '';
                                if (t.includes('ERROR XX13-V') || t.includes('Flash Player')) el.remove();
                            });
                        }
                    """)
                except Exception:
                    pass

                body_text = page.inner_text("body")

                # 1. Check if link was already used / expired
                if "Link already used" in body_text:
                    log("⚠️ الرابط مستهلك بالفعل (Link already used)! تم فتحه أو استخدامه سابقاً.")
                    page.screenshot(path=screenshot_path)
                    result["status"] = "already_used"
                    result["screenshot"] = screenshot_path
                    result["message"] = (
                        "⚠️ <b>الرابط مُستهلك بالفعل (Link already used)!</b>\n\n"
                        "روابط التوثيق تُفتح <b>مرة واحدة فقط</b> من اللعبة. هذا الرابط تم فتحه أو انتهت صلاحيته.\n"
                        "يرجى فتح اللعبة وضغط زر Verify للحصول على رابط جديد ونسخه فوراً دون فتحه."
                    )
                    break

                # 2. Check if verified successfully
                if "Account verified" in body_text:
                    log("🎉 تم التحقق بنجاح! شاشة Account verified ظاهرة.")
                    time.sleep(1)
                    page.screenshot(path=screenshot_path)
                    result["success"] = True
                    result["status"] = "verified"
                    result["screenshot"] = screenshot_path

                    # Extract player info
                    p_match = re.search(r"Player\s+([^\s·]+)\s*·\s*ID\s*(\d+)", body_text, re.IGNORECASE)
                    if p_match:
                        result["player"] = p_match.group(1)
                        result["player_id"] = p_match.group(2)

                    v_match = re.search(r"Login is allowed until[^\.]+\.", body_text, re.IGNORECASE)
                    if v_match:
                        result["valid_until"] = v_match.group(0)

                    elapsed = round(time.time() - start_time, 1)
                    result["message"] = (
                        "✅ <b>تم التحقق وتوثيق الحساب بنجاح!</b> 🎉\n\n"
                        f"👤 <b>اسم اللاعب:</b> <code>{result['player']}</code>\n"
                        f"🆔 <b>معرف الحساب:</b> <code>{result['player_id']}</code>\n"
                        f"⏱ <b>الصلاحية:</b> {result['valid_until'] or '40 دقيقة'}\n"
                        f"⚡ <b>استغرق التحقق:</b> {elapsed} ثانية فقط!\n\n"
                        "🎮 يمكنك الآن فتح اللعبة وسيسجل الدخول تلقائياً."
                    )
                    break

                # 3. Check for active buttons (Continue / Verify / Try again)
                btn_state = page.evaluate("""
                    () => {
                        const btn = document.querySelector('button');
                        if (!btn) return { exists: false };
                        return {
                            exists: true,
                            text: btn.innerText.trim(),
                            disabled: btn.disabled,
                            hidden: btn.hidden
                        };
                    }
                """)

                if btn_state.get("exists") and not btn_state.get("hidden"):
                    txt = btn_state.get("text", "")
                    disabled = btn_state.get("disabled", True)
                    
                    # Track step
                    step_match = re.search(r"Step\s*(\d)\s*of\s*(\d)", body_text)
                    current_step = step_match.group(0) if step_match else txt

                    if current_step not in step_history:
                        step_history.append(current_step)
                        log(f"الحالة الحالية: {current_step} | الزر: [{txt}]")

                    if not disabled:
                        log(f"الزر جاهز للنقر الآن: [{txt}]! جاري الضغط...")
                        try:
                            page.evaluate("() => document.querySelector('button').click()")
                        except Exception:
                            page.locator("button").first.click()
                        time.sleep(2)
                else:
                    if "Preparing" in body_text:
                        # Still resolving turnstile
                        pass

            if not result["success"] and result["status"] == "pending":
                page.screenshot(path=screenshot_path)
                result["screenshot"] = screenshot_path
                result["message"] = "⚠️ لم يكتمل التحقق خلال الوقت المحدد. تم حفظ لقطة الشاشة."

            browser.close()

    except Exception as e:
        log(f"Error: {e}")
        result["message"] = f"❌ خطأ غير متوقع: {e}"

    return result

if __name__ == "__main__":
    test_link = ""
    if len(sys.argv) > 1:
        test_link = sys.argv[1].strip()
    else:
        print("=" * 60)
        print("       KIPAS FOOTBALL - FAST VERIFICATION SOLVER")
        print("=" * 60)
        try:
            test_link = input("\nPaste Kipas Verification URL (ضع رابط التحقق هنا): ").strip()
        except Exception:
            pass

    test_link = test_link.strip('"').strip("'").strip()

    if not test_link or not test_link.startswith("http"):
        print("\n[!] Error: Invalid or empty URL provided. Please provide a valid link starting with http/https.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    print(f"\n[*] Running Fast Solver on: {test_link[:70]}...\n")
    res = fast_verify(test_link, headless=False)
    print("\n" + "=" * 60)
    print("--- RESULT ---")
    print("Success:", res["success"])
    print("Status:", res["status"])
    print("\nMessage:\n" + re.sub(r'<[^>]+>', '', res["message"]))
    print("Screenshot:", res["screenshot"])
    print("=" * 60)
    input("\nPress Enter to exit...")
