import os
import sys
import json
import base64

# Base64-encoded default verified Facebook cookies (User: Orange Dsl - 61586169623093)
EMBEDDED_COOKIES_B64 = """
Ww0KICB7DQogICAgIm5hbWUiOiAicHNfbCIsDQogICAgInZhbHVlIjogIjEiLA0KICAgICJkb21haW4iOiAiLmZhY2Vib29rLmNvbSIsDQogICAgInBhdGgiOiAiLyIsDQogICAgImV4cGlyZXMiOiAtMSwNCiAgICAiaHR0cE9ubHkiOiB0cnVlLA0KICAgICJzZWN1cmUiOiB0cnVlLA0KICAgICJzYW1lU2l0ZSI6ICJMYXgiDQogIH0sDQogIHsNCiAgICAibmFtZSI6ICJkYXRyIiwNCiAgICAidmFsdWUiOiAicW1QNmFkQ25YcHNlUVRvOGZsbmh4aFhaIiwNCiAgICAiZG9tYWluIjogIi5mYWNlYm9vay5jb20iLA0KICAgICJwYXRoIjogIi8iLA0KICAgICJleHBpcmVzIjogLTEsDQogICAgImh0dHBPbmx5IjogdHJ1ZSwNCiAgICAic2VjdXJlIjogdHJ1ZSwNCiAgICAic2FtZVNpdGUiOiAiTm9uZSINCiAgfSwNCiAgew0KICAgICJuYW1lIjogImRwciIsDQogICAgInZhbHVlIjogIjAuMzEyNSIsDQogICAgImRvbWFpbiI6ICIuZmFjZWJvb2suY29tIiwNCiAgICAicGF0aCI6ICIvIiwNCiAgICAiZXhwaXJlcyI6IC0xLA0KICAgICJodHRwT25seSI6IGZhbHNlLA0KICAgICJzZWN1cmUiOiB0cnVlLA0KICAgICJzYW1lU2l0ZSI6ICJOb25lIg0KICB9LA0KICB7DQogICAgIm5hbWUiOiAicHNfbiIsDQogICAgInZhbHVlIjogIjEiLA0KICAgICJkb21haW4iOiAiLmZhY2Vib29rLmNvbSIsDQogICAgInBhdGgiOiAiLyIsDQogICAgImV4cGlyZXMiOiAtMSwNCiAgICAiaHR0cE9ubHkiOiB0cnVlLA0KICAgICJzZWN1cmUiOiB0cnVlLA0KICAgICJzYW1lU2l0ZSI6ICJOb25lIg0KICB9LA0KICB7DQogICAgIm5hbWUiOiAic2IiLA0KICAgICJ2YWx1ZSI6ICJxbVA2YVFkb1UzaE03OWUwZWZQXzE0bEEiLA0KICAgICJkb21haW4iOiAiLmZhY2Vib29rLmNvbSIsDQogICAgInBhdGgiOiAiLyIsDQogICAgImV4cGlyZXMiOiAxODI2NTQzMzY3Ljg5MTM5MSwNCiAgICAiaHR0cE9ubHkiOiB0cnVlLA0KICAgICJzZWN1cmUiOiB0cnVlLA0KICAgICJzYW1lU2l0ZSI6ICJOb25lIg0KICB9LA0KICB7DQogICAgIm5hbWUiOiAid2QiLA0KICAgICJ2YWx1ZSI6ICIxMjgweDkwMCIsDQogICAgImRvbWFpbiI6ICIuZmFjZWJvb2suY29tIiwNCiAgICAicGF0aCI6ICIvIiwNCiAgICAiZXhwaXJlcyI6IDE3OTI1ODgxNzMsDQogICAgImh0dHBPbmx5IjogZmFsc2UsDQogICAgInNlY3VyZSI6IHRydWUsDQogICAgInNhbWVTaXRlIjogIkxheCINCiAgfSwNCiAgew0KICAgICJuYW1lIjogImNfdXNlciIsDQogICAgInZhbHVlIjogIjYxNTg2MTY5NjIzMDkzIiwNCiAgICAiZG9tYWluIjogIi5mYWNlYm9vay5jb20iLA0KICAgICJwYXRoIjogIi8iLA0KICAgICJleHBpcmVzIjogMTgyMzUxOTM3MS43MzUxMTMsDQogICAgImh0dHBPbmx5IjogZmFsc2UsDQogICAgInNlY3VyZSI6IHRydWUsDQogICAgInNhbWVTaXRlIjogIk5vbmUiDQogIH0sDQogIHsNCiAgICAibmFtZSI6ICJmciIsDQogICAgInZhbHVlIjogIjE2bkREaU1uaXdjV043YnoyLkFXZHIzejVhdU55UmtFdzRsbXhkTzlidnRNaUVZQWxoV3FJelBwZVJEeGZYVXJpWnUwZy5CcXozOE4uLkFBQS4wLjAuQnF6MzhOLkFXY1pFT3ZULUFuZXFYZHpfU3o5ZDQ1dnM2TSIsDQogICAgImRvbWFpbiI6ICIuZmFjZWJvb2suY29tIiwNCiAgICAicGF0aCI6ICIvIiwNCiAgICAiZXhwaXJlcyI6IDE3OTk3NTkzNzEuNzM1MjU2LA0KICAgICJodHRwT25seSI6IHRydWUsDQogICAgInNlY3VyZSI6IHRydWUsDQogICAgInNhbWVTaXRlIjogIk5vbmUiDQogIH0sDQogIHsNCiAgICAibmFtZSI6ICJ4cyIsDQogICAgInZhbHVlIjogIjMyJTNBb2lGd3hYcVVDcWpEd0ElM0EyJTNBMTc5MTk4MzM2OCUzQS0xJTNBLTElM0ElM0FBY3owR2xwUlZEX1cybE9RNHJ0Xzd5TEJxTGJFeW1DTWpjZzB0NHpUdHciLA0KICAgICJkb21haW4iOiAiLmZhY2Vib29rLmNvbSIsDQogICAgInBhdGgiOiAiLyIsDQogICAgImV4cGlyZXMiOiAxODIzNTE5MzcxLjczNTM0MiwNCiAgICAiaHR0cE9ubHkiOiB0cnVlLA0KICAgICJzZWN1cmUiOiB0cnVlLA0KICAgICJzYW1lU2l0ZSI6ICJOb25lIg0KICB9DQpd
"""

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
COOKIES_FILE = os.path.join(WORKSPACE_DIR, "fb_cookies.json")

def sanitize_cookies(cookies_list):
    """تهيئة الكوكيز لتكون متوافقة تماماً مع Playwright وتجنب أخطاء المتصفح"""
    sanitized = []
    for c in cookies_list:
        if not isinstance(c, dict) or "name" not in c or "value" not in c:
            continue
        item = {
            "name": str(c["name"]),
            "value": str(c["value"]),
            "domain": c.get("domain", ".facebook.com"),
            "path": c.get("path", "/")
        }
        if "secure" in c:
            item["secure"] = bool(c["secure"])
        if "httpOnly" in c:
            item["httpOnly"] = bool(c["httpOnly"])
        if "sameSite" in c:
            s = str(c["sameSite"]).lower()
            if s == "strict":
                item["sameSite"] = "Strict"
            elif s == "lax":
                item["sameSite"] = "Lax"
            elif s in ["none", "no_restriction"]:
                item["sameSite"] = "None"
        sanitized.append(item)
    return sanitized

def get_cookies():
    """جلب الكوكيز من الملف المحلي أو السيكرتس أو النسخة الاحتياطية المضمنة"""
    # 1. فحص وجود الملف المحلي
    if os.path.exists(COOKIES_FILE):
        try:
            with open(COOKIES_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if content:
                    parsed = json.loads(content)
                    print("[+] Loaded cookies from local fb_cookies.json")
                    return sanitize_cookies(parsed)
        except Exception as e:
            print(f"[!] Warning reading fb_cookies.json: {e}")

    # 2. فحص متغير البيئة
    env_c = os.getenv("FB_COOKIES")
    if env_c:
        try:
            parsed = json.loads(env_c)
            print("[+] Loaded cookies from FB_COOKIES environment variable")
            return sanitize_cookies(parsed)
        except Exception as e:
            print(f"[!] Warning parsing FB_COOKIES env: {e}")

    # 3. الاعتماد على النسخة المضمنة المشفرة
    try:
        raw_json = base64.b64decode(EMBEDDED_COOKIES_B64.strip()).decode("utf-8")
        parsed = json.loads(raw_json)
        # كتابتها للملف المحلي لاستخدامها مستقبلاً
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            f.write(raw_json)
        print("[+] Loaded cookies from embedded backup and saved to fb_cookies.json")
        return sanitize_cookies(parsed)
    except Exception as e:
        print(f"[!] Critical: Failed to decode embedded cookies: {e}")

    return None

def save_new_cookies(cookie_data):
    """حفظ كوكيز جديدة يتم إرسالها من تيليجرام وتحديث الملف"""
    try:
        if isinstance(cookie_data, str):
            parsed = json.loads(cookie_data)
        else:
            parsed = cookie_data
        with open(COOKIES_FILE, "w", encoding="utf-8") as f:
            json.dump(parsed, f, ensure_ascii=False, indent=2)
        print("[+] Successfully saved new cookies to fb_cookies.json")
        return True
    except Exception as e:
        print(f"[!] Error saving new cookies: {e}")
        return False
