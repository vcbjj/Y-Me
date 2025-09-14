import asyncio
import json
import os

from . import zedub
from ..core.managers import edit_delete, edit_or_reply

SUPER_FILE = "data/super.json"

# تحميل الداتا من ملف
def load_super():
    if not os.path.exists(SUPER_FILE):
        return {"groups": [], "running": {}}
    with open(SUPER_FILE, "r") as f:
        return json.load(f)

# حفظ الداتا في ملف
def save_super(data):
    with open(SUPER_FILE, "w") as f:
        json.dump(data, f, indent=4)


# إضافة مجموعة
@zedub.zed_cmd(pattern="ضع سوبر$")
async def add_super(event):
    data = load_super()
    chat_id = event.chat_id

    if chat_id not in data["groups"]:
        data["groups"].append(chat_id)
        save_super(data)
        await edit_delete(event, "**- تم إضافة المجموعة إلى قائمة السوبر ✓**")
    else:
        await edit_delete(event, "**- المجموعـة مضافـة مسبقاً ✓**")


# حذف مجموعة
@zedub.zed_cmd(pattern="حذف سوبر$")
async def del_super(event):
    data = load_super()
    chat_id = event.chat_id

    if chat_id in data["groups"]:
        data["groups"].remove(chat_id)
        save_super(data)
        await edit_delete(event, "**- تم حذف المجموعة من قائمة السوبر ✓**")
    else:
        await edit_delete(event, "**- المجموعـة غيـر مضافـة للقائمـة ✓**")


# عرض السوبرات
@zedub.zed_cmd(pattern="السوبرات$")
async def list_super(event):
    data = load_super()
    if not data["groups"]:
        return await edit_or_reply(event, "**- لا توجد أي مجموعـات سوبر ✓**")

    txt = "「❖╎قائمـة مجموعـات السوبـر ♾」\n\n"
    for i, g in enumerate(data["groups"], start=1):
        txt += f"{i} ➺ `{g}`\n"

    await edit_or_reply(event, txt)


# حذف كل السوبرات
@zedub.zed_cmd(pattern="حذف السوبرات$")
async def clear_super(event):
    data = {"groups": [], "running": {}}
    save_super(data)
    await edit_delete(event, "**- تم تصفير قائمـة السوبـرات ✓**")


# النشر العام التكراري
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
    if not data["groups"]:
        return await edit_or_reply(event, "**- لا توجد مجموعـات سوبر مضافة ✓**")

    msg = await edit_or_reply(event, f"**- جـارِ النشـر التكـراري لـ {count} مـرة / كل {delay} ثانية ✓**")

    for g in data["groups"]:
        data["running"][str(g)] = True
    save_super(data)

    for i in range(count):
        data = load_super()
        for g in data["groups"]:
            if not data["running"].get(str(g), False):
                continue
            try:
                await reply.forward_to(int(g))
            except:
                pass
        await asyncio.sleep(delay)

    await msg.edit("**- انتهى النشـر التكراري ✓**")


# ايقاف سوبر لمجموعة واحدة
@zedub.zed_cmd(pattern="ايقاف سوبر$")
async def stop_super(event):
    chat_id = str(event.chat_id)
    data = load_super()
    if chat_id in data["running"]:
        data["running"][chat_id] = False
        save_super(data)
        await edit_delete(event, "**- تم إيقاف النشـر عن هذه المجموعة ✓**")
    else:
        await edit_delete(event, "**- لا يوجد نشـر فعال هنا ✓**")


# ايقاف جميع السوبرات
@zedub.zed_cmd(pattern="ايقاف السوبرات$")
async def stop_all_super(event):
    data = load_super()
    for g in data["groups"]:
        data["running"][str(g)] = False
    save_super(data)
    await edit_delete(event, "**- تم إيقاف النشـر عن جميع المجموعـات ✓**")
