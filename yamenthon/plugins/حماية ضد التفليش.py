import json
import os
from datetime import datetime
from pyrogram import Client
from pyrogram.enums import ChatMemberStatus, ChatType

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

# ===================== مراقبة الطرد =====================
@zedub.pyro.on_chat_member_updated()
async def monitor_kicks(client, event):
    db = load_db()
    chat_id = str(event.chat.id)

    if chat_id not in db or not db[chat_id]:
        return

    chat = event.chat
    user = event.new_chat_member.user
    status = event.new_chat_member.status
    kicker = event.new_chat_member.restricted_by

    if chat.type not in [ChatType.SUPERGROUP, ChatType.CHANNEL]:
        return

    # لو فيه عملية طرد
    if status == ChatMemberStatus.BANNED and kicker and not kicker.is_self:
        now = datetime.now()

        # تحقق من معدل الطرد
        if kicker.id in last_kick_time:
            if (now - last_kick_time[kicker.id]).seconds < 60:
                try:
                    # إزالة صلاحيات المشرف
                    await client.promote_chat_member(
                        chat.id,
                        kicker.id,
                        privileges={}
                    )

                    # رسالة تنبيه
                    msg = (
                        "🚨 **تم عزل مشرف بسبب التفليش** 🚨\n\n"
                        f"👤 المشرف: [{kicker.first_name}](tg://user?id={kicker.id})\n"
                        f"🆔 ايدي: `{kicker.id}`\n"
                        f"📌 المجموعة/القناة: {chat.title}\n"
                        f"⏰ الوقت: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                        f"✅ النتيجة: تم سحب صلاحياته بنجاح"
                    )

                    if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
                        await client.send_message(BOTLOG_CHATID, msg)
                    else:
                        await client.send_message(chat.id, msg)

                except Exception as e:
                    await client.send_message(
                        chat.id,
                        f"⚠️ حدث خطأ أثناء محاولة تنزيل المشرف:\n`{str(e)}`"
                    )

        # تحديث الوقت
        last_kick_time[kicker.id] = now


# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    chat = event.chat
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    db = load_db()
    chat_id = str(event.chat.id)

    if db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش مفعلة مسبقًا في هذه المجموعة/القناة")

    db[chat_id] = True
    save_db(db)
    await event.edit("✅︙ تم تفعيل حماية منع التفليش في هذه المجموعة/القناة")


@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def disable_antiflash(event):
    chat = event.chat
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    db = load_db()
    chat_id = str(event.chat.id)

    if not db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش معطلة مسبقًا في هذه المجموعة/القناة")

    db.pop(chat_id, None)
    save_db(db)
    await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة/القناة")
