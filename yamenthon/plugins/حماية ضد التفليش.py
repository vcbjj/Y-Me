import json
import os
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
last_kick_time = {}  # تخزين آخر وقت طرد لكل مشرف

# ===================== مراقبة الطرد في المجموعات =====================
@zedub.on(events.ChatAction)
async def monitor_group_kicks(event):
    db = load_db()
    chat_id = str(event.chat_id)

    if chat_id not in db or not db[chat_id]:
        return

    if not event.user_kicked:
        return

    kicker = getattr(event.action_message.from_id, "user_id", None)
    if not kicker:
        return

    now = datetime.now()

    if kicker in last_kick_time and (now - last_kick_time[kicker]).seconds < 60:
        await punish_admin(event.client, event.chat, kicker, now)

    last_kick_time[kicker] = now

# ===================== مراقبة الطرد في القنوات =====================
@zedub.on(events.NewMessage)
async def monitor_channel_kicks(event):
    db = load_db()
    chat_id = str(event.chat_id)

    if chat_id not in db or not db[chat_id]:
        return

    chat = await event.get_chat()
    if not isinstance(chat, Channel) or not chat.megagroup:
        # قناة (broadcast) أو غير مجموعة
        try:
            result = await event.client(GetAdminLogRequest(
                channel=chat,
                limit=5,
                events_filter=ChannelAdminLogEventsFilter(kick=True),
                admins=[]
            ))

            now = datetime.now()
            for e in result.events:
                if e.user_id:
                    if e.user_id in last_kick_time and (now - last_kick_time[e.user_id]).seconds < 60:
                        await punish_admin(event.client, chat, e.user_id, now)
                    last_kick_time[e.user_id] = now
        except:
            return

# ===================== دالة عزل المشرف =====================
async def punish_admin(client, chat, user_id, now):
    try:
        admin_info = await client.get_entity(user_id)
        yamen_link = f"[{admin_info.first_name}](tg://user?id={admin_info.id})"

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

        await client(EditAdminRequest(
            channel=chat,
            user_id=user_id,
            admin_rights=rights,
            rank=""
        ))

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
        else:
            await client.send_message(chat.id, msg)

    except Exception as e:
        await client.send_message(chat.id, f"⚠️ خطأ أثناء عزل المشرف:\n`{str(e)}`")

# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    db = load_db()
    chat_id = str(event.chat_id)

    if db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش مفعلة مسبقًا")

    db[chat_id] = True
    save_db(db)
    await event.edit("✅︙ تم تفعيل حماية منع التفليش")


@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def disable_antiflash(event):
    db = load_db()
    chat_id = str(event.chat_id)

    if not db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش معطلة مسبقًا")

    db.pop(chat_id, None)
    save_db(db)
    await event.edit("🛑︙ تم تعطيل حماية منع التفليش")
