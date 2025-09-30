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
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def normalize_chat_record(value):
    if isinstance(value, dict):
        enabled = bool(value.get("enabled", True))
        last_id = int(value.get("last_event_id", 0) or 0)
        return {"enabled": enabled, "last_event_id": last_id}
    if isinstance(value, bool):
        return {"enabled": value, "last_event_id": 0}
    return {"enabled": False, "last_event_id": 0}

def get_chat_record(db, chat_id):
    raw = db.get(chat_id)
    if raw is None:
        return {"enabled": False, "last_event_id": 0}
    return normalize_chat_record(raw)

def set_chat_record(db, chat_id, enabled=None, last_event_id=None):
    rec = get_chat_record(db, chat_id)
    if enabled is not None:
        rec["enabled"] = bool(enabled)
    if last_event_id is not None:
        rec["last_event_id"] = int(last_event_id or 0)
    db[chat_id] = rec

# ===================== المتغيرات التشغيلية =====================
last_kick_time = {}
processed_event_ids = {}
ADMINLOG_POLL_INTERVAL = 5

# ===================== دالة استخراج actor id =====================
def extract_actor_id_from_event(ev):
    """
    استخراج id المشرف (الذي قام بالحظر/الطرد) من حدث السجل.
    """
    # في القنوات: user_id عادة = المشرف الفاعل
    if hasattr(ev, "user_id") and isinstance(ev.user_id, int):
        return ev.user_id

    # fallback على احتمالات أخرى
    for attr in ("actor_id", "admin_id", "from_id"):
        val = getattr(ev, attr, None)
        if val:
            if isinstance(val, int):
                return val
            if hasattr(val, "user_id"):
                return getattr(val, "user_id")
            if hasattr(val, "id"):
                return getattr(val, "id")

    # fallback على داخل action
    act = getattr(ev, "action", None)
    if act:
        uid = getattr(act, "user_id", None)
        if isinstance(uid, int):
            return uid
        uids = getattr(act, "user_ids", None)
        if uids and isinstance(uids, (list, tuple)) and len(uids) > 0:
            if isinstance(uids[0], int):
                return uids[0]
    return None

# ===================== معاقبة المشرف =====================
async def punish_admin(client, chat, actor_id, reason_time):
    try:
        admin_info = await client.get_entity(actor_id)
        admin_name = getattr(admin_info, "first_name", str(actor_id))
        yamen_link = f"[{admin_name}](tg://user?id={actor_id})"

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

        await client(EditAdminRequest(channel=chat, user_id=actor_id, admin_rights=rights, rank=""))

        msg = (
            "🚨 **تم عزل مشرف بسبب التفليش** 🚨\n\n"
            f"👤 المشرف: {yamen_link}\n"
            f"🆔 ايدي: `{actor_id}`\n"
            f"📌 المجموعة/القناة: {getattr(chat, 'title', getattr(chat, 'username', 'غير معروف'))}\n"
            f"⏰ الوقت: {reason_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"✅ النتيجة: تم سحب صلاحياته بنجاح"
        )

        if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
            try:
                await client.send_message(int(BOTLOG_CHATID), msg)
            except Exception:
                await client.send_message(chat.id, msg)
        else:
            await client.send_message(chat.id, msg)

    except Exception as e:
        err = f"⚠️ فشل سحب صلاحيات المشرف `{actor_id}`:\n`{str(e)}`"
        try:
            if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
                await client.send_message(int(BOTLOG_CHATID), err)
            else:
                await client.send_message(chat.id, err)
        except Exception:
            pass

# ===================== مراقبة الطرد في المجموعات =====================
@zedub.on(events.ChatAction)
async def monitor_group_kicks(event):
    try:
        db = load_db()
        chat_id = str(event.chat_id)
        rec = get_chat_record(db, chat_id)
        if not rec["enabled"]:
            return

        if not event.user_kicked:
            return

        kicker = getattr(event.action_message.from_id, "user_id", None)
        if not kicker:
            return

        now = datetime.now()
        prev = last_kick_time.get(kicker)

        if prev and (now - prev).total_seconds() < 60:
            await punish_admin(event.client, event.chat, kicker, now)

        last_kick_time[kicker] = now
    except Exception:
        return

# ===================== مراقبة سجلات الإدارة =====================
async def monitor_admin_logs():
    while True:
        try:
            await zedub.get_me()
            break
        except Exception:
            await asyncio.sleep(1)

    while True:
        try:
            db = load_db()
            for chat_id, raw in list(db.items()):
                rec = normalize_chat_record(raw)
                if not rec["enabled"]:
                    continue

                try:
                    entity = await zedub.get_entity(int(chat_id))
                except Exception:
                    continue

                try:
                    limit = 100
                    last_id = int(rec.get("last_event_id", 0) or 0)

                    result = await zedub(GetAdminLogRequest(
                        channel=entity,
                        q='',
                        min_id=0,
                        max_id=0,
                        limit=limit,
                        events_filter=ChannelAdminLogEventsFilter(
                            kick=True,
                            ban=True
                        ),
                        admins=[]
                    ))

                    events_list = getattr(result, "events", []) or []
                    if not events_list:
                        continue

                    items = []
                    for ev in events_list:
                        ev_id = getattr(ev, "id", None) or getattr(ev, "event_id", None) or 0
                        items.append((int(ev_id or 0), ev))
                    items = [it for it in items if it[0] > last_id]
                    if not items:
                        continue

                    items.sort(key=lambda x: x[0])
                    max_seen = last_id

                    for ev_id, ev in items:
                        if processed_event_ids.get(chat_id, 0) >= ev_id:
                            continue

                        actor_id = extract_actor_id_from_event(ev)
                        # DEBUG:
                        # print("DEBUG EVENT:", ev.stringify())

                        now = datetime.now()
                        if actor_id:
                            prev = last_kick_time.get(actor_id)
                            if prev and (now - prev).total_seconds() < 60:
                                await punish_admin(zedub, entity, actor_id, now)
                            last_kick_time[actor_id] = now

                        if ev_id > max_seen:
                            max_seen = ev_id
                        processed_event_ids[chat_id] = ev_id

                    set_chat_record(db, chat_id, enabled=True, last_event_id=max_seen)
                    save_db(db)

                except Exception:
                    continue

        except Exception:
            pass

        await asyncio.sleep(ADMINLOG_POLL_INTERVAL)

try:
    zedub.loop.create_task(monitor_admin_logs())
except Exception:
    pass

# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    try:
        db = load_db()
        chat_id = str(event.chat_id)
        set_chat_record(db, chat_id, enabled=True,
                        last_event_id=get_chat_record(db, chat_id)["last_event_id"])
        save_db(db)
        await event.edit("✅︙ تم تفعيل حماية منع التفليش في هذه المجموعة/القناة")
    except Exception as e:
        await event.edit(f"⚠️ حدث خطأ: `{str(e)}`")

@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def disable_antiflash(event):
    try:
        db = load_db()
        chat_id = str(event.chat_id)
        set_chat_record(db, chat_id, enabled=False,
                        last_event_id=get_chat_record(db, chat_id)["last_event_id"])
        save_db(db)
        await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة/القناة")
    except Exception as e:
        await event.edit(f"⚠️ حدث خطأ: `{str(e)}`")
