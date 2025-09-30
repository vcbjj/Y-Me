import json
import os
import asyncio
from datetime import datetime
from telethon import events
from telethon.tl.types import ChatAdminRights, Channel
from telethon.tl.functions.channels import EditAdminRequest, GetAdminLogRequest
from telethon.tl.types import ChannelAdminLogEventsFilter

from yamenthon import zedub
from . import BOTLOG_CHATID

# ===================== قاعدة البيانات =====================
DB_FILE = "anti_kick_db.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# ===================== المتغيرات =====================
remove_admins_aljoker = {}   # آخر وقت طرد لكل مشرف
last_checked = {}            # آخر فحص للقناة


# ===================== مراقبة الطرد في المجموعات =====================
@zedub.on(events.ChatAction)
async def monitor_kicks_group(event):
    db = load_db()
    chat_id = str(event.chat_id)

    if chat_id not in db or not db[chat_id]:
        return

    chat = await event.get_chat()
    if not chat or isinstance(chat, Channel):
        return  # هذا الكود خاص بالمجموعات فقط

    try:
        if event.user_kicked:
            user_id = getattr(event.action_message.from_id, "user_id", None)
            if not user_id:
                return

            await handle_kick(event.client, chat, user_id, event)
    except Exception:
        return


# ===================== مراقبة الطرد في القنوات (تلقائي) =====================
async def monitor_channels():
    await zedub.start()  # تأكد من تشغيل العميل
    while True:
        try:
            db = load_db()
            for chat_id, enabled in db.items():
                if not enabled:
                    continue

                try:
                    chat = await zedub.get_entity(int(chat_id))
                    if not isinstance(chat, Channel):
                        continue  # هذا الكود خاص بالقنوات

                    # منع التكرار (آخر فحص)
                    last_time = last_checked.get(chat_id, 0)

                    result = await zedub(GetAdminLogRequest(
                        channel=chat,
                        q='',
                        min_id=0,
                        max_id=0,
                        limit=10,
                        events_filter=ChannelAdminLogEventsFilter(kick=True),
                        admins=[]
                    ))

                    for log in result.events:
                        # وقت الحدث
                        log_time = log.date.timestamp()
                        if log_time <= last_time:
                            continue

                        user_id = log.user_id
                        if not user_id:
                            continue

                        # نفس المعالجة حق المجموعات
                        fake_event = type("obj", (), {"reply": zedub.send_message})  # بديل event
                        await handle_kick(zedub, chat, user_id, fake_event)

                    if result.events:
                        last_checked[chat_id] = max(e.date.timestamp() for e in result.events)

                except Exception:
                    continue

        except Exception:
            pass

        await asyncio.sleep(20)  # فحص كل 20 ثانية


zedub.loop.create_task(monitor_channels())


# ===================== دالة معالجة الطرد =====================
async def handle_kick(client, chat, user_id, event):
    now = datetime.now()

    if user_id in remove_admins_aljoker:
        if (now - remove_admins_aljoker[user_id]).seconds < 60:
            try:
                admin_info = await client.get_entity(user_id)
                yamen_link = f"[{admin_info.first_name}](tg://user?id={admin_info.id})"

                # صلاحيات فارغة لعزل المشرف
                rights = ChatAdminRights(
                    change_info=False,
                    post_messages=False,
                    edit_messages=False,
                    delete_messages=False,
                    ban_users=False,
                    invite_users=False,
                    pin_messages=False,
                    add_admins=False,
                    manage_call=False,
                    anonymous=False,
                )

                # تنفيذ عزل المشرف
                await client(
                    EditAdminRequest(
                        channel=chat,
                        user_id=user_id,
                        admin_rights=rights,
                        rank=""
                    )
                )

                # رسالة تنبيه
                msg = (
                    "🚨 **تم عزل مشرف بسبب التفليش** 🚨\n\n"
                    f"👤 المشرف: {yamen_link}\n"
                    f"🆔 ايدي: `{admin_info.id}`\n"
                    f"📌 المجموعة/القناة: {getattr(chat, 'title', 'غير معروف')}\n"
                    f"⏰ الوقت: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"✅ النتيجة: تم سحب صلاحياته بنجاح"
                )

                if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
                    await client.send_message(BOTLOG_CHATID, msg)

            except Exception as e:
                try:
                    await event.reply(f"⚠️ حدث خطأ أثناء محاولة تنزيل المشرف:\n`{str(e)}`")
                except:
                    pass

        remove_admins_aljoker[user_id] = now
    else:
        remove_admins_aljoker[user_id] = now


# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    db = load_db()
    chat_id = str(event.chat_id)

    if db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش مفعلة مسبقًا في هذه المجموعة/القناة")

    db[chat_id] = True
    save_db(db)
    await event.edit("✅︙ تم تفعيل حماية منع التفليش في هذه المجموعة/القناة")


@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def disable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    db = load_db()
    chat_id = str(event.chat_id)

    if not db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش معطلة مسبقًا في هذه المجموعة/القناة")

    db.pop(chat_id, None)
    save_db(db)
    await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة/القناة")
