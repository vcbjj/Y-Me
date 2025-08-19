import random
import re
import time
from datetime import datetime
from platform import python_version

import requests
from telethon import version
from telethon.errors.rpcerrorlist import (
    MediaEmptyError,
    WebpageCurlFailedError,
    WebpageMediaEmptyError,
)
from telethon.events import CallbackQuery

from yamenthon import StartTime, zedub, zedversion

from ..Config import Config
from ..core.managers import edit_or_reply
from ..helpers.functions import zedalive, check_data_base_heal_th, get_readable_time
from ..helpers.utils import reply_id
from ..sql_helper.globals import gvarstatus
from . import mention

plugin_category = "العروض"
STATS = gvarstatus("Z_STATS") or "فحص"


@zedub.zed_cmd(pattern=f"{STATS}$")
async def amireallyalive(event):
    reply_to_id = await reply_id(event)
    uptime = await get_readable_time((time.time() - StartTime))
    start = datetime.now()
    zedevent = await edit_or_reply(event, "**⎆┊جـاري .. فحـص السورس الخـاص بك**")
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    _, check_sgnirts = check_data_base_heal_th()

    Z_EMOJI = gvarstatus("ALIVE_EMOJI") or "❈┊"
    ALIVE_TEXT = gvarstatus("ALIVE_TEXT") or "**〆ᴅᴇᴠᴇʟᴏᴘᴇʀ ᴀsʜᴇǫ ᴀʟsᴀᴍᴛ〆**"
    ZED_IMG = gvarstatus("ALIVE_PIC")
    zed_caption = gvarstatus("ALIVE_TEMPLATE") or zed_temp

    # ✅ : اسم ثابت من قاعدة البيانات وربطه بمعرف المالك
    USERID = zedub.uid if Config.OWNER_ID == 0 else Config.OWNER_ID
    ALIVE_NAME = gvarstatus("ALIVE_NAME") or "-"
    mention = f"[{ALIVE_NAME}](tg://user?id={USERID})"

    caption = zed_caption.format(
        ALIVE_TEXT=ALIVE_TEXT,
        Z_EMOJI=Z_EMOJI,
        mention=mention,
        uptime=uptime,
        telever=version.__version__,
        tepver=zedversion,
        pyver=python_version(),
        dbhealth=check_sgnirts,
        ping=ms,
    )

    if ZED_IMG:
        ZED = [x for x in ZED_IMG.split()]
        PIC = random.choice(ZED)
        try:
            await event.client.send_file(
                event.chat_id, PIC, caption=caption, reply_to=reply_to_id
            )
            await zedevent.delete()
        except (WebpageMediaEmptyError, MediaEmptyError, WebpageCurlFailedError):
            return await edit_or_reply(
                zedevent,
                f"**⌔∮ عـذراً عليـك الـرد ع صـوره او ميـديـا  ⪼  `.اضف صورة الفحص` <بالرد ع الصـوره او الميـديـا> **",
            )
    else:
        await edit_or_reply(
            zedevent,
            caption,
        )


zed_temp = """{ALIVE_TEXT}
┏───────────────┓
│ ◉ ʙᴏᴛ ʏᴀᴍᴇɴᴛʜᴏɴ ɪs ʀᴜɴɴɪɴɢ ɴᴏᴡ
┣───────────────┫
**{Z_EMOJI} ᴅᴀᴛᴀʙᴀsᴇ ᴡᴏʀᴋɪɴɢ sᴜᴄᴄᴇssғᴜʟʟʏ
**{Z_EMOJI} ● ᴛᴇʟᴇᴛʜᴏɴ ʀᴇʟᴇᴀsᴇ➪ `{telever}`
**{Z_EMOJI} ● ʏᴀᴍᴇɴᴛʜᴏɴ ➪** `{tepver}`
**{Z_EMOJI} ● ᴘʏᴛʜᴏɴ ➪** `{pyver}`
**{Z_EMOJI} ● ᴜᴘ ᴛɪᴍᴇ ➪** `{uptime}`
**{Z_EMOJI} ● ɴᴀᴍᴇ ➪:** {mention}
**{Z_EMOJI} ● ᴍʏ ᴄʜᴀɴɴᴇʟ ➪ **[ᴄʟɪᴄᴋ ʜᴇʀᴇ](https://t.me/YamenThon)
┗───────────────┛"""


@zedub.zed_cmd(
    pattern="الفحص$",
    command=("الفحص", plugin_category),
    info={
        "header": "- لـ التحـقق من ان السورس يعمـل بنجـاح .. بخـاصيـة الانـلايـن ✓",
        "الاسـتخـدام": [
            "{tr}الفحص",
        ],
    },
)
async def amireallyialive(event):
    "A kind of showing bot details by your inline bot"
    reply_to_id = await reply_id(event)
    Z_EMOJI = gvarstatus("ALIVE_EMOJI") or "❈┊"
    zed_caption = "** سورس  يـــمنثون 𝙔𝘼𝙈  يعمـل .. بنجـاح ☑️ 𓆩 **\n"
    zed_caption += f"**{Z_EMOJI} إصـدار التـيليثون :** `{version.__version__}\n`"
    zed_caption += f"**{Z_EMOJI} إصـدار يـــمنثون :** `{zedversion}`\n"
    zed_caption += f"**{Z_EMOJI} إصـدار البـايثون :** `{python_version()}\n`"
    zed_caption += f"**{Z_EMOJI} المسـتخدم :** {mention}\n"
    results = await event.client.inline_query(Config.TG_BOT_USERNAME, zed_caption)
    await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
    await event.delete()


@zedub.tgbot.on(CallbackQuery(data=re.compile(b"stats")))
async def on_plug_in_callback_query_handler(event):
    statstext = await zedalive(StartTime)
    await event.answer(statstext, cache_time=0, alert=True)
