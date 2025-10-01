#-- coding: utf-8 --

""" Plugin: كشف الحضور الذكي متوافق مع مشروع يمنثون (yamenthon) ويستخدم @zedub.zed_cmd وظيفة: تفعيل/تعطيل مراقبة وجود المستخدمين (online) وإرسال إشعار لمجموعة التسجيل BOTLOG_CHATID

طريقة الاستخدام: .تفعيل الكاشف الذكي <@username | user_id> أو الرد على رسالة الشخص: .تفعيل الكاشف الذكي

.تعطيل الكاشف الذكي <@username | user_id> أو الرد على رسالة الشخص: .تعطيل الكاشف الذكي

احفظ الملف داخل مجلد plugins باسم: كشف_الحضور_الذكي.py

ملاحظات:

يحتاج البوت/اليوزربوت لصلاحية رؤية الحالة (presence). بعض الإعدادات في تيليجرام قد تمنع رؤية الحالة.

يتم عمل فحص دوري (polling) كل 15 ثانية. يمكن تعديل INTERVAL_SEC إن رغبت.

الإشعارات تُرسل إلى BOTLOG_CHATID المعرفة في مشروعك. """


import json import os import asyncio from datetime import datetime from telethon.errors import RPCError from telethon.tl.types import User

from yamenthon import zedub from . import BOTLOG_CHATID

DATA_FILE = "smart_presence_db.json" INTERVAL_SEC = 5  # فترة التحقق بالدقائق: يمكنك تقليل/زيادة حسب حاجتك

بنية الملف: {"monitored": {"<user_id>": {"first_seen": "...", "last_state": "online"/"offline", "name": "..."}}}

def load_db(): if not os.path.exists(DATA_FILE): return {"monitored": {}} try: with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f) except Exception: return {"monitored": {}}

def save_db(db): with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(db, f, ensure_ascii=False, indent=2)

async def resolve_user_from_arg_or_reply(event, arg: str): """حلّل الوسائط (يوزر/آيدي) أو الرد للحصول على كيان المستخدم و user_id و اسم""" client = event.client target = None

# أولاً: إذا تم الرد على رسالة
if event.is_reply:
    try:
        msg = await event.get_reply_message()
        if msg and msg.from_id:
            target = await client.get_entity(msg.from_id)
            return target
    except Exception:
        pass

# ثانياً: إذا وردت وسائط نصية (يوزر أو آيدي)
if arg:
    arg = arg.strip()
    # إذا رقم
    if arg.isdigit():
        try:
            target = await client.get_entity(int(arg))
            return target
        except Exception:
            pass
    # إذا ذكر مستخدم @username
    if arg.startswith("@"):
        try:
            target = await client.get_entity(arg)
            return target
        except Exception:
            pass

return None

@zedub.zed_cmd(pattern=r"تفعيل الكاشف الذكي(?:\s+(.+))?$") async def enable_smart_presence(event): """تفعيل مراقبة شخص""" if BOTLOG_CHATID in (None, 0, ""): await event.reply("خطأ: تعريف متغير BOTLOG_CHATID غير موجود. الرجاء ضبطه في إعدادات المشروع.") return

arg = event.pattern_match.group(1) if event.pattern_match else None
user_entity = await resolve_user_from_arg_or_reply(event, arg or "")
if not user_entity or not isinstance(user_entity, User):
    await event.reply("خطأ: لم أستطع العثور على المستخدم. استخدم: `.تفعيل الكاشف الذكي @username` أو رُد على رسالة الشخص.")
    return

uid = int(user_entity.id)
name = (user_entity.first_name or "") + (" " + user_entity.last_name if getattr(user_entity, "last_name", None) else "")
if not name.strip():
    name = user_entity.username or str(uid)

db = load_db()
monitored = db.setdefault("monitored", {})
if str(uid) in monitored:
    await event.reply(f"🔔 بالفعل يتم مراقبة {name} (id: {uid}).")
    return

monitored[str(uid)] = {
    "first_seen": datetime.utcnow().isoformat(),
    "last_state": None,
    "name": name,
}
save_db(db)

await event.reply(f"✅ تم تفعيل الكاشف الذكي للمستخدم: [{name}](tg://user?id={uid})\nسأرسل إشعارًا إلى مجموعة الإشعارات عند تسجيل تواجده.", parse_mode='md')

@zedub.zed_cmd(pattern=r"تعطيل الكاشف الذكي(?:\s+(.+))?$") async def disable_smart_presence(event): """إيقاف مراقبة شخص""" arg = event.pattern_match.group(1) if event.pattern_match else None user_entity = await resolve_user_from_arg_or_reply(event, arg or "") if not user_entity or not isinstance(user_entity, User): await event.reply("خطأ: لم أستطع العثور على المستخدم. استخدم: .تعطيل الكاشف الذكي @username أو رُد على رسالة الشخص.") return

uid = int(user_entity.id)
name = (user_entity.first_name or "") or user_entity.username or str(uid)

db = load_db()
monitored = db.setdefault("monitored", {})
if str(uid) not in monitored:
    await event.reply(f"ℹ️ المستخدم [{name}](tg://user?id={uid}) غير مراقب أصلاً.", parse_mode='md')
    return

monitored.pop(str(uid), None)
save_db(db)
await event.reply(f"⛔ تم إيقاف مراقبة المستخدم [{name}](tg://user?id={uid}).", parse_mode='md')

async def presence_watcher_loop(client): """حلقة تعمل في الخلفية وتتحقق من حالة المستخدمين المراقبين""" await client.connect() while True: try: db = load_db() monitored = db.get("monitored", {}) if not monitored: await asyncio.sleep(INTERVAL_SEC) continue

# نجمع اليوزر ايديز لنستدعيهم دفعة واحدة
        ids = [int(k) for k in monitored.keys()]
        for uid in ids:
            try:
                entity = await client.get_entity(uid)
            except RPCError:
                # لا يمكن جلب الكيان الآن
                await asyncio.sleep(0.5)
                continue
            except Exception:
                continue

            # حالة اليوزر: بعض الكائنات قد لا تحتوي status
            status = getattr(entity, 'status', None)
            is_online = False
            if status is not None:
                # Telethon يضع status كـ UserStatusOnline / UserStatusRecently / etc
                stname = type(status).__name__.lower()
                # اعتبارات بسيطة: إذا تضمن الاسم "online" اعتبر متصل
                if 'online' in stname:
                    is_online = True
                elif 'recently' in stname:
                    # ممكن أن نعتبر recently كـ online بحسب رغبتك — هنا لن نعتبرها متصلة
                    is_online = False
            else:
                is_online = False

            rec = monitored.get(str(uid), {})
            last = rec.get('last_state')
            name = rec.get('name') or (entity.first_name or entity.username or str(uid))

            if is_online and last != 'online':
                # تغيير إلى متصل -> أرسل إشعار
                msg = f"🔔 المستخدم الآن متصل: [{name}](tg://user?id={uid})\nالوقت: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
                try:
                    await client.send_message(BOTLOG_CHATID, msg, parse_mode='md')
                except Exception:
                    # فشل الإرسال لا يوقف الحلقة
                    pass
                rec['last_state'] = 'online'
                monitored[str(uid)] = rec
                save_db(db)

            elif (not is_online) and last == 'online':
                # تبديل من متصل إلى غير متصل -> نحدث الحالة فقط (اختياري: نرسل إشعار عند الخروج)
                rec['last_state'] = 'offline'
                monitored[str(uid)] = rec
                save_db(db)

            # لا تغيير -> تجاهل
            await asyncio.sleep(0.3)  # تخفيف الضغط بين الطلبات

    except Exception:
        # لا نريد أن تتوقف الحلقة بسبب خطأ عارض
        await asyncio.sleep(5)
    await asyncio.sleep(INTERVAL_SEC)

تسجيل المهمة عند بدء البوت

@zedub.zed_cmd(pattern=r"(?:start|boot|init)_presence_watcher$") async def _start_presence_watcher(event): """أمر داخلي لتشغيل الحلقة عند بداية التشغيل. يمكنك استدعاؤه يدوياً أو إضافته لبدء التشغيل.""" client = event.client # شغّل الحلقة بشكل غير محظور client.loop.create_task(presence_watcher_loop(client)) await event.reply("✅ تم تشغيل حلقة مراقبة الحضور (presence watcher).")

"""إذا كان في مشروعك يوجد hook لتشغيل مهام عند الإقلاع يمكنك استدعاء presence_watcher_loop(client)

مثال: عند init الرئيسي: client.loop.create_task(presence_watcher_loop(client))

"""
