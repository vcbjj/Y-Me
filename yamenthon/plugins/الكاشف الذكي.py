import json
import os
from datetime import datetime
from asyncio import sleep, create_task
from telethon import events
from telethon.tl.types import User, UserStatusOnline, UserStatusOffline

from yamenthon import zedub
from . import BOTLOG_CHATID

DATA_FILE = "smart_presence_db.json"

# ====================== إدارة قاعدة البيانات ======================
def load_db():
    if not os.path.exists(DATA_FILE):
        return {"monitored": {}}
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if not isinstance(data, dict):
                return {"monitored": {}}
            if "monitored" not in data:
                data["monitored"] = {}
            return data
    except Exception:
        return {"monitored": {}}

def save_db(db):
    if not isinstance(db, dict):
        db = {"monitored": {}}
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# ====================== أداة مساعدة لحل المستخدم ======================
async def resolve_user_from_arg_or_reply(event, arg: str):
    client = event.client
    target = None

    if event.is_reply:
        try:
            msg = await event.get_reply_message()
            if msg and msg.from_id:
                target = await client.get_entity(msg.from_id)
                return target
        except Exception:
            pass

    if arg:
        arg = arg.strip()
        if arg.isdigit():
            try:
                target = await client.get_entity(int(arg))
                return target
            except Exception:
                pass
        if arg.startswith("@"):
            try:
                target = await client.get_entity(arg)
                return target
            except Exception:
                pass

    return None

# ====================== الأوامر ======================
@zedub.zed_cmd(pattern=r"تفعيل الكاشف الذكي(?:\s+(.+))?$")
async def enable_smart_presence(event):
    if BOTLOG_CHATID in (None, 0, ""):
        await event.reply("⚠️ خطأ: متغير BOTLOG_CHATID غير مضبوط.")
        return

    arg = event.pattern_match.group(1) if event.pattern_match else None
    user_entity = await resolve_user_from_arg_or_reply(event, arg or "")
    if not user_entity or not isinstance(user_entity, User):
        await event.reply("⚠️ لم أستطع العثور على المستخدم.\nاستخدم: `.تفعيل الكاشف الذكي @username` أو رُد على رسالة.")
        return

    uid = int(user_entity.id)
    name = (user_entity.first_name or "") + (" " + user_entity.last_name if getattr(user_entity, "last_name", None) else "")
    if not name.strip():
        name = user_entity.username or str(uid)

    db = load_db()
    monitored = db.setdefault("monitored", {})
    if str(uid) in monitored:
        await event.reply(f"ℹ️ المستخدم [{name}](tg://user?id={uid}) تتم مراقبته بالفعل.")
        return

    monitored[str(uid)] = {
        "first_seen": datetime.utcnow().isoformat(),
        "last_state": None,
        "name": name,
    }
    save_db(db)

    await event.reply(f"✅ تم تفعيل الكاشف الذكي لـ [{name}](tg://user?id={uid}).")

@zedub.zed_cmd(pattern=r"تعطيل الكاشف الذكي(?:\s+(.+))?$")
async def disable_smart_presence(event):
    arg = event.pattern_match.group(1) if event.pattern_match else None
    user_entity = await resolve_user_from_arg_or_reply(event, arg or "")
    if not user_entity or not isinstance(user_entity, User):
        await event.reply("⚠️ لم أستطع العثور على المستخدم.\nاستخدم: `.تعطيل الكاشف الذكي @username` أو رُد على رسالة.")
        return

    uid = int(user_entity.id)
    name = (user_entity.first_name or "") or user_entity.username or str(uid)

    db = load_db()
    monitored = db.setdefault("monitored", {})
    if str(uid) not in monitored:
        await event.reply(f"ℹ️ المستخدم [{name}](tg://user?id={uid}) غير مراقب أصلاً.")
        return

    monitored.pop(str(uid), None)
    save_db(db)
    await event.reply(f"⛔ تم إيقاف مراقبة [{name}](tg://user?id={uid}).")

# ====================== فحص دوري لحالة المستخدمين ======================
async def monitor_users(client, delay=5):
    while True:
        db = load_db()
        monitored = db.get("monitored", {})
        for uid_str, rec in monitored.items():
            try:
                user = await client.get_entity(int(uid_str))
            except Exception:
                continue

            name = rec.get("name") or str(uid_str)
            last_state = rec.get("last_state")

            if hasattr(user, "status"):
                status = user.status
                if isinstance(status, UserStatusOnline):
                    new_state = "online"
                elif isinstance(status, UserStatusOffline):
                    new_state = "offline"
                else:
                    new_state = "unknown"
            else:
                new_state = "unknown"

            if new_state != last_state:
                rec["last_state"] = new_state
                save_db(db)
                if new_state == "online":
                    msg = f"🔔 المستخدم [{name}](tg://user?id={uid_str}) **متصل الآن**\n⏰ {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                    try:
                        await client.send_message(BOTLOG_CHATID, msg)
                    except Exception:
                        pass
        await sleep(delay)

# ====================== بدء المراقبة عند تشغيل البوت ======================
@zedub.on(events.NewMessage(pattern=r'^/start_monitor$'))
async def start_monitor(event):
    await event.reply("🚀 بدء مراقبة جميع المستخدمين المضافين...")
    create_task(monitor_users(event.client))
