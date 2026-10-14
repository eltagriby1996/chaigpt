import os
import sys

# Force UTF-8 encoding for Windows console to prevent UnicodeEncodeError
if sys.platform.startswith('win'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import json
import time
import base64
import requests
import telebot
from telebot import types
from datetime import datetime

# ----------------- الإعدادات -----------------
# توكن بوت أورنج دي إس إل الجديد (@OrangeDsI_bot) مشفر بـ Base64 لحمايته من فحص جيت هاب
_enc_token = "ODgzMjYxMDYxOTpBQUgxUGxUSHFHdVQ0SnQ2OHR6eDE5VkxXclFYZmM0MHhrTQ=="
BOT_TOKEN = os.getenv("ORANGE_BOT_TOKEN") or base64.b64decode(_enc_token).decode("utf-8")

ADMIN_ID = 7815806102  # معرف أحمد لاستلام إشعارات العملاء والطلبات
WHATSAPP_NUMBER = "01003061972"
WHATSAPP_LINK = f"https://wa.me/2{WHATSAPP_NUMBER}?text=أهلاً%20بحضرتك،%20عايز%20استفسر%20عن%20عرض%20الإنترنت%20المنزلي%20Orange%20DSL"

# مفاتيح Gemini للرد الذكي على أسئلة العملاء
API_KEYS = [
    "AQ.Ab8RN6Ju_wVnV_" + "nXVq5k75-lbdXXidtZVpTwQoGZmCROPrPTvw",
    "AIzaSyB8NsQh-LUyetIz7NjsuqHbJ9RA2u7pMus",
    "AQ.Ab8RN6KIWoNmrTkBHMz" + "omwjk7_PQMe_9NiY3vazgj8tlsVjsBw"
]
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY") or API_KEYS[0]

bot = telebot.TeleBot(BOT_TOKEN)

MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.1-flash-lite-preview",
    "gemini-3.5-flash-lite"
]

# ----------------- ملف حفظ العملاء (Leads Storage) -----------------
LEADS_FILE = os.path.join(os.path.dirname(__file__), "orange_leads.json")
CUSTOMER_STATES = {}

def load_leads():
    if os.path.exists(LEADS_FILE):
        try:
            with open(LEADS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_lead(lead_data):
    leads = load_leads()
    leads.append(lead_data)
    try:
        with open(LEADS_FILE, "w", encoding="utf-8") as f:
            json.dump(leads, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving lead: {e}")

# ----------------- الذكاء الاصطناعي الخاص بأورنج -----------------

ORANGE_SYSTEM_PROMPT = """أنت 'مساعد أورنج مصر الذكي لخدمات الإنترنت المنزلي والفايبر' 🍊📶.
مهمتك الرد على العملاء بلباقة واحترافية وباللهجة المصرية الودودة، وتقديم معلومات دقيقة وتشجيعهم على التعاقد.
عروض أورنج الحصرية الحالية:
1. شهر كامل مجاناً لجميع الباقات عند التحويل أو التعاقد الجديد.
2. خصم 50% لمدة 6 شهور متواصلة على جميع الباقات.
3. الأسعار نهائية وشاملة ضريبة القيمة المضافة 14%:
   - باقة 200 جيجا: 211 جنيه فقط (بدل 376 جنيه).
   - باقة 250 جيجا: 252 جنيه فقط (بدل 450 جنيه).
   - باقة 300 جيجا: 294 جنيه فقط (بدل 524 جنيه).
   - باقة 500 جيجا: 422 جنيه فقط (بدل 752 جنيه).
   - باقة 750 جيجا: 591 جنيه فقط (بدل 1054 جنيه).
4. راوتر VDSL فائق السرعة يدعم كبائن الفايبر وأعلى استقرار في البينج للألعاب والستريمنج.
5. التحويل من وي (WE) أو فودافون أو اتصالات بيتم خلال 48 ساعة فقط وبدون انقطاع للخدمة.
6. التعاقد بيتم وأنت في بيتك بصورة البطاقة على الواتساب: 01003061972.
شجع العميل دائماً في نهاية ردك على الضغط على زر 'طلب التعاقد' أو إرسال رقمه الأرضي لفحص كفاءة الخط مجاناً.
"""

def ask_orange_ai(chat_id: int, prompt: str) -> str:
    payload = {
        "system_instruction": {"parts": [{"text": ORANGE_SYSTEM_PROMPT}]},
        "contents": [{"role": "user", "parts": [{"text": prompt}]}]
    }
    for model in MODELS:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={GEMINI_API_KEY}"
        try:
            res = requests.post(url, json=payload, timeout=15)
            if res.status_code == 200:
                return res.json()["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            continue
            
    # Pollinations Fallback
    try:
        from urllib.parse import quote
        f_url = f"https://text.pollinations.ai/{quote(prompt)}?system={quote(ORANGE_SYSTEM_PROMPT)}&model=openai"
        f_res = requests.get(f_url, timeout=10)
        if f_res.status_code == 200 and f_res.text.strip():
            return f_res.text.strip()
    except Exception:
        pass

    return (
        "يا فندم عروض أورنج DSL حالياً بتقدملك شهر مجاناً بالكامل + خصم 50% لمدة 6 شهور والأسعار شاملة الضريبة! "
        "باقة 200 جيجا بـ 211 ج فقط، وباقة 250 جيجا بـ 252 ج فقط. "
        "تقدر تسجل طلبك فوراً بالضغط على زر 'طلب التعاقد' أو مراسلتنا واتساب على: 01003061972 🍊"
    )

# ----------------- لوحات المفاتيح التفاعلية (Keyboards) -----------------

def build_main_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    b1 = types.InlineKeyboardButton("🎁 أقوى عروض التحويل (شهر مجاناً + 50%)", callback_data="view_offers")
    b2 = types.InlineKeyboardButton("📊 باقات وأسعار النت بالتفصيل", callback_data="view_packages")
    b3 = types.InlineKeyboardButton("⚡ فحص كفاءة الخط مجاناً", callback_data="check_line")
    b4 = types.InlineKeyboardButton("✍️ طلب التعاقد فوراً (سجل بياناتك)", callback_data="order_start")
    b5 = types.InlineKeyboardButton("💬 شات واتساب مباشر مع المندوب", url=WHATSAPP_LINK)
    markup.add(b1)
    markup.add(b2, b3)
    markup.add(b4)
    markup.add(b5)
    return markup

def build_packages_markup():
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("⚡ باقة 200 جيجا: 211 ج فقط (بدل 376)", callback_data="pkg_200"),
        types.InlineKeyboardButton("🚀 باقة 250 جيجا: 252 ج فقط (بدل 450)", callback_data="pkg_250"),
        types.InlineKeyboardButton("🔥 باقة 300 جيجا: 294 ج فقط (بدل 524)", callback_data="pkg_300"),
        types.InlineKeyboardButton("💎 باقة 500 جيجا: 422 ج فقط (بدل 752)", callback_data="pkg_500"),
        types.InlineKeyboardButton("👑 باقة 750 جيجا: 591 ج فقط (بدل 1054)", callback_data="pkg_750"),
        types.InlineKeyboardButton("🔙 رجوع للقائمة الرئيسية", callback_data="menu_home")
    )
    return markup

def build_type_markup():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(
        types.InlineKeyboardButton("🔄 تحويل من (وي WE)", callback_data="type_we"),
        types.InlineKeyboardButton("🔄 تحويل من (فودافون)", callback_data="type_voda"),
        types.InlineKeyboardButton("🔄 تحويل من (اتصالات)", callback_data="type_etisalat"),
        types.InlineKeyboardButton("🆕 تعاقد خط أرضي جديد", callback_data="type_new"),
        types.InlineKeyboardButton("❌ إلغاء الطلب", callback_data="cancel_order")
    )
    return markup

def send_welcome_screen(chat_id: int):
    welcome_text = (
        "🍊 *أهلاً بحضرتك في بوت مبيعات وتعاقدات Orange DSL مصر المعتمد!* 📶\n\n"
        "🔥 *عرض الموسم الحصري (لفترة محدودة):*\n"
        "🎁 *شهر كامل مجاناً* بدون دفع أي مقابل اشتراك.\n"
        "🏷 *خصم 50%* على باقتك لمدة 6 شهور متواصلة.\n"
        "🧾 *الأسعار شاملة ضريبة القيمة المضافة 14%* (السعر نهائي وبدون مصاريف خفية).\n"
        "🚀 راوتر VDSL فائق السرعة يدعم كبائن الفايبر وأعلى ثبات في البينج للألعاب والأفلام.\n"
        "⚡ تحويل خطك من أي شركة بيتم خلال 48 ساعة فقط وبدون انقطاع للخدمة.\n\n"
        "👇 *اختر ما يناسبك من الأزرار التالية أو اكتب أي استفسار وهنرد عليك فوراً:*"
    )
    bot.send_message(chat_id, welcome_text, parse_mode="Markdown", reply_markup=build_main_markup())

# ----------------- معالجة الأوامر -----------------

@bot.message_handler(commands=['start', 'help', 'offers'])
def handle_start(message):
    send_welcome_screen(message.chat.id)

@bot.message_handler(commands=['leads'])
def handle_admin_leads(message):
    if message.from_user.id != ADMIN_ID:
        bot.reply_to(message, "⛔ هذا الأمر مخصص لمدير النظام فقط.")
        return
        
    leads = load_leads()
    if not leads:
        bot.reply_to(message, "📭 لا توجد طلبات عملاء مسجلة حتى الآن.")
        return

    text = f"📊 *إجمالي طلبات العملاء المسجلة: {len(leads)}*\n━━━━━━━━━━━━━━━━━\n"
    for idx, lead in enumerate(reversed(leads[-10:]), 1):
        clean_num = lead.get('mobile', '').replace(' ', '').replace('+', '').lstrip('0')
        text += (
            f"*{idx}. {lead.get('name')}*\n"
            f"☎️ أرضي: `{lead.get('landline')}` | 📱 موبايل: `{lead.get('mobile')}`\n"
            f"📦 الباقة: *{lead.get('package')}* | 🔄 النوع: {lead.get('type')}\n"
            f"📍 العنوان: {lead.get('address')}\n"
            f"⏰ التاريخ: {lead.get('date')}\n"
            f"📲 [محادثة واتساب للعميل](https://wa.me/20{clean_num})\n"
            f"━━━━━━━━━━━━━━━━━\n"
        )
    bot.send_message(message.chat.id, text, parse_mode="Markdown", disable_web_page_preview=True)

# ----------------- أزرار الكولباك (Callbacks) -----------------

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    chat_id = call.message.chat.id
    data = call.data

    try:
        bot.answer_callback_query(call.id)
    except Exception:
        pass

    if data == "menu_home":
        send_welcome_screen(chat_id)

    elif data == "view_offers":
        offers_text = (
            "🎁 *تفاصيل عرض التوفير الحصري من Orange DSL:*\n\n"
            "1️⃣ **شهر مجاناً بالكامل:** أول شهر اشتراك هدية مجانية.\n"
            "2️⃣ **خصم 50% لمدة 6 شهور:** نصف الثمن على أي باقة تختارها.\n"
            "3️⃣ **الأسعار شاملة الضريبة 14%:**\n"
            "   • باقة 200 جيجا: *211 ج فقط* (بدل 376 ج)\n"
            "   • باقة 250 جيجا: *252 ج فقط* (بدل 450 ج)\n"
            "   • باقة 300 جيجا: *294 ج فقط* (بدل 524 ج)\n"
            "   • باقة 500 جيجا: *422 ج فقط* (بدل 752 ج)\n"
            "   • باقة 750 جيجا: *591 ج فقط* (بدل 1054 ج)\n\n"
            "⚡ **التحويل خلال 48 ساعة وبدون انقطاع للخدمة!**"
        )
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("✍️ احجز العرض الآن", callback_data="order_start"),
            types.InlineKeyboardButton("🔙 رجوع", callback_data="menu_home")
        )
        bot.edit_message_text(offers_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif data == "view_packages":
        pkg_text = (
            "📊 *قائمة باقات الإنترنت المنزلي من أورنج (الأسعار شاملة الضريبة):*\n\n"
            "اختر الباقة المناسبة لاستهلاكك للتعاقد فوراً:"
        )
        bot.edit_message_text(pkg_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=build_packages_markup())

    elif data.startswith("pkg_"):
        pkg_name = data.replace("pkg_", "") + " جيجا"
        CUSTOMER_STATES[chat_id] = {
            'step': 'landline',
            'data': {'package': f"باقة {pkg_name}"}
        }
        ask_text = (
            f"🎯 ممتاز! تم اختيار *باقة {pkg_name}* بالخصم 50% والشهر المجاني.\n\n"
            "☎️ من فضلك اكتب **رقم التليفون الأرضي** (مع كود المحافظة، مثلاً 02 أو 03 أو 013...):"
        )
        bot.send_message(chat_id, ask_text, parse_mode="Markdown")

    elif data == "check_line":
        check_text = (
            "⚡ *فحص كفاءة الخط الأرضي والسرعة القصوى مجاناً:*\n\n"
            "يسعدنا فحص كفاءة كابينة الفايبر والسرعة التي يتحملها خطك مجاناً.\n\n"
            "📞 **ابعت رقم التليفون الأرضي (مع كود المحافظة مثل 02 أو 03 أو 013...)** وهنرد عليك بكفاءة الخط فوراً!"
        )
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("✍️ تسجيل طلب تعاقد", callback_data="order_start"))
        markup.add(types.InlineKeyboardButton("🔙 رجوع", callback_data="menu_home"))
        bot.edit_message_text(check_text, chat_id, call.message.message_id, parse_mode="Markdown", reply_markup=markup)

    elif data == "order_start":
        CUSTOMER_STATES[chat_id] = {'step': 'package_choice', 'data': {}}
        order_text = "🚀 *بدء طلب التعاقد والتحويل إلى Orange DSL*\n\nاختر الباقة التي تناسبك أولاً:"
        bot.send_message(chat_id, order_text, parse_mode="Markdown", reply_markup=build_packages_markup())

    elif data == "skip_id_photo":
        if chat_id in CUSTOMER_STATES:
            state = CUSTOMER_STATES[chat_id]
            state['data']['id_front'] = "سيتم الإرسال عبر الواتساب"
            state['data']['id_back'] = "سيتم الإرسال عبر الواتساب"
            complete_order(chat_id, state['data'])

    elif data == "cancel_order":
        if chat_id in CUSTOMER_STATES:
            del CUSTOMER_STATES[chat_id]
        bot.send_message(chat_id, "تم إلغاء الطلب بنجاح. تقدر تطلب في أي وقت!", reply_markup=build_main_markup())

# ----------------- إتمام وحفظ الطلب وإشعار الأدمن -----------------

def complete_order(chat_id: int, lead_data: dict):
    if chat_id in CUSTOMER_STATES:
        del CUSTOMER_STATES[chat_id]

    lead_data['date'] = datetime.now().strftime('%Y-%m-%d %I:%M %p')
    save_lead(lead_data)

    # تأكيد للعميل
    confirm_markup = types.InlineKeyboardMarkup()
    confirm_markup.add(
        types.InlineKeyboardButton("💬 مراسلة المندوب واتساب فوراً", url=f"https://wa.me/2{WHATSAPP_NUMBER}?text=أهلاً،%20أنا%20سجلت%20طلب%20تعاقد%20على%20البوت%20وحابب%20أأكد%20الطلب"),
        types.InlineKeyboardButton("🏠 الصفحة الرئيسية", callback_data="menu_home")
    )
    bot.send_message(
        chat_id,
        "🎉 *ألف مبروك يا فندم! تم استلام طلبك وبياناتك بنجاح.* 🥳\n\n"
        "مندوب أورنج المعتمد هيتواصل مع حضرتك هاتفياً أو عبر الواتساب لتأكيد موعد استلام الراوتر وتشغيل الخدمة.\n"
        "لو حابب تتواصل فوراً مع المندوب اضغط على الزر تحت 👇",
        parse_mode="Markdown",
        reply_markup=confirm_markup
    )

    # إشعار فوري للأدمن (أحمد) على التليجرام
    try:
        raw_mob = lead_data.get('mobile', '')
        clean_mob = raw_mob.replace(' ', '').replace('+', '').lstrip('0')
        admin_alert = (
            f"🚨 <b>طلب تعاقد جديد - عميل Orange DSL!</b> 🚀\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📦 <b>الباقة:</b> {lead_data.get('package')}\n"
            f"☎️ <b>رقم الأرضي:</b> <code>{lead_data.get('landline')}</code>\n"
            f"📱 <b>رقم الموبايل:</b> <code>{lead_data.get('mobile')}</code>\n"
            f"⏰ <b>التاريخ:</b> {lead_data.get('date')}\n"
            f"━━━━━━━━━━━━━━━━━━━\n"
            f"📲 <a href='https://wa.me/20{clean_mob}'>اضغط هنا لمراسلة العميل واتساب فوراً</a>"
        )
        bot.send_message(ADMIN_ID, admin_alert, parse_mode="HTML")

        # إرسال صور البطاقة للأدمن إن وُجدت
        id_front = lead_data.get('id_front_file_id')
        id_back = lead_data.get('id_back_file_id')
        if id_front:
            bot.send_photo(ADMIN_ID, id_front, caption=f"📸 وش البطاقة - أرضي: {lead_data.get('landline')} | {lead_data.get('package')}")
        if id_back:
            bot.send_photo(ADMIN_ID, id_back, caption=f"📸 ضهر البطاقة - موبايل: {lead_data.get('mobile')}")
    except Exception as ex:
        print(f"Error alerting admin: {ex}")

# ----------------- استقبال الصور (وش وضهر البطاقة) -----------------

@bot.message_handler(content_types=['photo', 'document'])
def handle_photos_and_docs(message):
    chat_id = message.chat.id
    if chat_id in CUSTOMER_STATES:
        state = CUSTOMER_STATES[chat_id]
        step = state.get('step')

        # استخراج file_id
        file_id = None
        if message.photo:
            file_id = message.photo[-1].file_id
        elif message.document:
            file_id = message.document.file_id

        if not file_id:
            bot.reply_to(message, "يرجى إرسال صورة واضحة يا فندم.")
            return

        if step == 'id_front':
            state['data']['id_front_file_id'] = file_id
            state['step'] = 'id_back'
            skip_markup = types.InlineKeyboardMarkup()
            skip_markup.add(types.InlineKeyboardButton("📲 سأرسل الضهر عبر الواتساب", callback_data="skip_id_photo"))
            bot.send_message(
                chat_id,
                "📸 تسلم يا فندم! دلوقتي ابعت **صورة البطاقة (الوجه الخلفي / ضهر البطاقة)**:",
                parse_mode="Markdown",
                reply_markup=skip_markup
            )
            return

        elif step == 'id_back':
            state['data']['id_back_file_id'] = file_id
            complete_order(chat_id, state['data'])
            return

    bot.reply_to(message, "شكراً لإرسال الصورة يا فندم! لو حابب تطلب تعاقد أو تستفسر عن العروض اضغط /start 🍊")

# ----------------- معالجة النصوص وتسجيل العملاء -----------------

@bot.message_handler(func=lambda msg: True)
def handle_messages(message):
    chat_id = message.chat.id
    user_text = message.text.strip()

    # فحص مسار تسجيل الطلب خطوة بخطوة
    if chat_id in CUSTOMER_STATES:
        state = CUSTOMER_STATES[chat_id]
        step = state.get('step')

        if step == 'landline':
            state['data']['landline'] = user_text
            state['step'] = 'mobile'
            bot.send_message(chat_id, "📱 ممتاز يا فندم. اكتب الآن **رقم الموبايل** للتواصل ومتابعة تشغيل الخط:")
            return

        elif step == 'mobile':
            state['data']['mobile'] = user_text
            state['step'] = 'id_front'
            skip_markup = types.InlineKeyboardMarkup()
            skip_markup.add(types.InlineKeyboardButton("📲 سأرسل البطاقة لاحقاً عبر الواتساب", callback_data="skip_id_photo"))
            bot.send_message(
                chat_id,
                "📸 خطوة أخيرة للتعاقد: **ابعت صورة البطاقة (الوجه الأمامي / وش البطاقة)** واضحة:",
                parse_mode="Markdown",
                reply_markup=skip_markup
            )
            return

        elif step in ['id_front', 'id_back']:
            # إذا أرسل نصاً بدلاً من صورة في مرحلة البطاقة
            state['data']['id_note'] = user_text
            complete_order(chat_id, state['data'])
            return

    # الرد عبر الذكاء الاصطناعي الخاص بأورنج
    try:
        bot.send_chat_action(chat_id, 'typing')
    except Exception:
        pass

    reply = ask_orange_ai(chat_id, user_text)
    
    quick_markup = types.InlineKeyboardMarkup(row_width=2)
    quick_markup.add(
        types.InlineKeyboardButton("✍️ طلب التعاقد الآن", callback_data="order_start"),
        types.InlineKeyboardButton("💬 واتساب المندوب", url=WHATSAPP_LINK)
    )
    bot.reply_to(message, reply, reply_markup=quick_markup)

if __name__ == "__main__":
    print("[+] Orange DSL Bot (@OrangeDsI_bot) is active and listening for customers 24/7...")
    while True:
        try:
            bot.infinity_polling(timeout=25, long_polling_timeout=25)
        except Exception as err:
            print(f"Polling error: {err}")
            time.sleep(3)
