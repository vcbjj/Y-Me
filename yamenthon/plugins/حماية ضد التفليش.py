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
    """
    يتعامل مع القيمة القديمة (True) أو الجديدة (dict)
    يرجع dict يحتوي keys: enabled, last_event_id
    """
    if isinstance(value, dict):
        enabled = bool(value.get("enabled", True))
        last_id = int(value.get("last_event_id", 0) or 0)
        return {"enabled": enabled, "last_event_id": last_id}
    if isinstance(value, bool):
        return {"enabled": value, "last_event_id": 0}
    # fallback
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
# يخزن آخر وقت طرد لكل مشرف (actor_id -> datetime)
last_kick_time = {}
# لمنع معالجة نفس AdminLog event أكثر من مرة أثناء الجلسة:
processed_event_ids = {}  # chat_id -> last_event_id

# وقت الانتظار بين كل فحص لسجلات الإدارة (بالثواني)
ADMINLOG_POLL_INTERVAL = 5


# ===================== دالة مساعدة لاستخراج actor id من حدث السجل =====================
def extract_actor_id_from_event(ev):
    """
    يحاول استخراج id الخاص بالمستخدم الذي قام بالعملية (المشرف / actor).
    يغطي عدة صيغ قد ترجعها Telethon.
    """
    # محاولات مباشرة
    for attr in ("user_id", "actor_id", "admin_id", "from_id"):
        val = getattr(ev, attr, None)
        if val:
            # val قد يكون int أو object يحتوي user_id/id
            if isinstance(val, int):
                return val
            if hasattr(val, "user_id"):
                return getattr(val, "user_id")
            if hasattr(val, "id"):
                return getattr(val, "id")

    # جرب الوصول داخل .action (قد تكون action تحتوي على user_id أو user_ids)
    act = getattr(ev, "action", None)
    if act:
        # user_id مفرد
        uid = getattr(act, "user_id", None)
        if uid:
            if isinstance(uid, int):
                return uid
            if hasattr(uid, "user_id"):
                return getattr(uid, "user_id")
            if hasattr(uid, "id"):
                return getattr(uid, "id")
        # user_ids قائمة
        uids = getattr(act, "user_ids", None)
        if uids and isinstance(uids, (list, tuple)) and len(uids) > 0:
            first = uids[0]
            if isinstance(first, int):
                return first
            if hasattr(first, "user_id"):
                return getattr(first, "user_id")
            if hasattr(first, "id"):
                return getattr(first, "id")
    return None


# ===================== دالة معاقبة المشرف (سحب الصلاحيات) =====================
async def punish_admin(client, chat, actor_id, reason_time):
    """
    يحاول سحب صلاحيات المشرف (actor_id) في الشات المحدد.
    يرسل إشعاراً إلى BOTLOG_CHATID أو إلى الشات نفسه.
    """
    try:
        # جلب بيانات المشرف للعرض
        admin_info = await client.get_entity(actor_id)
        admin_name = getattr(admin_info, "first_name", str(actor_id))
        yamen_link = f"[{admin_name}](tg://user?id={actor_id})"

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

        # تنفيذ العزل (سحب الصلاحيات)
        await client(EditAdminRequest(channel=chat, user_id=actor_id, admin_rights=rights, rank=""))

        # رسالة التنبيه
        msg = (
            "🚨 **تم عزل مشرف بسبب التفليش** 🚨\n\n"
            f"👤 المشرف: {yamen_link}\n"
            f"🆔 ايدي: `{actor_id}`\n"
            f"📌 المجموعة/القناة: {getattr(chat, 'title', getattr(chat, 'username', 'غير معروف'))}\n"
            f"⏰ الوقت: {reason_time.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"✅ النتيجة: تم سحب صلاحياته بنجاح"
        )

        # إرسال الإشعار إلى BOTLOG_CHATID إذا معرف، وإلا للإستنطاق في نفس الشات
        if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
            try:
                await client.send_message(int(BOTLOG_CHATID), msg)
            except Exception:
                await client.send_message(chat.id if hasattr(chat, 'id') else chat, msg)
        else:
            await client.send_message(chat.id if hasattr(chat, 'id') else chat, msg)

    except Exception as e:
        # لو فشل العزل، نبلغ BOTLOG أو الشات برسالة خطأ
        err = f"⚠️ فشل سحب صلاحيات المشرف `{actor_id}`:\n`{str(e)}`"
        try:
            if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
                await client.send_message(int(BOTLOG_CHATID), err)
            else:
                await client.send_message(chat.id if hasattr(chat, 'id') else chat, err)
        except Exception:
            pass


# ===================== مراقبة الطرد في المجموعات (ChatAction) =====================
@zedub.on(events.ChatAction)
async def monitor_group_kicks(event):
    """
    هذا الجزء يعمل كما كان: يراقب ChatAction للمجموعات/السوبرجروبات.
    """
    try:
        db = load_db()
        chat_id = str(event.chat_id)
        rec = get_chat_record(db, chat_id)
        if not rec["enabled"]:
            return

        # فقط عالج طرد الأعضاء
        if not event.user_kicked:
            return

        # من قام بالطرد (من action_message.from_id)
        kicker = getattr(event.action_message.from_id, "user_id", None)
        if not kicker:
            return

        now = datetime.now()
        prev = last_kick_time.get(kicker)

        # لو المشرف طرد أكثر من شخص خلال دقيقة -> عاقبه
        if prev and (now - prev).total_seconds() < 60:
            await punish_admin(event.client, event.chat, kicker, now)

        # حدث الطرد يتم تسجيل وقته
        last_kick_time[kicker] = now

    except Exception:
        return


# ===================== مهمة فحص سجلات الإدارة (Admin Log) لكل الشات المفعلة =====================
async def monitor_admin_logs():
    # انتظار تأكد من اتصال الـ client
    while True:
        try:
            # محاولة جلب me للتأكد من أن zedub متصل وجاهز
            await zedub.get_me()
            break
        except Exception:
            await asyncio.sleep(1)

    # حلقة فحص مستمرة
    while True:
        try:
            db = load_db()
            # iterate over كل شات محفوظ في DB
            for chat_id, raw in list(db.items()):
                rec = normalize_chat_record(raw)
                if not rec["enabled"]:
                    continue

                try:
                    # جلب الـ entity للشات
                    entity = await zedub.get_entity(int(chat_id))
                except Exception:
                    # لا نستطيع الوصول للشات (ربما تم حذف البوت/الغاء الدعوة) -> تخطي
                    continue

                # نستعمل GetAdminLogRequest لجميع أنواع القنوات/مجموعات (لو الحساب يملك صلاحية)
                try:
                    # حد الاستدعاء: نحاول استرجاع حتى 100 حدث جديد
                    limit = 100
                    last_id = int(rec.get("last_event_id", 0) or 0)

                    # نجلب آخر أحداث السجل (الأحدث أولاً عادة)
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

                    # نحاول استخراج معرفات الأحداث (id) وترتيبها من الأقدم للأحدث
                    items = []
                    for ev in events_list:
                        ev_id = getattr(ev, "id", None) or getattr(ev, "event_id", None) or 0
                        items.append((int(ev_id or 0), ev))
                    # تصفية الأحداث الأقدم من last_id
                    items = [it for it in items if it[0] > last_id]
                    if not items:
                        continue

                    items.sort(key=lambda x: x[0])  # من الأقدم للأحدث

                    max_seen = last_id
                    for ev_id, ev in items:
                        # منع معالجة نفس الحدث أكثر من مرة في الجلسة
                        if processed_event_ids.get(chat_id, 0) >= ev_id:
                            continue

                        # محاولة استخراج actor id
                        actor_id = extract_actor_id_from_event(ev)
                        now = datetime.now()

                        if actor_id:
                            prev = last_kick_time.get(actor_id)
                            if prev and (now - prev).total_seconds() < 60:
                                # تم طرد أكثر من مرة خلال دقيقة -> عاقب
                                await punish_admin(zedub, entity, actor_id, now)

                            # سجّل وقت الطرد للمشرف
                            last_kick_time[actor_id] = now

                        # حدّث المتغيرات لتعقب التقدّم
                        if ev_id > max_seen:
                            max_seen = ev_id
                        processed_event_ids[chat_id] = ev_id

                    # تحديث الـ DB مع آخر event id تمت معالجته
                    set_chat_record(db, chat_id, enabled=True, last_event_id=max_seen)
                    save_db(db)

                except Exception:
                    # لا مشكلة — تفشل القراءة لبعض الشاتات أحيانا (صلاحيات/نوع الشات) -> تجاهل
                    continue

        except Exception:
            # خطأ عام في الحلقة — تجاهل واستمر
            pass

        await asyncio.sleep(ADMINLOG_POLL_INTERVAL)


# تشغيل مهمة الفحص في الخلفية عند تحميل الموديول
try:
    zedub.loop.create_task(monitor_admin_logs())
except Exception:
    # لو لم يكن هناك loop متاح، تجاوز بهدوء (سيعمل عند التشغيل)
    pass


# ===================== الأوامر (تفعيل/تعطيل) =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    try:
        db = load_db()
        chat_id = str(event.chat_id)
        set_chat_record(db, chat_id, enabled=True, last_event_id=get_chat_record(db, chat_id)["last_event_id"])
        save_db(db)
        await event.edit("✅︙ تم تفعيل حماية منع التفليش في هذه المجموعة/القناة")
    except Exception as e:
        await event.edit(f"⚠️ حدث خطأ: `{str(e)}`")

@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def disable_antiflash(event):
    try:
        db = load_db()
        chat_id = str(event.chat_id)
        set_chat_record(db, chat_id, enabled=False, last_event_id=get_chat_record(db, chat_id)["last_event_id"])
        save_db(db)
        await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة/القناة")
    except Exception as e:
        await event.edit(f"⚠️ حدث خطأ: `{str(e)}`")
