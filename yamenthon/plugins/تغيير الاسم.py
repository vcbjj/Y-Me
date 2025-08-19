from ..sql_helper.globals import addgvar
from ..core.managers import edit_or_reply
from yamenthon import zedub

@zedub.zed_cmd(pattern="تغيير اسمي(?: (.*))?$")
async def set_alive_name(event):
    input_name = event.pattern_match.group(1)
    reply = await event.get_reply_message()

    if input_name:
        name = input_name.strip()
    elif reply and reply.text:
        name = reply.text.strip()
    else:
        return await edit_or_reply(event, "**✘ يجب كتابة الاسم أو الرد على رسالة تحتوي على الاسم.**")

    addgvar("ALIVE_NAME", name)
    await edit_or_reply(event, f"**✓ تم تعيين الاسم بنجاح إلى :** `{name}`")
