"""
ملحق Anti-Flashing متوافق مع سورس يمنثون (Telethon)

- تفعيل/تعطيل الحماية بالأوامر:
  .قفل التفليش
  .فتح التفليش

- يراقب الطرد في القنوات والمجموعات العادية والسوبرجروب،
  يعزل المشرف الذي نفذ الطرد تلقائياً،
  ويرسل تقرير مفصل إلى BOTLOG_CHATID.
"""

import json
import os
from datetime import datetime
from telethon import events
from telethon.tl.functions.channels import GetAdminLogRequest, EditAdminRequest
from telethon.tl.types import ChatAdminRights

# ملف قاعدة البيانات
DB_FILE = "anti_flashing.json"

# ===================== قاعدة البيانات =====================
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# ===================== استدعاءات سورس يمنثون =====================
from yamenthon import zedub, bot
from ..Config import Config
from . import BOTLOG, BOTLOG_CHATID

# ===================== الأوامر =====================
@zedub.zed_cmd(pattern=r"^\.قفل التفليش$")
async def enable_anti(event):
    db = load_db()
    chat_id = str(event.chat_id)
    db[chat_id] = True
    save_db(db)
    await event.reply("✅ تم تفعيل حماية التفليش في هذه المجموعة/القناة")

@zedub.zed_cmd(pattern=r"^\.فتح التفليش$")
async def disable_anti(event):
    db = load_db()
    chat_id = str(event.chat_id)
    if chat_id in db:
        db.pop(chat_id)
        save_db(db)
    await event.reply("🛑 تم تعطيل حماية التفليش في هذه المجموعة/القناة")

# ===================== المراقبة =====================
@zedub.on(events.ChatAction)
async def monitor_kicks(event):
    db = load_db()
    if str(event.chat_id) not in db:
        return

    # تحديد الهدف الذي تم طرده
    target = None
    try:
        if getattr(event, "user_kicked", False):
            target = getattr(event, "user", None)
        elif getattr(event, "left", False) and not getattr(event, "user_joined", False):
            target = getattr(event, "user", None)
    except Exception:
        return
    if not target or not getattr(target, 'id', None):
        return

    # جلب سجلات الإدارة الأخيرة
    try:
        result = await bot(GetAdminLogRequest(
            channel=event.chat_id,
            q='',
            max_id=0,
            min_id=0,
            limit=50,  # زيادة الحد لمزيد من الدقة
            events_filter=None
        ))
    except Exception:
        return

    events_list = getattr(result, 'events', None) or getattr(result, 'entries', None)
    if not events_list:
        return

    actor_id = None
    for ev in events_list:
        if ev is None:
            continue
        try:
            if hasattr(ev, 'user_id') and ev.user_id == getattr(target, 'id', None):
                actor_id = getattr(ev, 'actor_id', None)
                break
            if hasattr(ev, 'affected') and getattr(ev, 'affected', None):
                for a in ev.affected:
                    if not a:
                        continue
                    if getattr(a, 'user_id', None) == getattr(target, 'id', None):
                        actor_id = getattr(ev, 'actor_id', None)
                        break
            if actor_id:
                break
        except Exception:
            continue
    if not actor_id:
        return

    # إزالة صلاحيات المشرف
    demoted = False
    empty_rights = ChatAdminRights(
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
        other=False,
    )
    try:
        await bot(EditAdminRequest(
            channel=event.chat_id,
            user_id=actor_id,
            admin_rights=empty_rights,
            rank=""
        ))
        demoted = True
    except Exception:
        demoted = False

    # جلب معلومات المشرف والعضو
    actor = None
    target_ent = None
    try:
        actor = await bot.get_entity(actor_id)
    except Exception:
        actor = None
    try:
        target_ent = await bot.get_entity(target.id)
    except Exception:
        target_ent = None

    # تجهيز تقرير مفصل
    msg = "🚨 تم عزل مشرف قام بطرد عضو\n\n"
    if actor:
        name = (actor.first_name or "") + (" " + actor.last_name if actor.last_name else "")
        msg += f"المشرف: {name}\n"
        if actor.username:
            msg += f"يوزر: @{actor.username}\n"
        msg += f"ايدي: {actor.id}\n"
    else:
        msg += f"المشرف: غير معروف (id: {actor_id})\n"

    if target_ent:
        tname = (target_ent.first_name or "") + (" " + target_ent.last_name if target_ent.last_name else "")
        msg += f"العضو الذي طُرد: {tname}\n"
        if target_ent.username:
            msg += f"يوزر العضو: @{target_ent.username}\n"
        msg += f"ايدي العضو: {target_ent.id}\n"
    else:
        msg += "العضو الذي طُرد: غير معروف\n"

    msg += f"الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
    msg += f"نجح سحب الصلاحيات: {'نعم' if demoted else 'لا'}\n"

    # إرسال التقرير
    try:
        if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
            await bot.send_message(BOTLOG_CHATID, msg)
        else:
            await bot.send_message(event.chat_id, msg)
    except Exception:
        return
