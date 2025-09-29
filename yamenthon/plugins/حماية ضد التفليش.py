"""ملحق Anti-Flashing متوافق مع سورس يمنثون (Telethon)

يعتمد على وجود المتغيرات التالية في مشروعك: zedub, bot, BOTLOG_CHATID

يقوم بمراقبة عمليات الطرد (kick) في القنوات/المجموعات، ويعزل المشرف الذي قام بالطرد

ويُرسل إشعارًا إلى مجموعة الاشعارات BOTLOG_CHATID مع تفاصيل المشرف والمطلوب.
"""
import json
import os
from datetime import datetime
from telethon import events, types
from telethon.tl.functions.channels import GetAdminLogRequest, EditAdminRequest
from telethon.tl.types import ChannelAdminLogEventsFilter, ChatAdminRights
# لا تغير: اسم الملف لحفظ حالة التفعيل لكل شات
DB_FILE = "anti_flashing.json"

# helper: تحميل/حفظ قاعدة البيانات البسيطة
def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(db, f, ensure_ascii=False, indent=2)

# ندعم ديكوريتور zedub.zed_cmd الموجود في سورس يمنثون
from yamenthon import zedub, bot
from ..Config import Config
from . import BOTLOG, BOTLOG_CHATID


# أوامر تفعيل/تعطيل
@zedub.zed_cmd(pattern=r"^.قفل التفليش$")
async def enable_anti(event):
    """تفعيل الحماية من التفليش في الشات الحالي"""
    db = load_db()
    chat_id = str(event.chat_id)
    db[chat_id] = True
    save_db(db)
    await event.reply("✅ تم تفعيل حماية التفليش في هذه المجموعة/القناة")

@zedub.zed_cmd(pattern=r"^.فتح التفليش$")
async def disable_anti(event):
    """تعطيل الحماية من التفليش في الشات الحالي"""
    db = load_db()
    chat_id = str(event.chat_id)
    if chat_id in db:
        db.pop(chat_id)
        save_db(db)
    await event.reply("🛑 تم تعطيل حماية التفليش في هذه المجموعة/القناة")

# مراقبة إجراءات الدردشة (ChatAction)
@bot.on(events.ChatAction)
async def monitor_kicks(event):
    # نتأكد أن العمل في شات مدعوم
    db = load_db()
    if str(event.chat_id) not in db:
        return

    # إذا تم طرد (kick) مستخدم
    # ملاحظة: event.user_kicked قد لا يكون مدعوماً في كل نسخ telethon؛
    # سنستخدم فحص الأنواع لتحديد حالة الطرد/الحظر
    try:
        # Telethon يوفر شرط event.user_kicked في بعض الإصدارات
        if getattr(event, "user_kicked", False):
            target = event.user
        else:
            # بديل: إذا حدث left وحالة 'kicked' في raw update
            if getattr(event, "left", False) and not getattr(event, "user_joined", False):
                # قد لا يفرق بين leave وkick؛ نتحقق عبر سجلات المشرفين لاحقًا
                target = event.user
            else:
                return
    except Exception:
        return

    # نحاول الحصول على آخر سجل إداري لنعرف من نفذ الطرد
    try:
        # Filter للبحث عن الأحداث المتعلقة بحذف المستخدمين
        filt = ChannelAdminLogEventsFilter(flags=getattr(types, 'ChannelAdminLogEventsFilterFlags', lambda: None)()) if hasattr(types, 'ChannelAdminLogEventsFilterFlags') else None
        
        # نطلب سجلات المسؤولين في الشات، نبحث عن آخر 20 حدثًا
        result = await bot(GetAdminLogRequest(
            channel=event.chat_id,
            q='',
            max_id=0,
            min_id=0,
            limit=30,
            events_filter=None  # لاستخدام الافتراضي، لأن الفلاتر قد تختلف بالإصدار
        ))

        # تحليل النتائج الخام للحصول على آخر actor الذي أثر على target
        actor_id = None
        action_time = None
        
        # result.entries يحتوي على سجلات الأحداث
        events_list = getattr(result, 'events', []) or getattr(result, 'entries', [])

        # نحاول مطابقة الهدف في أي سجل حديث
        for ev in events_list:
            try:
                # كل حدث قد يحتوي على "users" أو "affected" أو "user_id" حسب النوع
                if hasattr(ev, 'user_id') and ev.user_id == getattr(target, 'id', None):
                    actor_id = getattr(ev, 'actor_id', None)
                    action_time = getattr(ev, 'date', None)
                    break
                
                # بعض الأحداث تحتوي على 'affected' كقائمة
                if hasattr(ev, 'affected') and getattr(ev, 'affected'):
                    for a in ev.affected:
                        if getattr(a, 'user_id', None) == getattr(target, 'id', None):
                            actor_id = getattr(ev, 'actor_id', None)
                            action_time = getattr(ev, 'date', None)
                            break
                    if actor_id:
                        break
            except Exception:
                continue

        if not actor_id:
            # لم نجد من نفذ الطرد؛ نختم هنا
            return

        # الآن نزيل صلاحيات المشرف (نعزله عن الاشراف) - يتطلب أن البوت لديه صلاحية إدارة المشرفين
        try:
            # إعداد حقوق فارغة تعني عدم وجود صلاحيات
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
                other=False
            )

            # نجرب تنفيذ طلب إزالة صلاحيات المشرف
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

        except Exception:
            demoted = False

        # إعداد رسالة الاشعار
        actor = None
        try:
            actor = await bot.get_entity(actor_id)
        except Exception:
            actor = None

        target_ent = None
        try:
            target_ent = await bot.get_entity(target.id)
        except Exception:
            target_ent = None

        msg = f"🚨 تم عزل مشرف قام بطرد عضو\n\n"
        if actor:
            uname = getattr(actor, 'username', None)
            name = getattr(actor, 'first_name', '') + (' ' + getattr(actor, 'last_name', '') if getattr(actor, 'last_name', None) else '')
            msg += f"المشرف: {name}\n" 
            if uname:
                msg += f"يوزر: @{uname}\n"
            msg += f"ايدي: {getattr(actor, 'id', 'غير متوفر')}\n"
        else:
            msg += f"المشرف: لم نستطع جلب بياناته (id: {actor_id})\n"

        if target_ent:
            tname = getattr(target_ent, 'first_name', '') + (' ' + getattr(target_ent, 'last_name', '') if getattr(target_ent, 'last_name', None) else '')
            tusername = getattr(target_ent, 'username', None)
            msg += f"العضو الذي طُرد: {tname}\n"
            if tusername:
                msg += f"يوزر العضو: @{tusername}\n"
            msg += f"ايدي العضو: {getattr(target_ent, 'id', 'غير متوفر')}\n"
        else:
            msg += f"العضو الذي طُرد: لم نستطع جلب بياناته\n"

        msg += f"الوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
        msg += f"نجح سحب الصلاحيات: {'نعم' if demoted else 'لا'}\n"

        # نرسل الاشعار لمجموعة الاشعارات
        try:
            if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
                await bot.send_message(BOTLOG_CHATID, msg)
        except Exception:
            # إذا إرسال الرسالة فشل، نرسل داخل نفس الشات إن أمكن
            try:
                await bot.send_message(event.chat_id, msg)
            except Exception:
                pass

    except Exception as e:
        # أي خطأ عام — لا نوقف البوت
        return

"""ملاحظات:

1. لكي يعمل السحب التلقائي للصلاحيات يجب أن يكون للبوت صلاحيات إدارة المشرفين في القناة/المجموعة.

2. بعض أنواع المحادثات (مجموعات بسيطة vs سوبرجروب vs قناة) تتطلب استدعاءات مختلفة لإدارة الصلاحيات.

3. قد تحتاج إلى تعديل استخدام GetAdminLogRequest / EditAdminRequest بحسب نسخة Telethon لديك.

4. هذا الملف يحفظ حالة التفعيل لكل شات في anti_flashing.json في مجلد التشغيل.

5. إذا واجهت مشكلة في التعرف على من نفذ الطرد، يمكنك زيادة limit في GetAdminLogRequest أو تسجيل السجلات (logging).

"""
