import json
import os
from datetime import datetime
from telethon import events
from telethon.tl.types import ChatAdminRights, Channel, ChannelAdminLogEventsFilter
from telethon.tl.functions.channels import EditAdminRequest, GetAdminLogRequest

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
remove_admins_aljoker = {}  # تخزين آخر وقت طرد لكل مشرف

# ===================== دالة بديلة لجلب آخر من قام بالطرد =====================
async def get_last_kick_actor(client, chat):
    try:
        log = await client(GetAdminLogRequest(
            channel=chat,
            q="",
            max_id=0,
            min_id=0,
            limit=5,
            events_filter=ChannelAdminLogEventsFilter(kick=True)
        ))
        if log.events:
            return log.events[0].user_id
    except Exception:
        pass
    return None

# ===================== مراقبة الطرد =====================
@zedub.on(events.ChatAction)
async def monitor_kicks(event):
    db = load_db()
    chat_id = str(event.chat_id)

    if chat_id not in db or not db[chat_id]:
        return

    chat = await event.get_chat()
    if not chat:
        return

    try:
        if event.user_kicked:  # فقط لو في عملية طرد
            user_id = getattr(event.action_message.from_id, "user_id", None)

            # محاولة بديلة لجلب الفاعل من سجل الإدارة في حال from_id غير متوفر
            if not user_id:
                user_id = await get_last_kick_actor(event.client, chat)
                if not user_id:
                    return  # لم يتم العثور على من قام بالطرد

            now = datetime.now()

            # تحقق من معدل الطرد
            if user_id in remove_admins_aljoker:
                if (now - remove_admins_aljoker[user_id]).seconds < 60:
                    try:
                        admin_info = await event.client.get_entity(user_id)
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
                        await event.client(EditAdminRequest(
                            channel=chat,
                            user_id=user_id,
                            admin_rights=rights,
                            rank=""
                        ))

                        # رسالة تنبيه
                        msg = (
                            "🚨 **تم عزل مشرف بسبب التفليش** 🚨\n\n"
                            f"👤 المشرف: {yamen_link}\n"
                            f"🆔 ايدي: `{admin_info.id}`\n"
                            f"📌 المجموعة/القناة: {getattr(chat, 'title', 'غير معروف')}\n"
                            f"⏰ الوقت: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"✅ النتيجة: تم سحب صلاحياته بنجاح"
                        )

                        # إرسال الإشعار
                        if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
                            await event.client.send_message(BOTLOG_CHATID, msg)
                        else:
                            await event.reply(msg)

                    except Exception as e:
                        await event.reply(f"⚠️ حدث خطأ أثناء محاولة تنزيل المشرف:\n`{str(e)}`")

                # تحديث الوقت
                remove_admins_aljoker[user_id] = now
            else:
                remove_admins_aljoker[user_id] = now

    except Exception:
        return


# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="قفل التفليش", require_admin=True)
async def enable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    db = load_db()
    chat_id = str(event.chat_id)

    if db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش مفعلة مسبقًا في هذه المجموعة")

    db[chat_id] = True
    save_db(db)
    await event.edit("✅︙ تم تفعيل حماية منع التفليش بنجاح\n⚠️︙ تعمل فقط في السوبرجروبات التي يمتلك فيها البوت صلاحيات مشرف ورؤية سجل الإدارة")


@zedub.zed_cmd(pattern="فتح التفليش", require_admin=True)
async def disable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    db = load_db()
    chat_id = str(event.chat_id)

    if not db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش معطلة مسبقًا في هذه المجموعة")

    db.pop(chat_id, None)
    save_db(db)
    await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة")
