"""
📌 منع التفليش (Anti-Kick Flood) - سورس يمنثون

- الأوامر:
  .منع التفليش   ← تفعيل حماية منع التفليش
  .سماح التفليش  ← تعطيل حماية منع التفليش

- يدعم:
  ✅ المجموعات العادية
  ✅ السوبرجروب
  ✅ القنوات (broadcast + discussion)

- عند محاولة أي مشرف طرد عدة أعضاء بسرعة (تفليش),
  يتم تنزيله مباشرة من الإدارة وإرسال تنبيه إلى مجموعة السجلات BOTLOG_CHATID.
"""

import json
import os
from datetime import datetime, timedelta
from telethon import events
from telethon.tl.types import ChatAdminRights, Channel, ChannelAdminLogEventActionParticipantBan
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
kick_count = {}  # لتسجيل عدد الطرد خلال دقيقة لكل مشرف

# ===================== دالة عزل المشرف =====================
async def demote_admin(client, chat, user_id, admin_info):
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

    yamen_link = f"[{admin_info.first_name}](tg://user?id={admin_info.id})"
    now = datetime.now()
    msg = (
        f"🚨 **تم عزل مشرف بسبب التفليش** 🚨\n\n"
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

    is_channel = isinstance(chat, Channel)

    try:
        # --- الحالة الأولى: مجموعات وسوبرجروب ---
        if getattr(event, "user_kicked", False):
            user_id = getattr(getattr(event.action_message, "from_id", None), "user_id", None)
            if not user_id:
                return

            now = datetime.now()
            # زيادة العد أو تهيئته
            if user_id not in kick_count:
                kick_count[user_id] = {"count": 1, "time": now}
            else:
                last = kick_count[user_id]
                if now - last["time"] > timedelta(seconds=60):
                    kick_count[user_id] = {"count": 1, "time": now}
                else:
                    kick_count[user_id]["count"] += 1
                    kick_count[user_id]["time"] = now
                    if kick_count[user_id]["count"] >= 2:  # شرط التفليش
                        try:
                            admin_info = await event.client.get_entity(user_id)
                            await demote_admin(event.client, chat, user_id, admin_info)
                        except Exception:
                            pass
                        kick_count[user_id] = {"count": 0, "time": now}
            return

        # --- الحالة الثانية: القنوات (سجل الإدارة) ---
        if is_channel:
            result = await event.client(GetAdminLogRequest(
                channel=chat,
                q="",
                max_id=0,
                min_id=0,
                limit=10
            ))

            for entry in getattr(result, "events", []):
                if isinstance(entry.action, ChannelAdminLogEventActionParticipantBan):
                    actor = entry.user_id
                    now = datetime.now()
                    # زيادة العد أو تهيئته
                    if actor not in kick_count:
                        kick_count[actor] = {"count": 1, "time": now}
                    else:
                        last = kick_count[actor]
                        if now - last["time"] > timedelta(seconds=60):
                            kick_count[actor] = {"count": 1, "time": now}
                        else:
                            kick_count[actor]["count"] += 1
                            kick_count[actor]["time"] = now
                            if kick_count[actor]["count"] >= 2:  # شرط التفليش
                                try:
                                    admin_info = await event.client.get_entity(actor)
                                    await demote_admin(event.client, chat, actor, admin_info)
                                except Exception:
                                    pass
                                kick_count[actor] = {"count": 0, "time": now}

    except Exception:
        return

# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    db = load_db()
    chat_id = str(event.chat_id)
    if db.get(chat_id):
        return await event.edit("ℹ️︙ حماية منع التفليش مفعلة مسبقًا هنا")

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
        return await event.edit("ℹ️︙ حماية منع التفليش معطلة مسبقًا هنا")

    db.pop(chat_id, None)
    save_db(db)
    await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة/القناة")
