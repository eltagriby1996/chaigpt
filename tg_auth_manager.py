import os
import sys
import json
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

WORKSPACE_DIR = os.path.dirname(os.path.abspath(__file__))
SESSION_FILE = os.path.join(WORKSPACE_DIR, "userbot")
AUTH_STATE_FILE = os.path.join(WORKSPACE_DIR, "tg_auth_state.json")

DEFAULT_API_ID = 2040
DEFAULT_API_HASH = "b18441a1ff607e10a989891a5462e627"

async def request_code(phone: str):
    if not phone.startswith("+"):
        if phone.startswith("01"):
            phone = "+2" + phone
        elif phone.startswith("201"):
            phone = "+" + phone
        else:
            phone = "+" + phone

    client = TelegramClient(SESSION_FILE, DEFAULT_API_ID, DEFAULT_API_HASH)
    await client.connect()

    if await client.is_user_authorized():
        me = await client.get_me()
        print(f"[ALREADY_AUTHORIZED] Already logged in as {me.first_name} (@{me.username or me.phone})")
        await client.disconnect()
        return

    print(f"[*] Sending code request to {phone} ...")
    sent = await client.send_code_request(phone)
    print(f"[+] Code successfully requested!")
    print(f"[+] Phone Code Hash: {sent.phone_code_hash}")
    
    with open(AUTH_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump({
            "phone": phone,
            "phone_code_hash": sent.phone_code_hash,
            "api_id": DEFAULT_API_ID,
            "api_hash": DEFAULT_API_HASH
        }, f, indent=2)
        
    print(f"[WAITING_FOR_OTP] Please check your Telegram app on {phone} and provide the code.")
    await client.disconnect()

async def submit_code(code: str, password: str = None):
    if not os.path.exists(AUTH_STATE_FILE):
        print("[ERROR] No pending auth state found. Run --request first.")
        return

    with open(AUTH_STATE_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    phone = data["phone"]
    phone_code_hash = data["phone_code_hash"]
    api_id = data.get("api_id", DEFAULT_API_ID)
    api_hash = data.get("api_hash", DEFAULT_API_HASH)

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.connect()

    try:
        await client.sign_in(phone=phone, code=str(code).strip(), phone_code_hash=phone_code_hash)
        me = await client.get_me()
        print(f"[SUCCESS] Successfully authorized as {me.first_name} (@{me.username or me.phone})!")
        if os.path.exists(AUTH_STATE_FILE):
            os.remove(AUTH_STATE_FILE)
    except SessionPasswordNeededError:
        if password:
            await client.sign_in(password=password)
            me = await client.get_me()
            print(f"[SUCCESS] Successfully authorized with 2FA as {me.first_name} (@{me.username or me.phone})!")
            if os.path.exists(AUTH_STATE_FILE):
                os.remove(AUTH_STATE_FILE)
        else:
            print("[2FA_REQUIRED] Account has Two-Step Verification enabled. Password needed.")
    except Exception as e:
        print(f"[ERROR] Sign in failed: {e}")
    finally:
        await client.disconnect()

async def submit_password(password: str):
    api_id = DEFAULT_API_ID
    api_hash = DEFAULT_API_HASH
    phone = None
    phone_code_hash = None

    if os.path.exists(AUTH_STATE_FILE):
        with open(AUTH_STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        api_id = data.get("api_id", DEFAULT_API_ID)
        api_hash = data.get("api_hash", DEFAULT_API_HASH)
        phone = data.get("phone")
        phone_code_hash = data.get("phone_code_hash")

    client = TelegramClient(SESSION_FILE, api_id, api_hash)
    await client.connect()

    try:
        await client.sign_in(password=password)
        me = await client.get_me()
        print(f"[SUCCESS] Successfully authorized with 2FA as {me.first_name} (@{me.username or me.phone})!")
        if os.path.exists(AUTH_STATE_FILE):
            os.remove(AUTH_STATE_FILE)
    except Exception as e1:
        print(f"[*] Direct password sign-in notice: {e1}. Trying with cached state...")
        if phone and phone_code_hash:
            try:
                await client.sign_in(phone=phone, password=password)
                me = await client.get_me()
                print(f"[SUCCESS] Successfully authorized as {me.first_name} (@{me.username or me.phone})!")
                if os.path.exists(AUTH_STATE_FILE):
                    os.remove(AUTH_STATE_FILE)
            except Exception as e2:
                print(f"[ERROR] Password submission failed: {e2}")
        else:
            print(f"[ERROR] Password submission failed: {e1}")
    finally:
        await client.disconnect()

async def check_status():
    client = TelegramClient(SESSION_FILE, DEFAULT_API_ID, DEFAULT_API_HASH)
    await client.connect()
    is_auth = await client.is_user_authorized()
    if is_auth:
        me = await client.get_me()
        print(f"[AUTHORIZED] Logged in as: {me.first_name} {me.last_name or ''} (@{me.username or me.phone})")
    else:
        print("[NOT_AUTHORIZED] Session is not logged in.")
    await client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python tg_auth_manager.py --request <phone>")
        print("  python tg_auth_manager.py --submit <code> [password]")
        print("  python tg_auth_manager.py --password <password>")
        print("  python tg_auth_manager.py --status")
        sys.exit(1)

    cmd = sys.argv[1]
    if cmd == "--request":
        phone = sys.argv[2] if len(sys.argv) > 2 else "+201003061972"
        asyncio.run(request_code(phone))
    elif cmd == "--submit":
        code = sys.argv[2]
        pwd = sys.argv[3] if len(sys.argv) > 3 else None
        asyncio.run(submit_code(code, pwd))
    elif cmd == "--password":
        pwd = sys.argv[2]
        asyncio.run(submit_password(pwd))
    elif cmd == "--status":
        asyncio.run(check_status())
    else:
        print(f"Unknown command: {cmd}")
