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
    - Completely blocks all file downloads (accept_downloads=False & d.cancel())
    - Strictly filters buttons to only click genuine verification buttons (Continue, Verify, Try again)
    - Automatically eliminates ad buttons (Free Download, Install, WPS Office, Opera, etc.)
    - Prevents sponsor page redirects and restores verification page instantly
    - Captures player info & success screenshot
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
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
                accept_downloads=False
            )

            # Completely disable and cancel all downloads
            context.on("download", lambda d: d.cancel())

            # Script to neutralize popups, fake alerts, and ad-triggered downloads
            context.add_init_script("""
                window.open = function() { console.log('Blocked popup window.open'); return null; };
                window.alert = function() { return true; };
                window.confirm = function() { return true; };
                window.prompt = function() { return null; };

                // Intercept and prevent ad clicks that trigger downloads
                document.addEventListener('click', function(e) {
                    const el = e.target.closest('a, button, [role="button"]');
                    if (!el) return;
                    const txt = (el.innerText || el.textContent || '').trim().toLowerCase();
                    const href = (el.getAttribute('href') || '').toLowerCase();
                    const isAdDownload = el.hasAttribute('download') || 
                                         /(\.exe|\.zip|\.apk|\.msi|setup|download)/i.test(href) ||
                                         /(free download|download now|install now|start download)/i.test(txt);
                    const isVerifyBtn = /(continue|verify|try again|متابعة|تحقق)/i.test(txt);

                    if (isAdDownload && !isVerifyBtn) {
                        console.log('Blocked ad download click:', txt);
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        try { el.remove(); } catch(err) {}
                        return false;
                    }
                }, true);
            """)

            page = context.new_page()
            page.on("download", lambda d: d.cancel())
            page.on("dialog", lambda d: d.dismiss())
            context.on("page", lambda p: p.close() if (p and p != page) else None)

            log("جاري فتح صفحة التحقق وتحميل كابتشا Cloudflare Turnstile...")
            page.goto(url, wait_until="domcontentloaded", timeout=45000)

            # Polling loop (max 75 seconds total)
            step_history = []
            max_wait_seconds = 75
            loop_start = time.time()

            while time.time() - loop_start < max_wait_seconds:
                time.sleep(1)

                # 0. Check if page was hijacked/redirected to an ad domain
                current_url = page.url
                if "kipascommunity.com/verify" not in current_url:
                    log(f"⚠️ رصد تحويل لصفحة إعلانية ({current_url[:40]}...)! جاري الرجوع فوراً لصفحة التحقق...")
                    try:
                        page.goto(url, wait_until="domcontentloaded", timeout=30000)
                    except Exception:
                        pass
                    time.sleep(1.5)
                    continue

                # 1. Clean fake overlays and ad banners from DOM
                try:
                    page.evaluate("""
                        () => {
                            // Remove ad iframes (keep Cloudflare Turnstile)
                            document.querySelectorAll('iframe').forEach(f => {
                                const src = (f.src || '').toLowerCase();
                                if (!src.includes('cloudflare') && !src.includes('turnstile') && !src.includes('challenges')) {
                                    try { f.remove(); } catch(e) {}
                                }
                            });
                            // Remove ad banners and fake download buttons
                            document.querySelectorAll('div, section, aside, a, button').forEach(el => {
                                const t = (el.innerText || '').toLowerCase();
                                if (t.includes('free download') || t.includes('download now') || 
                                    t.includes('install now') || t.includes('wps office') || 
                                    t.includes('opera gx') || t.includes('error xx13-v') || 
                                    t.includes('flash player')) {
                                    try { el.remove(); } catch(e) {}
                                }
                            });
                        }
                    """)
                except Exception:
                    pass

                body_text = page.inner_text("body")

                # 2. Check if link was already used / expired
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

                # 3. Check if verified successfully
                if "Account verified" in body_text:
                    log("🎉 تم التحقق وتوثيق الحساب بنجاح! شاشة Account verified ظاهرة.")
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

                # 4. Check step indicator
                step_match = re.search(r"Step\s*(\d)\s*of\s*(\d)", body_text, re.IGNORECASE)
                step_text = step_match.group(0) if step_match else "المرحلة الحالية"

                # 5. STRICT BUTTON INSPECTION: Only allow genuine Kipas buttons
                btn_info = page.evaluate("""
                    () => {
                        const allowed = ['continue', 'verify', 'try again', 'متابعة', 'تحقق', 'إعادة المحاولة'];
                        const forbidden = /download|install|free|tải|wps|opera|accept|agree|open|start|play|signup|register|allow|update|vpn/i;

                        // Check inside .card or main first, then fallback to form or document
                        const containers = [
                            document.querySelector('.card'),
                            document.querySelector('main'),
                            document.querySelector('form'),
                            document.body
                        ];

                        let candidate = null;
                        for (const container of containers) {
                            if (!container) continue;
                            const buttons = Array.from(container.querySelectorAll('button, a.btn, input[type="submit"]'));
                            for (const b of buttons) {
                                const txt = (b.innerText || b.value || b.textContent || '').trim();
                                const lower = txt.toLowerCase();

                                // Ignore forbidden ad texts completely
                                if (forbidden.test(lower)) continue;

                                const isMatch = allowed.some(a => lower === a || lower.startsWith(a));
                                const isWait = lower.includes('wait') || lower.includes('preparing') || lower.includes('انتظر');

                                if (isMatch || isWait) {
                                    candidate = { el: b, text: txt, isMatch: isMatch, isWait: isWait };
                                    break;
                                }
                            }
                            if (candidate) break;
                        }

                        if (!candidate) return { found: false };

                        const b = candidate.el;
                        const txt = candidate.text;
                        const lower = txt.toLowerCase();
                        const style = window.getComputedStyle(b);
                        const isHidden = b.hidden || style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0';
                        const isDisabled = b.disabled || 
                                           b.getAttribute('aria-disabled') === 'true' || 
                                           b.classList.contains('disabled') ||
                                           candidate.isWait;

                        return {
                            found: true,
                            text: txt,
                            disabled: isDisabled,
                            hidden: isHidden,
                            canClick: candidate.isMatch && !isDisabled && !isHidden
                        };
                    }
                """)

                if btn_info.get("found") and not btn_info.get("hidden"):
                    txt = btn_info.get("text", "")
                    can_click = btn_info.get("canClick", False)
                    disabled = btn_info.get("disabled", True)

                    state_key = f"{step_text} -> [{txt}]"
                    if state_key not in step_history:
                        step_history.append(state_key)
                        log(f"[{step_text}] الزر المكتشف: [{txt}] | جاهز: {'نعم' if can_click else 'انتظار العداد/الكابتشا'}")

                    if can_click:
                        log(f"🚀 الضغط على زر التوثيق: [{txt}] في مرحلة ({step_text})...")
                        # Perform click via evaluate on the exact matching element
                        clicked = page.evaluate("""
                            () => {
                                const allowed = ['continue', 'verify', 'try again', 'متابعة', 'تحقق', 'إعادة المحاولة'];
                                const forbidden = /download|install|free|tải|wps|opera|accept|agree|open|start|play|signup|register|allow|update|vpn/i;

                                const buttons = Array.from(document.querySelectorAll('button, a.btn, input[type="submit"]'));
                                for (const b of buttons) {
                                    const txt = (b.innerText || b.value || b.textContent || '').trim();
                                    const lower = txt.toLowerCase();
                                    if (forbidden.test(lower)) continue;
                                    if (allowed.some(a => lower === a || lower.startsWith(a))) {
                                        b.click();
                                        return true;
                                    }
                                }
                                return false;
                            }
                        """)
                        if not clicked:
                            # Fallback using locator
                            for act in ["Continue", "Verify", "Try again", "متابعة", "تحقق"]:
                                loc = page.locator(f"button:has-text('{act}'), a:has-text('{act}')").first
                                if loc.is_visible() and loc.is_enabled():
                                    loc.click()
                                    break
                        time.sleep(2.5)

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
