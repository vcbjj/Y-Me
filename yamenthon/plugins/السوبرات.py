import asyncio
import json
import os

from . import zedub
from ..core.managers import edit_delete, edit_or_reply

# مسار ملف البيانات
DATA_DIR = "data"
SUPER_FILE = os.path.join(DATA_DIR, "super.json")

# تأكد من وجود المجلد
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR, exist_ok=True)


def load_super():
    if not os.path.exists(SUPER_FILE):
        return {"groups": [], "running": {}}
    with open(SUPER_FILE, "r") as f:
        try:
            return json.load(f)
        except Exception:
            return {"groups": [], "running": {}}


def save_super(data):
    with open(SUPER_FILE, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


# مساعد لتحويل أي مدخل قديم (رقم) إلى شكل موحد { "id": ..., "note": "" }
def normalize_groups(data):
    groups = []
    for g in data.get("groups", []):
        if isinstance(g, dict):
            gid = g.get("id")
            note = g.get("note", "")
        else:
            gid = g
            note = ""
        groups.append({"id": int(gid), "note": note})
    return groups


def save_normalized_groups(data, groups_list):
    data["groups"] = groups_list
    save_super(data)


# ==========================
# أمر: اضف سوبر
# ==========================
@zedub.zed_cmd(pattern="ضع سوبر$")
async def add_super(event):
    chat_id = int(event.chat_id)
    data = load_super()
    groups = normalize_groups(data)

    # هل المجموعة موجودة؟
    if any(int(g["id"]) == chat_id for g in groups):
        return await edit_delete(event, "**- المجموعـة مضافـة مسبقاً ✓**")

    # حاول قراءة نص الإشعار إذا كان الأمر مُنفذ بالرد على رسالة
    note = ""
    try:
        reply = await event.get_reply_message()
    except Exception:
        reply = None

    if reply:
        # آمن: لا نصل إلى reply.text إلا لو موجود
        if getattr(reply, "text", None):
            note = reply.text
        elif getattr(reply, "message", None):
            note = reply.message
        elif getattr(reply, "media", None):
            note = "<وسيط (صورة/فيديو/صوت)>"

        # قص النص لو طويل جدًا للعرض
        if note and len(note) > 400:
            note = note[:400] + " ..."

    # أضف المجموعة بشكل موحد
    groups.append({"id": chat_id, "note": note})
    save_normalized_groups(data, groups)

    msg = "**- تم إضافة المجموعة إلى قائمة السوبر ✓**"
    if note:
        msg += f"\n- نـص الإشعـار المحفوظ: `{note}`"
    await edit_delete(event, msg)


# ==========================
# أمر: حذف سوبر
# ==========================
@zedub.zed_cmd(pattern="حذف سوبر$")
async def del_super(event):
    chat_id = int(event.chat_id)
    data = load_super()
    groups = normalize_groups(data)

    new_groups = [g for g in groups if int(g["id"]) != chat_id]
    if len(new_groups) == len(groups):
        return await edit_delete(event, "**- المجموعـة غيـر مضافـة للقائمـة ✓**")

    save_normalized_groups(data, new_groups)
    await edit_delete(event, "**- تم حذف المجموعة من قائمة السوبر ✓**")


# ==========================
# أمر: السوبرات (عرض)
# ==========================
@zedub.zed_cmd(pattern="السوبرات$")
async def list_super(event):
    data = load_super()
    groups = normalize_groups(data)

    if not groups:
        return await edit_or_reply(event, "**- لا توجد أي مجموعـات سوبر ✓**")

    txt = "「❖╎قائمـة مجموعـات السوبـر ♾」\n\n"
    for i, g in enumerate(groups, start=1):
        display_note = f" — {g['note']}" if g.get("note") else ""
        txt += f"{i} ➺ `{g['id']}`{display_note}\n"

    await edit_or_reply(event, txt)


# ==========================
# أمر: حذف السوبرات (تصفير)
# ==========================
@zedub.zed_cmd(pattern="حذف السوبرات$")
async def clear_super(event):
    data = {"groups": [], "running": {}}
    save_super(data)
    await edit_delete(event, "**- تم تصفير قائمـة السوبـرات ✓**")


# ==========================
# أمر: سوبر (النشر التكراري)
# صيغة: .سوبر <ثواني> <مرات> (بالرد على رسالة/ميديا)
# ==========================
@zedub.zed_cmd(pattern="سوبر(?: |$)(.*)")
async def super_spam(event):
    if not event.is_reply:
        return await edit_or_reply(event, "**- بالـرد ع رسـالة او ميديـا ✓**")

    reply = await event.get_reply_message()
    args = event.pattern_match.group(1).split()
    if len(args) < 2:
        return await edit_or_reply(event, "**- صيغة الامر: .سوبر + ثواني + مرات ✓**")

    try:
        delay = int(args[0])
        count = int(args[1])
    except:
        return await edit_or_reply(event, "**- يجب كتابة أرقام صحيحة ✓**")

    data = load_super()
    groups = normalize_groups(data)
    if not groups:
        return await edit_or_reply(event, "**- لا توجد مجموعـات سوبر مضافة ✓**")

    status_msg = await edit_or_reply(event, f"**- جـارِ النشـر التكـراري لـ {count} مـرة / كل {delay} ثانية ✓**")

    # علّم المجموعات بأنها تعمل
    for g in groups:
        data["running"][str(g["id"])] = True
    save_super(data)

    for i in range(count):
        data = load_super()
        groups = normalize_groups(data)
        for g in groups:
            if not data["running"].get(str(g["id"]), False):
                continue
            try:
                await reply.forward_to(int(g["id"]))
            except Exception:
                # تجاهل الأخطاء لكل مجموعة (مثلاً خروج البوت، حظر، إلخ)
                pass
        await asyncio.sleep(delay)

    await status_msg.edit("**- انتهى النشـر التكراري ✓**")


# ==========================
# أمر: ايقاف سوبر (في المجموعة الحالية)
# ==========================
@zedub.zed_cmd(pattern="ايقاف سوبر$")
async def stop_super(event):
    chat_id = str(event.chat_id)
    data = load_super()

    if data.get("running", {}).get(chat_id) is None:
        # إذا لم توجد علامة تشغيل للمجموعة، اعتبرها غير مفعلة
        data.setdefault("running", {})[chat_id] = False
        save_super(data)
        return await edit_delete(event, "**- لا يوجد نشـر فعال هنا ✓**")

    data["running"][chat_id] = False
    save_super(data)
    await edit_delete(event, "**- تم إيقاف النشـر عن هذه المجموعة ✓**")


# ==========================
# أمر: ايقاف السوبرات (إيقاف الكل)
# ==========================
@zedub.zed_cmd(pattern="ايقاف السوبرات$")
async def stop_all_super(event):
    data = load_super()
    groups = normalize_groups(data)
    for g in groups:
        data.setdefault("running", {})[str(g["id"])] = False
    save_super(data)
    await edit_delete(event, "**- تم إيقاف النشـر عن جميع المجموعـات ✓**")
