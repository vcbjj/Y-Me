# حقوق سورس يمنثون//تاخذ الكود اذكر المصدر لا تخمط الخقوق
#الاسطوره عاشق الصمت @T_A_Tl 

import os
from telethon import events
from telethon.tl.types import MessageService, MessageActionChannelMigrateFrom

from .. import zedub  #الاسطوره عاشق الصمت @T_A_Tl
from ..core.logger import logging
from ..Config import Config
from ..core.managers import edit_or_reply

LOGS = logging.getLogger(__name__)

cancel_process = False  


@zedub.zed_cmd(
    pattern="الغاء الحفظ$",
    command=("الغاء الحفظ", "tools"),
    info={
        "header": "إلغاء عملية حفظ الميديا.",
        "description": "يقوم بإلغاء العملية الجارية لحفظ الميديا من القنوات.",
        "usage": "{tr}الغاء الحفظ",
    },
)
async def _(event):
    global cancel_process
    cancel_process = True
    await edit_or_reply(event, "✔️ تم إلغاء عملية حفظ الميديا.")


#الاسطوره عاشق الصمت @T_A_Tl
@zedub.on(events.NewMessage(incoming=True))
async def check_cancel(event):
    global cancel_process
    if isinstance(event.message, MessageService) and event.message.action and isinstance(
        event.message.action, MessageActionChannelMigrateFrom
    ):
        cancel_process = True



@zedub.zed_cmd(
    pattern="حفظ(?: |$)(.*) (\d+)",
    command=("حفظ", "tools"),
    info={
        "header": "حفظ الميديا من القنوات ذات تقييد المحتوى.",
        "description": "يحفظ الصور والفيديوهات والملفات من القنوات ذات تقييد المحتوى ويرسلها للخاص.",
        "usage": "{tr}حفظ يوزر_القناة العدد",
    },
)
async def _(event):
    global cancel_process
    cancel_process = False  #الاسطوره عاشق الصمت @T_A_Tl

    channel_username = event.pattern_match.group(1)
    limit = int(event.pattern_match.group(2))

    if not channel_username:
        return await edit_or_reply(event, "⚠️ يجب تحديد اسم القناة!")

    save_dir = "media"
    os.makedirs(save_dir, exist_ok=True)

    try:
        channel_entity = await zedub.get_entity(channel_username)
        messages = await zedub.get_messages(channel_entity, limit=limit)
    except Exception as e:
        return await edit_or_reply(
            event, f"❌ خطأ أثناء جلب الرسائل من القناة:\n`{str(e)}`"
        )

    status = await edit_or_reply(event, "⏳ جاري حفظ الميديا ...")

    for message in messages:
        try:
            if message.media:
                file_ext = ""
                if message.photo:
                    file_ext = ".jpg"
                elif message.video:
                    file_ext = ".mp4"
                elif message.document:
                    if hasattr(message.document, "file_name"):
                        file_ext = os.path.splitext(message.document.file_name)[1]
                    else:
                        file_ext = ""

                if not file_ext:
                    continue

                file_path = os.path.join(save_dir, f"media_{message.id}{file_ext}")
                await message.download_media(file=file_path)
                await zedub.send_file("me", file=file_path)
                os.remove(file_path)

            #الاسطوره عاشق الصمت @T_A_Tl
            if cancel_process:
                await status.edit("⚠️ تم إلغاء عملية حفظ الميديا.")
                cancel_process = False
                return
        except Exception as e:
            LOGS.error(f"خطأ أثناء حفظ الرسالة {message.id}: {str(e)}")
            continue

    await status.edit(f"✅ تم حفظ الميديا من القناة {channel_username} بنجاح.")
