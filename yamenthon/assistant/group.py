import json
import asyncio
import threading
import time
import logging
from datetime import datetime

from aiogram import Bot, Dispatcher, Router, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command

from telethon import TelegramClient, functions
from telethon.sessions import StringSession
from ..Config import Config

# ===== logging =====
logging.basicConfig(level=logging.INFO)
LOGS = logging.getLogger(__name__)

# ===== bot & router (لا تشغّل polling هنا) =====
bot = Bot(token=Config.TG_BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()  # يمكن للمشروع الرئيسي استعمال هذا أو لا
router = Router()  # هذا الروتر يجب أن تُدرجه في المشروع الرئيسي

# ===== إعداد Telethon fallback (لا تغيّر منطقك) =====
API_ID = getattr(Config, "API_ID", 100000)
API_HASH = getattr(Config, "API_HASH", "placeholder")

SESSIONS_FILE = "sessions.json"
user_states = {}  # لحفظ حالة المستخدم (انتظر جلسة)


# ===== وظائف مساعدة =====
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except:
        return {}


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4)


def load_sessions():
    try:
        with open(SESSIONS_FILE, "r") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except:
        return []


def save_session(new_session, user_id):
    sessions = load_sessions()
    if not any(sess["session"] == new_session for sess in sessions):
        sessions.append({"session": new_session, "user_id": user_id})
        save_json(SESSIONS_FILE, sessions)


def main_menu():
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("‹ اضافة حساب ›", callback_data="add_account"),
        types.InlineKeyboardButton("‹ عرض الحسابات ›", callback_data="show_accounts")
    )
    markup.add(types.InlineKeyboardButton("‹ انشاء مجموعات ›", callback_data="create_groups"))
    markup.row(
        types.InlineKeyboardButton("‹ Source YamenThon ›", url="https://t.me/YamenThon"),
        types.InlineKeyboardButton("‹ Developer ›", url="https://t.me/T_A_Tl")
    )
    return markup


# ===== handler للـ /group (مسجل أدناه على Router) =====
async def send_welcome(message: types.Message):
    await message.answer("⌁︙ مرحباً بك في لوحة التحكم :", reply_markup=main_menu())


# ===== دالة استقبال الرسائل لحالة إدخال الجلسة =====
async def message_router(message: types.Message):
    # فقط نمسك الرسائل عندما المستخدم في حالة انتظار الجلسة
    if user_states.get(message.from_user.id) == "waiting_session":
        await process_session(message)
    # وإلا نتجاهل الرسائل (لا نغيّر منطقك)


# ===== معالجة الجلسة (كما كانت منطقيًا) =====
async def process_session(message: types.Message):
    session = message.text.strip()
    user_id = message.from_user.id
    user_states.pop(user_id, None)

    if len(session) < 20:
        await message.answer("⌁︙الجلسة لا تعمل تأكد انها نشطة او تكون تليثون .")
        return

    try:
        client = TelegramClient(StringSession(session), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            await message.answer("⌁︙الجلسة غير مفعّلة .")
            return

        # محاولة الانضمام للقنوات (كما في كودك)
        try:
            await client(functions.channels.JoinChannelRequest(channel="D8BB8"))
            await client(functions.channels.JoinChannelRequest(channel="rsrrsrr"))
        except Exception as e:
            LOGS.debug(f"join channels failed: {e}")

        user = await client.get_me()
        save_session(session, user_id)
        await client.disconnect()

        await message.answer(f"⌁︙تم تسجيل الدخول : {user.first_name or ''} @{user.username or 'لا يوجد'}")
    except Exception as e:
        await message.answer(f"خطأ: {str(e)}")


# ===== إنشاء 50 مجموعة (async) =====
async def async_create_50_groups(session_string, chat_id):
    try:
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            await bot.send_message(chat_id, "⌁︙الجلسة غير مفعّلة.")
            return

        today = datetime.now().strftime("%d-%m-%Y")
        description = "‹ By @zqqqzq - @GroupDrOxBoT ›"

        for i in range(50):
            title = f"{today} - {i+1}"
            result = await client(functions.channels.CreateChannelRequest(
                title=title,
                about=description,
                megagroup=True
            ))
            # حماية: تأكد من وجود chats
            group = None
            if hasattr(result, "chats") and result.chats:
                group = result.chats[0]

            if not group:
                await bot.send_message(chat_id, f"⌁︙فشل إنشاء المجموعة {i+1}")
                await asyncio.sleep(1)
                continue

            for _ in range(5):
                await client.send_message(group.id, description)
                await asyncio.sleep(0.4)  # فواصل صغيرة لتخفيف الضغط

            try:
                invite = await client(functions.messages.ExportChatInviteRequest(peer=group))
                link = getattr(invite, "link", None) or getattr(invite, "invite_link", None)
            except Exception:
                link = None

            if link:
                await bot.send_message(chat_id, f"⌁︙تم إنشاء المجموعة رقم {i+1} — {link}")
            else:
                await bot.send_message(chat_id, f"⌁︙تم إنشاء المجموعة رقم {i+1} — (لم يتم استخراج الرابط)")

            await asyncio.sleep(1)
        await client.disconnect()
    except Exception as e:
        await bot.send_message(chat_id, f"خطأ: {str(e)}")


# ===== callback router واحد يتعامل مع جميع callback_data (يبقي منطقك كما هو) =====
async def callback_router(call: types.CallbackQuery):
    data = (call.data or "")
    # add account
    if data == "add_account":
        user_states[call.from_user.id] = "waiting_session"
        await call.message.edit_text("⌁︙ ارسل لي جلسة ( تليثون ) الحساب :")
        return

    # create groups
    if data == "create_groups":
        sessions = load_sessions()
        user_sessions = [s for s in sessions if s.get("user_id") == call.from_user.id]
        if not user_sessions:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("‹ رجوع ›", callback_data="back"))
            await call.message.edit_text("⌁︙لا توجد جلسات .", reply_markup=markup)
            return

        await call.message.edit_text("⌁︙جاري إنشاء 50 مجموعة ...")
        for session in user_sessions:
            await async_create_50_groups(session["session"], call.message.chat.id)
        return

    # show accounts
    if data == "show_accounts":
        sessions = load_sessions()
        user_sessions = [s for s in sessions if s.get("user_id") == call.from_user.id]
        if not user_sessions:
            markup = types.InlineKeyboardMarkup().add(types.InlineKeyboardButton("‹ رجوع ›", callback_data="back"))
            await call.message.edit_text("⌁︙لا توجد جلسات .", reply_markup=markup)
            return

        markup = types.InlineKeyboardMarkup()
        for i, session in enumerate(user_sessions):
            markup.row(
                types.InlineKeyboardButton(f"حساب {i+1}", callback_data=f"acc_{i+1}"),
                types.InlineKeyboardButton("🗑", callback_data=f"delete_acc_{i}")
            )
        markup.add(types.InlineKeyboardButton("‹ رجوع ›", callback_data="back"))
        await call.message.edit_text("⌁︙الحسابات:", reply_markup=markup)
        return

    # delete account
    if data.startswith("delete_acc_"):
        index = int(data.split("_")[-1])
        sessions = load_sessions()
        user_sessions = [s for s in sessions if s.get("user_id") == call.from_user.id]
        if index < len(user_sessions):
            session_to_delete = user_sessions[index]
            sessions.remove(session_to_delete)
            save_json(SESSIONS_FILE, sessions)
            await call.answer("⌁︙تم حذف الجلسة بنجاح")
        else:
            await call.answer("⌁︙فشل في العثور على الجلسة", show_alert=True)
        # أعد عرض الحسابات
        await callback_router(types.CallbackQuery(**{"data": "show_accounts", "message": call.message, "from_user": call.from_user}))
        return

    # back
    if data == "back":
        await call.message.edit_text("⌁︙ مرحباً بك في لوحة التحكم :", reply_markup=main_menu())
        return

    # بقية data يمكنك توسيعها هنا...


# ===== التسجيل في الروتر =====
router.message.register(send_welcome, Command(commands=["group"]))
router.message.register(message_router)  # يعالج حالة الجلسة
router.callback_query.register(callback_router)


# ===== مهمة دورية كما كانت عندك (تعمل في Thread منفصل) =====
def create_all_groups_periodically():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        print("⌁︙بدء مهمة إنشاء المجموعات التلقائية.")
        sessions = load_sessions()
        for i, sess in enumerate(sessions, start=1):
            try:
                loop.run_until_complete(async_create_50_groups(sess["session"], Config.OWNER_ID))
            except Exception as e:
                print(f"⌁︙خطأ في الجلسة رقم {i}: {e}")
        print("⌁︙تم إنشاء جميع المجموعات، الانتظار 12 ساعة...")
        time.sleep(43200)


threading.Thread(target=create_all_groups_periodically, daemon=True).start()


# محاولة آمنة لضم الروتر إلى الـ Dispatcher الرئيسي إن وُجد داخل حزمتك (yamenthon)
try:
    import yamenthon  # أو استبدل بالاسم الصحيح إذا مختلف
    main_dp = getattr(yamenthon, "dp", None) or getattr(yamenthon, "dispatcher", None) or getattr(yamenthon, "bot_dispatcher", None)
    if main_dp:
        main_dp.include_router(router)
        LOGS.info("✔️ تم تضمين group.router في Dispatcher الرئيسي تلقائياً")
    else:
        LOGS.debug("ℹ️ لم يتم العثور على Dispatcher رئيسي باسم متوقع داخل yamenthon")
except Exception as e:
    LOGS.debug("❌ محاولة auto-include فشلت: %s", e)
