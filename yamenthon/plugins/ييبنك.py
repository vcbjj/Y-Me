import asyncio
import random
from datetime import datetime
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)
from telethon import events

from yamenthon import zedub
from ..Config import Config
from . import mention
from ..core.managers import edit_or_reply
from ..helpers.utils import reply_id
from ..sql_helper.globals import gvarstatus

# تصميم جديد مع إيموجيات وتأثيرات
temp = """
✨ **{PING_TEXT}** ✨

┏━━━━━━━━━━━━━━┓
┃  ⚡️ **البنـك:** `{ping} مللي ثانية`
┃  🧑‍💻 **المـستخدم:** {mention}
┃  🕒 **الوقـت:** `{time}`
┗━━━━━━━━━━━━━━┛

🎉 **سـرعة الاستجـابة ممتازة** 🎉
"""

plugin_category = "utils"

@zedub.zed_cmd(pattern="بنك(?:\s|$)([\s\S]*)")
async def jokerping(event):
    reply_to_id = await reply_id(event)
    start = datetime.now()
    
    # رسالة تحميل متحركة
    loading_msg = await edit_or_reply(event, "**🔄 جارٍ قياس سرعة البنك...**")
    
    # تأثيرات تحميل
    for emoji in ["⏳", "⌛️", "⏱️"]:
        await loading_msg.edit(f"**{emoji} جارٍ التحقق من السرعة...**")
        await asyncio.sleep(0.5)
    
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    current_time = datetime.now().strftime("%H:%M:%S")
    
    # إيموجيات ديناميكية بناءً على سرعة البنك
    if ms < 200:
        ping_emoji = "🚀"
        status = "**⚡ سريع جدًا!**"
    elif ms < 500:
        ping_emoji = "⚡"
        status = "**🐆 سرعة جيدة!**"
    else:
        ping_emoji = "🐢"
        status = "**🦥 السرعة متوسطة**"
    
    EMOJI = gvarstatus("ALIVE_EMOJI") or ping_emoji
    PING_TEXT = gvarstatus("PING_TEXT") or "**⏱️ قياس سرعة البنك**"
    PING_IMG = gvarstatus("PING_PIC") or "https://telegra.ph/file/fb62d70ce09f4a78dfc86.jpg"
    HuRe_caption = gvarstatus("PING_TEMPLATE") or temp

    mention_user = f"[{event.sender.first_name}](tg://user?id={event.sender_id})"

    caption = HuRe_caption.format(
        PING_TEXT=f"{PING_TEXT} {status}",
        EMOJI=EMOJI,
        mention=mention_user,
        ping=ms,
        time=current_time
    )

    JEP = [x for x in PING_IMG.split()]
    if not JEP:
        return await edit_or_reply(event, "❌ **خطأ:** لا يوجد رابط صورة صالح")
    
    PIC = random.choice(JEP)
    try:
        # إرسال الرسالة مع تأثيرات
        await event.client.send_file(
            event.chat_id, 
            PIC, 
            caption=caption, 
            reply_to=reply_to_id
        )
        await loading_msg.edit("**✅ تم قياس السرعة بنجاح!**")
        await asyncio.sleep(1)
        await event.delete()
    except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
        await loading_msg.edit(f"""
❌ **حدث خطأ!**
{random.choice(["📛", "⚠️", "🔴"])} لا يمكن تحميل الصورة
{random.choice(["🔧", "🛠️", "⚙️"])} الرجاء تغيير الرابط باستخدام الأمر:
`.اضف_فار PING_PIC [رابط_جديد]`
""")
