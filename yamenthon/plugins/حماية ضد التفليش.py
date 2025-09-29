"""ملحق Anti-Flashing متوافق مع سورس يمنثون (Telethon)

- تفعيل/تعطيل الحماية بالأوامر:
  .قفل التفليش
  .فتح التفليش

- يقوم بمراقبة عمليات الطرد (kick) في القنوات/المجموعات،
  ويعزل المشرف الذي قام بالطرد تلقائياً،
  ويرسل إشعاراً إلى مجموعة السجلات BOTLOG_CHATID.

"""

import json
import os
from datetime import datetime
from telethon import events
from telethon.tl.functions.channels import GetAdminLogRequest, EditAdminRequest
from telethon.tl.types import ChatAdminRights

# ملف قاعدة البيانات (حالة التفعيل لكل شات)
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
from yamenthon import zedub
from ..Config import Config
from . import BOTLOG, BOTLOG_CHATID


# ===================== الأوامر =====================
@zedub.zed_cmd(pattern=r"^\.قفل التفليش$")
async def enable_anti(event):
    """تفعيل الحماية من التفليش"""
    db = load_db()
    chat_id = str(event.chat_id)
    db[chat_id] = True
    save_db(db)
    await event.reply("✅ تم تفعيل حماية التفليش في هذه المجموعة/القناة")


@zedub.zed_cmd(pattern=r"^\.فتح التفليش$")
async def disable_anti(event):
    """تعطيل الحماية من التفليش"""
    db = load_db()
    chat_id = str(event.chat_id)
    if chat_id in db:
        db.pop(chat_id)
        save_db(db)
    await event.reply("🛑 تم تعطيل حماية التفليش في هذه المجموعة/القناة")


# ===================== المراقبة =====================
@zedub.on(events.ChatAction)
async def monitor_kicks(event):
    """مراقبة الطرد وعزل المشرف المنفذ"""
    db = load_db()
    if str(event.chat_id) not in db:
        return

    try:
        # نتأكد أن الحدث عبارة عن طرد
        if getattr(event, "user_kicked", False):
            target = event.user
        elif getattr(event, "left", False) and not getattr(event, "user_joined", False):
            target = event.user
        else:
            return
    except Exception:
        return

    try:
        # نجلب آخر 30 سجل إداري في الشات
        result = await bot(GetAdminLogRequest(
            channel=event.chat_id,
            q='',
            max_id=0,
            min_id=0,
            limit=30,
            events_filter=None
        ))

        actor_id = None
        events_list = getattr(result, 'events', []) or getattr(result, 'entries', [])
        for ev in events_list:
            if hasattr(ev, 'user_id') and ev.user_id == getattr(target, 'id', None):
                actor_id = getattr(ev, 'actor_id', None)
                break
            if hasattr(ev, 'affected') and getattr(ev, 'affected'):
                for a in ev.affected:
                    if getattr(a, 'user_id', None) == getattr(target, 'id', None):
                        actor_id = getattr(ev, 'actor_id', None)
                        break
            if actor_id:
                break

        if not actor_id:
            return

        # إزالة صلاحيات المشرف
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

        # تجهيز رسالة الإشعار
        try:
            actor = await bot.get_entity(actor_id)
        except Exception:
            actor = None
        try:
            target_ent = await bot.get_entity(target.id)
        except Exception:
            target_ent = None

        msg = "🚨 تم عزل مشرف قام بطرد عضو\n\n"
        if actor:
            name = actor.first_name or ""
            if actor.last_name:
                name += " " + actor.last_name
            msg += f"المشرف: {name}\n"
            if actor.username:
                msg += f"يوزر: @{actor.username}\n"
            msg += f"ايدي: {actor.id}\n"
        else:
            msg += f"المشرف: غير معروف (id: {actor_id})\n"

        if target_ent:
            tname = target_ent.first_name or ""
            if target_ent.last_name:
                tname += " " + target_ent.last_name
            msg += f"العضو الذي طُرد: {tname}\n"
            if target_ent.username:
                msg += f"يوزر العضو: @{target_ent.username}\n"
            msg += f"ايدي العضو: {target_ent.id}\n"
        else:
            msg += "العضو الذي طُرد: غير معروف\n"

        msg += f"الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        msg += f"نجح سحب الصلاحيات: {'نعم' if demoted else 'لا'}\n"

        # إرسال الإشعار
        if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
            await bot.send_message(BOTLOG_CHATID, msg)
        else:
            await bot.send_message(event.chat_id, msg)

    except Exception:
        return
