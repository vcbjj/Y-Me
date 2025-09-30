from datetime import datetime
from telethon import events
from telethon.tl.types import ChatAdminRights, Channel, ChannelAdminLogEvent
from telethon.tl.functions.channels import EditAdminRequest, GetAdminLogRequest
from yamenthon import zedub
from . import gvarstatus, addgvar, delgvar, BOTLOG_CHATID
import json, os

DB_FILE = "anti_kick_db.json"

def load_db():
    if not os.path.exists(DB_FILE): return {}
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f: return json.load(f)
    except: return {}

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

remove_admins_aljoker = {}  # آخر وقت طرد لكل مشرف

@zedub.on(events.ChatAction)
async def monitor_kicks(event):
    db = load_db()
    chat_id = str(event.chat_id)
    if chat_id not in db or not db[chat_id]: return

    chat = await event.get_chat()
    if not chat: return

    try:
        is_channel = isinstance(chat, Channel)

        # --- مجموعات / سوبرجروب ---
        if getattr(event, "user_kicked", False):
            user_id = getattr(getattr(event.action_message, "from_id", None), "user_id", None)
            if not user_id: return
            now = datetime.now()
            if user_id in remove_admins_aljoker and (now - remove_admins_aljoker[user_id]).seconds < 60:
                admin_info = await event.client.get_entity(user_id)
                rights = ChatAdminRights(
                    change_info=False, post_messages=False, edit_messages=False,
                    delete_messages=False, ban_users=False, invite_users=False,
                    pin_messages=False, add_admins=False, manage_call=False,
                    anonymous=False
                )
                await event.client(EditAdminRequest(channel=chat, user_id=user_id, admin_rights=rights, rank=""))
                msg = f"🚨 تم عزل مشرف بسبب التفليش: [{admin_info.first_name}](tg://user?id={admin_info.id})"
                if BOTLOG_CHATID: await event.client.send_message(BOTLOG_CHATID, msg)
            remove_admins_aljoker[user_id] = now
            return

        # --- القنوات: سجل الإدارة ---
        if is_channel:
            result = await event.client(GetAdminLogRequest(channel=chat, limit=5))
            for entry in getattr(result, "events", []):
                if isinstance(entry, ChannelAdminLogEvent) and entry.action:
                    if "ParticipantBan" in entry.action.__class__.__name__:
                        actor = entry.user_id
                        now = datetime.now()
                        if actor in remove_admins_aljoker and (now - remove_admins_aljoker[actor]).seconds < 60:
                            admin_info = await event.client.get_entity(actor)
                            rights = ChatAdminRights(
                                change_info=False, post_messages=False, edit_messages=False,
                                delete_messages=False, ban_users=False, invite_users=False,
                                pin_messages=False, add_admins=False, manage_call=False,
                                anonymous=False
                            )
                            await event.client(EditAdminRequest(channel=chat, user_id=actor, admin_rights=rights, rank=""))
                            msg = f"🚨 تم عزل مشرف بسبب التفليش في القناة: [{admin_info.first_name}](tg://user?id={admin_info.id})"
                            if BOTLOG_CHATID: await event.client.send_message(BOTLOG_CHATID, msg)
                        remove_admins_aljoker[actor] = now
    except: return

# ================= الأوامر =================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    chat = await event.get_chat()
    if not chat: return await event.edit("⚠️ لا يمكن استخدام هذا الأمر هنا")
    db = load_db()
    db[str(chat.id)] = True
    save_db(db)
    await event.edit("✅ تم تفعيل حماية منع التفليش في هذه المجموعة/القناة")

@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def disable_antiflash(event):
    chat = await event.get_chat()
    if not chat: return await event.edit("⚠️ لا يمكن استخدام هذا الأمر هنا")
    db = load_db()
    db.pop(str(chat.id), None)
    save_db(db)
    await event.edit("🛑 تم تعطيل حماية منع التفليش في هذه المجموعة/القناة")
