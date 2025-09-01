import json
import math
import os
import random
import re
import time
import asyncio
from pathlib import Path
from uuid import uuid4
import requests
from urllib.parse import quote_plus
from telethon import Button, types, events
from telethon.errors import QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery
from youtubesearchpython import VideosSearch
import yt_dlp  

from yamenthon import zedub
from ..Config import Config
from ..helpers.functions import rand_key
from ..helpers.functions.utube import (
    download_button,
    get_yt_video_id,
    get_ytthumb,
    result_formatter,
    ytsearch_data,
)
from ..sql_helper.globals import gvarstatus
from ..core.logger import logging

LOGS = logging.getLogger(__name__)

tr = Config.COMMAND_HAND_LER
DOWNLOAD_DIR = "./ytdl_cache"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def get_thumb(name):
    url = f"https://github.com/TgCatUB/CatUserbot-Resources/blob/master/Resources/Inline/{name}?raw=true"
    return types.InputWebDocument(url=url, size=0, mime_type="image/png", attributes=[])


def ibuild_keyboard(buttons):
    keyb = []
    for btn in buttons:
        if btn[2] and keyb:
            keyb[-1].append(Button.url(btn[0], btn[1]))
        else:
            keyb.append([Button.url(btn[0], btn[1])])
    return keyb


@zedub.tgbot.on(InlineQuery)
async def inline_handler(event):
    builder = event.builder
    result = None
    query = event.text
    string = query.lower()
    query_user_id = event.query.user_id
    str_y = query.split(" ", 1)

    if query_user_id == Config.OWNER_ID or query_user_id in Config.SUDO_USERS:
        if str_y[0].lower() == "ytdl" and len(str_y) == 2:
            link = get_yt_video_id(str_y[1].strip())
            found_ = True

            if link is None:
    search = VideosSearch(str_y[1].strip(), limit=15)
    resp = (search.result()).get("result")
    if not resp:
        found_ = False
    else:
        outdata = await result_formatter(resp)
        if not outdata:
            found_ = False
        else:
            key_ = rand_key()
            ytsearch_data.store_(key_, outdata)

            first_video = outdata[0]  # ✅ تأكدنا من وجود عنصر
            buttons = [
                Button.inline(f"1 / {len(outdata)}", data=f"ytdl_next_{key_}_1"),
                Button.inline("القائمـة 📜", data=f"ytdl_listall_{key_}_1"),
                Button.inline("⬇️  تحميـل", data=f'ytdl_download_{first_video["video_id"]}_0'),
            ]
            caption = first_video["message"]
            photo = await get_ytthumb(first_video["video_id"])
            else:
                caption, buttons = await download_button(link, body=True)
                photo = await get_ytthumb(link)

            if found_:
                markup = event.client.build_reply_markup(buttons)
                photo = types.InputWebDocument(url=photo, size=0, mime_type="image/jpeg", attributes=[])
                text, msg_entities = await event.client._parse_message_text(caption, "html")

                result = types.InputBotInlineResult(
                    id=str(uuid4()),
                    type="photo",
                    title=str(link),
                    description="⬇️ اضغـط للتحميـل",
                    thumb=photo,
                    content=photo,
                    send_message=types.InputBotInlineMessageMediaAuto(
                        reply_markup=markup, message=text, entities=msg_entities
                    ),
                )
            else:
                result = builder.article(
                    title="Not Found",
                    text=f"No Results found for `{str_y[1]}`",
                    description="INVALID",
                )

            try:
                await event.answer([result] if result else None)
            except QueryIdInvalidError:
                await event.answer(
                    [
                        builder.article(
                            title="Not Found",
                            text=f"No Results found for `{str_y[1]}`",
                            description="INVALID",
                        )
                    ]
                )

        elif string == "pmpermit":
            buttons = [Button.inline(text="عـرض الخيـارات", data="show_pmpermit_options")]
            PM_PIC = gvarstatus("pmpermit_pic")
            if PM_PIC:
                CAT = [x for x in PM_PIC.split()]
                PIC = list(CAT)
                CAT_IMG = random.choice(PIC)
            else:
                CAT_IMG = None

            query = gvarstatus("pmpermit_text")
            if CAT_IMG and CAT_IMG.endswith((".jpg", ".jpeg", ".png")):
                result = builder.photo(CAT_IMG, text=query, buttons=buttons)
            elif CAT_IMG:
                result = builder.document(CAT_IMG, title="Alive cat", text=query, buttons=buttons)
            else:
                result = builder.article(title="Alive cat", text=query, buttons=buttons)

            await event.answer([result] if result else None)

    else:
        buttons = [
            (
                Button.url("قنـاة السـورس", "https://t.me/YamenThon"),
                Button.url("مطـور السـورس", "https://t.me/T_A_Tl"),
            )
        ]
        markup = event.client.build_reply_markup(buttons)
        photo = types.InputWebDocument(
            url="https://i.postimg.cc/HsBGV28T/image.jpg",
            size=0,
            mime_type="image/jpeg",
            attributes=[],
        )
        text, msg_entities = await event.client._parse_message_text(
            "𝗗𝗲𝗽𝗹𝗼𝘆 𝘆𝗼𝘂𝗿 𝗼𝘄𝗻 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉⛤.", "md"
        )
        result = types.InputBotInlineResult(
            id=str(uuid4()),
            type="photo",
            title="𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉⛤ 𓅛",
            description="روابـط التنصـيب",
            url="https://t.me/YamenThon",
            thumb=photo,
            content=photo,
            send_message=types.InputBotInlineMessageMediaAuto(
                reply_markup=markup, message=text, entities=msg_entities
            ),
        )
        await event.answer([result] if result else None)


# ✅ التحميل مع API + fallback yt_dlp
def download_with_api(video_url, output_path):
    api_err = None
    try:
        api_endpoint = "https://sii3.moayman.top/api/do.php"
        resp = requests.get(
            api_endpoint,
            params={"url": video_url},
            headers={"User-Agent": "Mozilla/5.0"},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if not data.get("links"):
            raise Exception("❌ الرد من الـ API ما فيه روابط تحميل.")

        file_url = None
        preferred_res = ("360", "480", "720")
        mp4_links = [x for x in data["links"] if (x.get("ext") or "").lower() == "mp4"]

        for r in preferred_res:
            for x in mp4_links:
                q = str(x.get("quality") or x.get("resolution") or "")
                if r in q:
                    file_url = x["url"]
                    break
            if file_url:
                break

        if not file_url and mp4_links:
            file_url = mp4_links[0]["url"]

        if not file_url:
            raise Exception("❌ ما لقيت أي رابط mp4 صالح.")

        with requests.get(file_url, stream=True, timeout=60) as file_resp:
            file_resp.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in file_resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)

    except Exception as e:
        api_err = e
        # نجرب fallback yt_dlp
        try:
            ydl_opts = {
                "format": "mp4[height<=720]/mp4",
                "outtmpl": output_path,
                "noplaylist": True,
                "quiet": True,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([video_url])
        except Exception as e2:
            raise Exception(f"❌ فشل API ({api_err}) و yt_dlp ({e2})")


@zedub.tgbot.on(events.CallbackQuery(pattern=b"ytdl_download_(.*)"))
async def ytdl_download_callback(event):
    try:
        await event.answer("🚀 يتم التحميـل من يوتيوب، الرجاء الانتظـار...", alert=True)

        data = event.data.decode("utf-8")
        video_id = data.split("_")[2]
        url = f"https://www.youtube.com/watch?v={video_id}"

        file_name = f"{uuid4()}.mp4"
        video_path = os.path.join(DOWNLOAD_DIR, file_name)

        loop = asyncio.get_running_loop()
        await loop.run_in_executor(None, download_with_api, url, video_path)

        if os.path.getsize(video_path) > 49 * 1024 * 1024:
            os.remove(video_path)
            return await event.edit("❌ الفيديو أكبر من 50MB ولا يمكن للبوت إرساله.")

        caption = f"📹 تم التحميـل من YouTube\n🔗 `{url}`"
        await event.client.send_file(event.chat_id, file=video_path, caption=caption)

        await asyncio.sleep(5)
        os.remove(video_path)

    except Exception as e:
        await event.edit(f"❌ حدث خطأ أثناء التحميل أو الإرسال:\n`{str(e)}`")
