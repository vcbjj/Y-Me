# assistant/group_plugin.py
import re
import json
import asyncio
import threading
import time
import logging
from datetime import datetime

from telethon import Button, events
from telethon import functions as tl_functions
from telethon.sessions import StringSession
from telethon import TelegramClient

from yamenthon import Config, zedub
from ..core.session import tgbot
from ..core.logger import logging as logger_core
from . import BOTLOG, BOTLOG_CHATID

LOGS = logger_core.getLogger("يمنثون.group_plugin")

# ===== تعريف my_mention (من حساب المالك) =====
async def get_owner_mention():
    try:
        me = await zedub.get_me()
        return f"[{me.first_name}](tg://user?id={me.id})"
    except Exception:
        return "المالك"

my_mention = None

async def init_my_mention():
    global my_mention
    my_mention = await get_owner_mention()

# نضمن انه يتنفذ اول ما البوت يشتغل
zedub.loop.create_task(init_my_mention())

# ===== من هنا تبدأ أوامر البوت =====


# ===== إعدادات وجلب مفاتيح =====
API_ID = Config.APP_ID
API_HASH = Config.API_HASH

SESSIONS_FILE = "sessions.json"  
user_states = {}  

# ===== دوال مساعدة لقراءة وكتابة الجلسات =====
def load_json(file):
    try:
        with open(file, "r") as f:
            return json.load(f)
    except Exception:
        return []

def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def load_sessions():
    data = load_json(SESSIONS_FILE)
    return data if isinstance(data, list) else []

def save_session(new_session, user_id):
    sessions = load_sessions()
    # تخزين بدون تكرار (إذا نفس السلسلة موجودة)
    if not any(sess.get("session") == new_session for sess in sessions):
        sessions.append({"session": new_session, "user_id": user_id})
        save_json(SESSIONS_FILE, sessions)

def remove_session_by_index_for_user(index, user_id):
    sessions = load_sessions()
    # نأخذ جلسات هذا المستخدم
    user_sessions = [s for s in sessions if s.get("user_id") == user_id]
    if index < 0 or index >= len(user_sessions):
        return False
    session_to_delete = user_sessions[index]
    sessions.remove(session_to_delete)
    save_json(SESSIONS_FILE, sessions)
    return True

# ===== تكوين لوحة التحكم (زرار telethon) =====
def main_menu_buttons():
    return [
        [
            Button.inline("🛃 اضافة حساب ", b"add_account"),
            Button.inline("🗳 عرض الحسابات ", b"show_accounts"),
        ],
        [Button.inline("♾️ انشاء مجموعات ", b"create_groups")],
        [
            Button.url("ᯓSource YamenThon ›", "https://t.me/YamenThon"),
            Button.url(" ᯓDeveloper ›", "https://t.me/T_A_Tl"),
        ],
    ]

# ===== /group -> عرض اللوحة (يتم استدعاؤه كبوت مساعد) =====
@tgbot.on(events.NewMessage(pattern=r"^/group(?:@.*)?$", func=lambda e: e.is_private))
async def send_welcome(event):
    try:
        await tgbot.send_message(
            event.chat_id,
            f"🫂**︙ مرحباً بك مالكي** {my_mention}\n\n🚸**︙ هاذه لوحـة التحكم الخاصة بك**\n📍**︙ تستطيع من خلالها إنشاء مجموعات بشكل تلقائي**\n🎛**︙ كما يمكنك أضافه عدة حسابات**\n🛃**︙ يتم إنشاء 25 مجموعة تلقائي لكل حساب**\n\n ⚠️**︙ ملاحظـه هامـه لا تنشى اكثر من 25 مجموعة للحساب في يوم واحد للحفاظ على الحساب**\n[ᯓ 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 ♥️](t.me/YamenThon)",link_preview =False,
            buttons=main_menu_buttons(),
        )
    except Exception as e:
        LOGS.error(f"send_welcome error: {e}")

# ===== استقبال نص الجلسة عندما المستخدم في حالة waiting_session =====
@tgbot.on(events.NewMessage(func=lambda e: e.is_private))
async def message_router(event):
    # فقط نتعامل عندما المستخدم في وضع انتظار الجلسة
    user_id = event.sender_id
    state = user_states.get(user_id)
    if state != "waiting_session":
        return  # نتجاهل الرسائل الأخرى هنا (ملفات البوت الأخرى تتعامل معها)
    await process_session(event)

# ===== معالجة نص الجلسة المرسل من المستخدم =====
async def process_session(event):
    session = (event.raw_text or "").strip()
    user_id = event.sender_id
    # نظف الحالة
    user_states.pop(user_id, None)

    if not session or len(session) < 20:
        await event.reply("**عزيزي المالك 🫂**\n**🚸 هاذه الجلسة لا تعمل عليك استخراج كود تليثـون ثم اعد المحاوله** \n **شرح استخراج كود تليثـون** [⦇  اضـغـط هنــا  ⦈](https://t.me/YamenThon_Api/19)", link_preview = False)
        return

    try:
        client = TelegramClient(StringSession(session), API_ID, API_HASH)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                await client.disconnect()
                await event.reply("⌁︙الجلسة غير مفعّلة.")
                return
        except Exception:
            # في بعض الاحيان client.is_user_authorized() يرمى استثناءات على الشبكة
            await client.disconnect()
            await event.reply("**عزيزي المالك 🫂**\n**🚸 هاذه الجلسة لا تعمل عليك استخراج كود تليثـون ثم اعد المحاوله** \n **شرح استخراج كود تليثـون** [⦇  اضـغـط هنــا  ⦈](https://t.me/YamenThon_Api/19)",link_preview=False)
            return

        # محاولة الانضمام للقنوات (حماية زي الكود الأصلي)
        try:
            await client(tl_functions.channels.JoinChannelRequest(channel="YamenThon"))
            await client(tl_functions.channels.JoinChannelRequest(channel="YamenThon_Gorop"))
        except Exception as e:
            LOGS.debug(f"join channels failed: {e}")

        user = await client.get_me()
        save_session(session, user_id)
        await client.disconnect()

        await event.reply(f"🛃**تم تسجيل الدخول بنجـاح:** \n🚸** الحـساب **← {getattr(user, 'first_name', '')} \n**🔗 اليوزر** ← @{getattr(user, 'username', 'لا يوجد')}\n ♾️** الــحاله **← 🔄")
    except Exception as e:
        LOGS.error(f"process_session error: {e}")
        await event.reply(f"خطأ: {str(e)}")

# ===== إنشاء 25 مجموعة لكل جلسة =====
async def async_create_25_groups(session_string, chat_id):
    try:
        client = TelegramClient(StringSession(session_string), API_ID, API_HASH)
        await client.connect()
        try:
            if not await client.is_user_authorized():
                await client.disconnect()
                await tgbot.send_message(chat_id, "⌁︙الجلسة غير مفعّلة.")
                return
        except Exception:
            await client.disconnect()
            await tgbot.send_message(chat_id, "⌁︙فشل التحقق من الجلسة.")
            return

        today = datetime.now().strftime("%d-%m-%Y")
        description = "**يتم إرسال هاذه الرسائل تلقائي لتجنب فقدان المجموعـة**\n **سورس يـــمنثون 👑**"

        for i in range(25):
            title = f"{today} - {i+1}"
            try:
                result = await client(tl_functions.channels.CreateChannelRequest(
                    title=title,
                    about=description,
                    megagroup=True
                ))
            except Exception as e:
                LOGS.debug(f"create channel error {e}")
                await tgbot.send_message(chat_id, f"⌁︙فشل إنشاء المجموعة \n𓊈 **⚠️ 𝗘𝗥𝗥𝗢𝗥 ⚠️** 𓊉")
                await asyncio.sleep(1)
                continue

            group = None
            if hasattr(result, "chats") and result.chats:
                group = result.chats[0]

            if not group:
                await tgbot.send_message(chat_id, f"⌁︙فشل إنشاء المجموعة \n 𓊈 **⚠️ 𝗘𝗥𝗥𝗢𝗥 ⚠️** 𓊉")
                await asyncio.sleep(1)
                continue

            # إرسال وصف/رسائل داخل المجموعة للتثبيت كأول رسالة
            for _ in range(5):
                try:
                    await client.send_message(group.id, description)
                except Exception:
                    pass
                await asyncio.sleep(0.4)

            # محاولة استخراج رابط الدعوة
            try:
                invite = await client(tl_functions.messages.ExportChatInviteRequest(peer=group))
                link = getattr(invite, "link", None) or getattr(invite, "invite_link", None)
            except Exception:
                link = None

            if link:
                await tgbot.send_message(chat_id, f"⌁︙تم إنشاء المجموعة رقم {i+1} — {link}")
            else:
                await tgbot.send_message(chat_id, f"⌁︙تم إنشاء المجموعة رقم {i+1} — (لم يتم استخراج الرابط)")

            await asyncio.sleep(1)

        await client.disconnect()
    except Exception as e:
        LOGS.error(f"async_create_25_groups error: {e}")
        try:
            await tgbot.send_message(chat_id, f"خطأ: 𓊈 **⚠️ 𝗘𝗥𝗥𝗢𝗥 ⚠️** 𓊉")
        except Exception:
            pass

# ===== Callback router واحد للتعامل مع كل الأزرار =====
@tgbot.on(events.CallbackQuery)
async def callback_router(event):
    try:
        data_bytes = event.data or b""
        try:
            data = data_bytes.decode()
        except Exception:
            # في حال وجود بايت غير قابل للديكود نفشل بهدوء
            data = ""
        sender_id = event.sender_id

        # فقط نسمح للمالك أو للمرسل نفسه بالتفاعل مع أزرار لو لزم (هنا نسمح لأي مستخدم في الخاص)
        # add_account
        if data == "add_account":
            user_states[sender_id] = "waiting_session"
            await event.edit("📌**︙ ارسل لي جلسة ( تليثون ) الخاصه بالحساب الذي تريد إنشاء مجموعات في تلقائي**:", buttons=[Button.inline("ᯓ★ رجـــوع", b"back")])
            return

        # create_groups
        if data == "create_groups":
            sessions = load_sessions()
            user_sessions = [s for s in sessions if s.get("user_id") == sender_id]
            if not user_sessions:
                await event.edit("**🌐 عزيزي المالك**\n ** لا توجد جلسات بعد قم بإضافة جلسات اولاً**", buttons=[Button.inline("ᯓ★ رجـــوع", b"back")])
                return

            await event.edit(f"🛃** عزيزي المالك **{my_mention} \n\n**🎯يتم الان إنشـاء 25 مجموعة تلقائي ♾️**\n**🔄الحالــه  ← مــفعله 🟢**", buttons=[Button.inline("ᯓ★ رجـــوع", b"back")])
            # نفذ لكل جلسة للمستخدم
            for session in user_sessions:
                # ننفّذ بشكل غير متزامن (ننتظر الانتهاء لكل جلسة)
                await async_create_25_groups(session["session"], event.chat_id)
            # بعد الانتهاء نعرض رسالة انتهاء
            await event.client.send_message(
            BOTLOG_CHATID, "**إنشــاء المجموعــات التلقـائي ♽**\n\n**🛃 عـزيـزي المــالك**\n🚸**تـم الانتهــاء من إنشـاء المجموعات**\n**🌐تم إنشاء ← 25**\n**🗂الــحالــه ← معــطله 🔴**\n [ᯓ 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 ♥️](t.me/YamenThon)", link_preview =False)
            return

        # show_accounts
        if data == "show_accounts":
            sessions = load_sessions()
            user_sessions = [s for s in sessions if s.get("user_id") == sender_id]
            if not user_sessions:
                await event.edit("**🌐 عزيزي المالك**\n ** لا توجد جلسات بعد قم بإضافة جلسات اولاً**", buttons=[Button.inline("ᯓ★ رجـــوع", b"back")])
                return

            # نكوّن أزرار لحسابات المستخدم
            buttons = []
            row = []
            for i, session in enumerate(user_sessions):
                # زر لعرض الحساب وزر للحذف
                # callback data: acc_{i} و delete_acc_{i}
                row = [
                    Button.inline(f"حساب {i+1}", f"acc_{i}".encode()),
                    Button.inline("🗑 حذف", f"delete_acc_{i}".encode()),
                ]
                buttons.append(row)
            buttons.append([Button.inline("ᯓ★ رجـــوع", b"back")])
            await event.edit("**مــرحبــا مــالــكي 💛**\n\n**هــنا قــائمـة الحــسابات كــما يمكنك حــذف اي حسـاب تريـد**\n [ᯓ 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 ♥️](t.me/YamenThon)",link_preview =False, buttons=buttons)
            return

        # delete account (data like delete_acc_0)
        if data.startswith("delete_acc_"):
            try:
                index = int(data.split("_")[-1])
            except Exception:
                await event.answer("فشل في تحديد الجلسة", alert=True)
                return
            success = remove_session_by_index_for_user(index, sender_id)
            if success:
                await event.answer("⌁︙تم حذف الجلسة بنجاح", alert=False)
            else:
                await event.answer("⌁︙فشل في العثور على الجلسة", alert=True)
            # بعد الحذف نعيد عرض الحسابات
            # خاطف عرض الحسابات بنفس الطريقة
            sessions = load_sessions()
            user_sessions = [s for s in sessions if s.get("user_id") == sender_id]
            if not user_sessions:
                await event.edit("**🌐 عزيزي المالك**\n ** لا توجد جلسات بعد قم بإضافة جلسات اولاً**", buttons=[Button.inline("ᯓ★ رجـــوع", b"back")])
                return
            buttons = []
            for i, session in enumerate(user_sessions):
                buttons.append([
                    Button.inline(f"حساب {i+1}", f"acc_{i}".encode()),
                    Button.inline("🗑 حذف", f"delete_acc_{i}".encode()),
                ])
            buttons.append([Button.inline("ᯓ★ رجـــوع", b"back")])
            await event.edit("**مــرحبــا مــالــكي 💛**\n\n**هــنا قــائمـة الحــسابات كــما يمكنك حــذف اي حسـاب تريـد**\n [ᯓ 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 ♥️](t.me/YamenThon)",link_preview =False, buttons=buttons)
            return

        # back
        if data == "back":
            await event.edit(f"🫂**︙ مرحباً بك مالكي** {my_mention}\n\n🚸**︙ هاذه لوحـة التحكم الخاصة بك**\n📍**︙ تستطيع من خلالها إنشاء مجموعات بشكل تلقائي**\n🎛**︙ كما يمكنك أضافه عدة حسابات**\n🛃**︙ يتم إنشاء 25 مجموعة تلقائي لكل حساب**\n\n ⚠️**︙ ملاحظـه هامـه لا تنشى اكثر من 25 مجموعة للحساب في يوم واحد للحفاظ على الحساب**\n[ᯓ 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉 ♥️](t.me/YamenThon)",link_preview =False, buttons=main_menu_buttons())
            return

        # acc_{i} -> نعرض معلومات عن الحساب (يمكن تعديل لاحقاً لعمل actions)
        if data.startswith("acc_"):
            try:
                index = int(data.split("_")[-1])
            except Exception:
                await event.answer("فشل في تحديد الحساب", alert=True)
                return
            sessions = load_sessions()
            user_sessions = [s for s in sessions if s.get("user_id") == sender_id]
            if index < 0 or index >= len(user_sessions):
                await event.answer("فشل في العثور على الجلسة", alert=True)
                return
            # فقط نعرض تفاصيل مبسطة (طول الجلسة ووقت التسجيل)
            sess = user_sessions[index]
            info = f"⌁︙معلومات الحساب:\n• معرف المالك: `{sess.get('user_id')}`\n• طول الجلسة: {len(sess.get('session',''))} حرف\n"
            await event.edit(info, buttons=[Button.inline("ᯓ★ رجـــوع", b"show_accounts")])
            return

        # أي data آخر يمكن توسيعه لاحقاً...
    except Exception as e:
        LOGS.error(f"callback_router error: {e}")
        try:
            await event.answer("حدث خطأ.", alert=True)
        except Exception:
            pass

# ===== مهمة دورية لإنشاء المجموعات تلقائياً (خيط مستقل) =====
def create_all_groups_periodically():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        LOGS.info("⌁︙بدء مهمة إنشاء المجموعات التلقائية.")
        sessions = load_sessions()
        for i, sess in enumerate(sessions, start=1):
            try:
                loop.run_until_complete(async_create_25_groups(sess["session"], Config.OWNER_ID))
            except Exception as e:
                LOGS.error(f"⌁︙خطأ في الجلسة رقم {i}: {e}")
        LOGS.info("⌁︙تم إنشاء جميع المجموعات، الانتظار 12 ساعة...")
        time.sleep(43200)

# شغّل الخيط كخلفية (daemon)
threading.Thread(target=create_all_groups_periodically, daemon=True).start()

LOGS.info("✔️ تم تحميل ملحق group_plugin بنجاح (بوت مساعد).")
