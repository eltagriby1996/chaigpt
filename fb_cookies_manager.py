import os
import sys
import json
import base64

# Base64-encoded default verified Facebook cookies (User: Orange Dsl - 61586169623093)
EMBEDDED_COOKIES_B64 = """
WwogICAgewogICAgICAgICJkb21haW4iOiAiLmZhY2Vib29rLmNvbSIsCiAgICAgICAgImV4cGly
YXRpb25EYXRlIjogMTgxMjU3NzI3My4yMjUwNDMsCiAgICAgICAgImhvc3RPbmx5IjogZmFsc2Us
CiAgICAgICAgImh0dHBPbmx5IjogdHJ1ZSwKICAgICAgICAibmFtZSI6ICJwc19sIiwKICAgICAg
ICAicGF0aCI6ICIvIiwKICAgICAgICAic2FtZVNpdGUiOiAibGF4IiwKICAgICAgICAic2VjdXJl
IjogdHJ1ZSwKICAgICAgICAic2Vzc2lvbiI6IGZhbHNlLAogICAgICAgICJzdG9yZUlkIjogbnVs
bCwKICAgICAgICAidmFsdWUiOiAiMSIKICAgIH0sCiAgICB7CiAgICAgICAgImRvbWFpbiI6ICIu
ZmFjZWJvb2suY29tIiwKICAgICAgICAiZXhwaXJhdGlvbkRhdGUiOiAxODEyNTc3MTg3LjYyMzc3
OCwKICAgICAgICAiaG9zdE9ubHkiOiBmYWxzZSwKICAgICAgICAiaHR0cE9ubHkiOiB0cnVlLAog
ICAgICAgICJuYW1lIjogImRhdHIiLAogICAgICAgICJwYXRoIjogIi8iLAogICAgICAgICJzYW1l
U2l0ZSI6ICJub19yZXN0cmljdGlvbiIsCiAgICAgICAgInNlY3VyZSI6IHRydWUsCiAgICAgICAg
InNlc3Npb24iOiBmYWxzZSwKICAgICAgICAic3RvcmVJZCI6IG51bGwsCiAgICAgICAgInZhbHVl
IjogInFtUDZhZENuWHBzZVFUbzhmbG5oeGhYWiIKICAgIH0sCiAgICB7CiAgICAgICAgImRvbWFp
biI6ICIuZmFjZWJvb2suY29tIiwKICAgICAgICAiZXhwaXJhdGlvbkRhdGUiOiAxNzk5NzUyMjE5
LjA4MDEzMywKICAgICAgICAiaG9zdE9ubHkiOiBmYWxzZSwKICAgICAgICAiaHR0cE9ubHkiOiB0
cnVlLAogICAgICAgICJuYW1lIjogImZyIiwKICAgICAgICAicGF0aCI6ICIvIiwKICAgICAgICAi
c2FtZVNpdGUiOiAibm9fcmVzdHJpY3Rpb24iLAogICAgICAgICJzZWN1cmUiOiB0cnVlLAogICAg
ICAgICJzZXNzaW9uIjogZmFsc2UsCiAgICAgICAgInN0b3JlSWQiOiBudWxsLAogICAgICAgICJ2
YWx1ZSI6ICIxV1lhdnVjSWoxZkF3aWdpdC5BV2U2T0ZPQnpRLVRSdzl0QUFDRXhobXpaTXhYaEow
R0cyeG9lM1k2X2RRODZjSlo5VVUuQnF6Mk1LLi5BQUEuMC4wLkJxejJNZC5BV2ZKUVJzRHoyNzFj
YnhYdWg5LTNvbmNLWE0iCiAgICB9LAogICAgewogICAgICAgICJkb21haW4iOiAiLmZhY2Vib29r
LmNvbSIsCiAgICAgICAgImV4cGlyYXRpb25EYXRlIjogMTgyMzUxMjIwMC45NDU1ODMsCiAgICAg
ICAgImhvc3RPbmx5IjogZmFsc2UsCiAgICAgICAgImh0dHBPbmx5IjogdHJ1ZSwKICAgICAgICAi
bmFtZSI6ICJ4cyIsCiAgICAgICAgInBhdGgiOiAiLyIsCiAgICAgICAgInNhbWVTaXRlIjogIm5v
X3Jlc3RyaWN0aW9uIiwKICAgICAgICAic2VjdXJlIjogdHJ1ZSwKICAgICAgICAic2Vzc2lvbiI6
IGZhbHNlLAogICAgICAgICJzdG9yZUlkIjogbnVsbCwKICAgICAgICAidmFsdWUiOiAiNiUzQXlO
QTVQUGFGS3FDSldBJTNBMiUzQTE3OTE5NzYxOTglM0EtMSUzQS0xJTNBJTNBQWN4ZEwwNENHN0Fo
WFgxb0tELThmQ2RwbDkzTGFJU3ZYSVF3NzRzSllBIgogICAgfSwKICAgIHsKICAgICAgICAiZG9t
YWluIjogIi5mYWNlYm9vay5jb20iLAogICAgICAgICJleHBpcmF0aW9uRGF0ZSI6IDE4MjM1MTIy
MDAuOTQ1Mjc2LAogICAgICAgICJob3N0T25seSI6IGZhbHNlLAogICAgICAgICJodHRwT25seSI6
IGZhbHNlLAogICAgICAgICJuYW1lIjogImNfdXNlciIsCiAgICAgICAgInBhdGgiOiAiLyIsCiAg
ICAgICAgInNhbWVTaXRlIjogIm5vX3Jlc3RyaWN0aW9uIiwKICAgICAgICAic2VjdXJlIjogdHJ1
ZSwKICAgICAgICAic2Vzc2lvbiI6IGZhbHNlLAogICAgICAgICJzdG9yZUlkIjogbnVsbCwKICAg
ICAgICAidmFsdWUiOiAiNjE1ODYxNjk2MjMwOTMiCiAgICB9LAogICAgewogICAgICAgICJkb21h
aW4iOiAiLmZhY2Vib29rLmNvbSIsCiAgICAgICAgImhvc3RPbmx5IjogZmFsc2UsCiAgICAgICAg
Imh0dHBPbmx5IjogZmFsc2UsCiAgICAgICAgIm5hbWUiOiAicHJlc2VuY2UiLAogICAgICAgICJw
YXRoIjogIi8iLAogICAgICAgICJzYW1lU2l0ZSI6IG51bGwsCiAgICAgICAgInNlY3VyZSI6IHRy
dWUsCiAgICAgICAgInNlc3Npb24iOiB0cnVlLAogICAgICAgICJzdG9yZUlkIjogbnVsbCwKICAg
ICAgICAidmFsdWUiOiAiQyU3QiUyMnQzJTIyJTNBJTVCJTVEJTJDJTIydXRjMyUyMiUzQTE3OTE5
NzYyMjM1NDElMkMlMjJ2JTIyJTNBMSU3RCIKICAgIH0sCiAgICB7CiAgICAgICAgImRvbWFpbiI6
ICIuZmFjZWJvb2suY29tIiwKICAgICAgICAiZXhwaXJhdGlvbkRhdGUiOiAxNzkyNTgxMDIyLAog
ICAgICAgICJob3N0T25seSI6IGZhbHNlLAogICAgICAgICJodHRwT25seSI6IGZhbHNlLAogICAg
ICAgICJuYW1lIjogImRwciIsCiAgICAgICAgInBhdGgiOiAiLyIsCiAgICAgICAgInNhbWVTaXRl
IjogIm5vX3Jlc3RyaWN0aW9uIiwKICAgICAgICAic2VjdXJlIjogdHJ1ZSwKICAgICAgICAic2Vz
c2lvbiI6IGZhbHNlLAogICAgICAgICJzdG9yZUlkIjogbnVsbCwKICAgICAgICAidmFsdWUiOiAi
MC4zMTI1IgogICAgfSwKICAgIHsKICAgICAgICAiZG9tYWluIjogIi5mYWNlYm9vay5jb20iLAog
ICAgICAgICJleHBpcmF0aW9uRGF0ZSI6IDE4MTI1NzcyNzMuMjI1MzQzLAogICAgICAgICJob3N0
T25seSI6IGZhbHNlLAogICAgICAgICJodHRwT25seSI6IHRydWUsCiAgICAgICAgIm5hbWUiOiAi
cHNfbiIsCiAgICAgICAgInBhdGgiOiAiLyIsCiAgICAgICAgInNhbWVTaXRlIjogIm5vX3Jlc3Ry
aWN0aW9uIiwKICAgICAgICAic2VjdXJlIjogdHJ1ZSwKICAgICAgICAic2Vzc2lvbiI6IGZhbHNl
LAogICAgICAgICJzdG9yZUlkIjogbnVsbCwKICAgICAgICAidmFsdWUiOiAiMSIKICAgIH0sCiAg
ICB7CiAgICAgICAgImRvbWFpbiI6ICIuZmFjZWJvb2suY29tIiwKICAgICAgICAiZXhwaXJhdGlv
bkRhdGUiOiAxODI2NTM2MTk4LjAxMjYwNSwKICAgICAgICAiaG9zdE9ubHkiOiBmYWxzZSwKICAg
ICAgICAiaHR0cE9ubHkiOiB0cnVlLAogICAgICAgICJuYW1lIjogInNiIiwKICAgICAgICAicGF0
aCI6ICIvIiwKICAgICAgICAic2FtZVNpdGUiOiAibm9fcmVzdHJpY3Rpb24iLAogICAgICAgICJz
ZWN1cmUiOiB0cnVlLAogICAgICAgICJzZXNzaW9uIjogZmFsc2UsCiAgICAgICAgInN0b3JlSWQi
OiBudWxsLAogICAgICAgICJ2YWx1ZSI6ICJxbVA2YVFkb1UzaE03OWUwZWZQXzE0bEEiCiAgICB9
LAogICAgewogICAgICAgICJkb21haW4iOiAiLmZhY2Vib29rLmNvbSIsCiAgICAgICAgImV4cGly
YXRpb25EYXRlIjogMTc5MjU4MTAyMiwKICAgICAgICAiaG9zdE9ubHkiOiBmYWxzZSwKICAgICAg
ICAiaHR0cE9ubHkiOiBmYWxzZSwKICAgICAgICAibmFtZSI6ICJ3ZCIsCiAgICAgICAgInBhdGgi
OiAiLyIsCiAgICAgICAgInNhbWVTaXRlIjogImxheCIsCiAgICAgICAgInNlY3VyZSI6IHRydWUs
CiAgICAgICAgInNlc3Npb24iOiBmYWxzZSwKICAgICAgICAic3RvcmVJZCI6IG51bGwsCiAgICAg
ICAgInZhbHVlIjogIjYxMTJ4Mjk2MCIKICAgIH0KXQo=
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
