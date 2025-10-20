""" Download Youtube Video / Audio in a User friendly interface """
# --------------------------- #
#   Modded ytdl by code-rgb   #
# --------------------------- #

import asyncio
import glob
import io
import requests
import os
import re
from pathlib import Path
from time import time

import ujson
from telethon import Button, types
from telethon.errors import BotResponseTimeoutError
from telethon.events import CallbackQuery
from telethon.utils import get_attributes
from wget import download

from yamenthon import zedub

from ..Config import Config
from ..core import check_owner, pool
from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import post_to_telegraph, progress, reply_id
from ..helpers.functions.utube import (
    _mp3Dl,
    _tubeDl,
    download_button,
    get_choice_by_id,
    get_ytthumb,
    yt_search_btns,
)
from ..plugins import BOTLOG_CHATID

LOGS = logging.getLogger(__name__)
BASE_YT_URL = "https://www.youtube.com/watch?v="
YOUTUBE_REGEX = re.compile(
    r"(?:youtube\.com|youtu\.be)/(?:[\w-]+\?v=|embed/|v/|shorts/)?([\w-]{11})"
)
PATH = "./yamenthon/cache/ytsearch.json"
plugin_category = "البوت"


@zedub.zed_cmd(
    pattern="يوت(?:\s|$)([\s\S]*)",
    command=("يوت", plugin_category),
    info={
        "header": "ytdl with inline buttons.",
        "description": "To search and download youtube videos by inline buttons.",
        "usage": "{tr}iytdl [URL / Text] or [Reply to URL / Text]",
    },
)
async def iytdl_inline(event):
    "ytdl with inline buttons."
    reply = await event.get_reply_message()
    reply_to_id = await reply_id(event)
    input_str = event.pattern_match.group(1)
    input_url = None
    if input_str:
        input_url = (input_str).strip()
    elif reply and reply.text:
        input_url = (reply.text).strip()
    if not input_url:
        return await edit_delete(event, "**- بالـرد ع رابـط او كتـابة نص مـع الامـر**")
    zedevent = await edit_or_reply(event, f"**⌔╎جـارِ البحث في اليوتيوب عـن:** `'{input_url}'`")
    flag = True
    cout = 0
    results = None
    while flag:
        try:
            results = await event.client.inline_query(
                Config.TG_BOT_USERNAME, f"ytdl {input_url}"
            )
            flag = False
        except BotResponseTimeoutError:
            await asyncio.sleep(2)
        cout += 1
        if cout > 5:
            flag = False
    if results:
        await zedevent.delete()
        await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
    else:
        await zedevent.edit("**⌔╎عـذراً .. لم اجد اي نتائـج**")


@zedub.tgbot.on(
    CallbackQuery(
        data=re.compile(b"^ytdl_download_(.*)_([\d]+|mkv|mp4|mp3)(?:_(a|v))?")
    )
)
@check_owner
async def ytdl_download_callback(c_q: CallbackQuery):
    yt_code = (
        str(c_q.pattern_match.group(1).decode("UTF-8"))
        if c_q.pattern_match.group(1) is not None
        else None
    )
    choice_id = (
        str(c_q.pattern_match.group(2).decode("UTF-8"))
        if c_q.pattern_match.group(2) is not None
        else None
    )
    downtype = (
        str(c_q.pattern_match.group(3).decode("UTF-8"))
        if c_q.pattern_match.group(3) is not None
        else None
    )
    startTime = time()
    media_type = "فيديو" if downtype == "v" else "مقطع صوتي"
    disp_str = choice_id if not str(choice_id).isdigit() else f"id {choice_id}"

    yt_url = f"https://www.youtube.com/watch?v={yt_code}"

    await c_q.answer(f"جـارِ تحميل {media_type} عبر الـ API ...", alert=True)
    upload_msg = await c_q.client.send_message(BOTLOG_CHATID, f"⌔╎جـارِ تحميـل {media_type} ...")

    api_url = f"https://api.dfkz.xo.je/apis/v3/download.php?url={yt_url}"
    try:
        import aiohttp
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                if resp.status != 200:
                    return await upload_msg.edit("❌ فشل الاتصال بالـ API.")
                data = await resp.json()
    except Exception as e:
        return await upload_msg.edit(f"⚠️ خطأ أثناء الاتصال بالـ API:\n{e}")

    # تحقق من وجود رابط التحميل
    download_url = None
    title = data.get("title") or "youtube_video"
    thumb = data.get("thumbnail")

    # نحاول استخراج رابط الصوت أو الفيديو
    if "audio" in data:
        download_url = data["audio"].get("url") or data["audio"].get("download_url")
    elif "video" in data:
        download_url = data["video"].get("url") or data["video"].get("download_url")

    if not download_url:
        return await upload_msg.edit("❌ لم يتم العثور على رابط التحميل في استجابة الـ API.")

    # تحميل الملف عبر ffmpeg (تحويل إلى صوت إذا لزم)
    temp_path = f"{Config.TEMP_DIR}/{startTime}"
    os.makedirs(temp_path, exist_ok=True)

    file_path = os.path.join(temp_path, f"{title}.mp3" if downtype == "a" else f"{title}.mp4")

    cmd = [
        "ffmpeg",
        "-i", download_url,
        "-vn" if downtype == "a" else "-c", "copy",
        file_path,
        "-y"
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    await proc.communicate()

    if not os.path.exists(file_path):
        return await upload_msg.edit("⚠️ فشل التحويل أو التحميل عبر ffmpeg.")

    # رفع الفيديو أو الصوت إلى تيليجرام
    thumb_file = None
    if thumb:
        thumb_file = os.path.join(temp_path, "thumb.jpg")
        try:
            import wget
            wget.download(thumb, thumb_file)
        except Exception:
            thumb_file = None

    caption = f"<b>⌔╎الاسـم :</b> <code>{os.path.basename(file_path)}</code>\n🎧 <b>النوع:</b> {media_type}"
    await c_q.client.send_file(
        BOTLOG_CHATID,
        file=file_path,
        thumb=thumb_file,
        caption=caption,
        parse_mode="html",
    )

    await upload_msg.delete()
    await c_q.edit(
        f"<b>✅ تم تحميل ورفع {media_type} بنجاح عبر الـ API</b>",
        parse_mode="html"
    )


@zedub.tgbot.on(
    CallbackQuery(data=re.compile(b"^ytdl_(listall|back|next|detail)_([a-z0-9]+)_(.*)"))
)
@check_owner
async def ytdl_callback(c_q: CallbackQuery):
    choosen_btn = (
        str(c_q.pattern_match.group(1).decode("UTF-8"))
        if c_q.pattern_match.group(1) is not None
        else None
    )
    data_key = (
        str(c_q.pattern_match.group(2).decode("UTF-8"))
        if c_q.pattern_match.group(2) is not None
        else None
    )
    page = (
        str(c_q.pattern_match.group(3).decode("UTF-8"))
        if c_q.pattern_match.group(3) is not None
        else None
    )
    if not os.path.exists(PATH):
        return await c_q.answer(
            "عملية البحث غير دقيقة يرجى اختيار عنوان صحيح وحاول مجددا",
            alert=True,
        )
    with open(PATH) as f:
        view_data = ujson.load(f)
    search_data = view_data.get(data_key)
    total = len(search_data) if search_data is not None else 0
    if total == 0:
        return await c_q.answer(
            "يرجى البحث مرة اخرى لم يتم العثور على نتائج دقيقة", alert=True
        )
    if choosen_btn == "back":
        index = int(page) - 1
        del_back = index == 1
        await c_q.answer()
        back_vid = search_data.get(str(index))
        await c_q.edit(
            text=back_vid.get("message"),
            file=await get_ytthumb(back_vid.get("video_id")),
            buttons=yt_search_btns(
                del_back=del_back,
                data_key=data_key,
                page=index,
                vid=back_vid.get("video_id"),
                total=total,
            ),
            parse_mode="html",
        )
    elif choosen_btn == "next":
        index = int(page) + 1
        if index > total:
            return await c_q.answer("هذا كل ما يمكنني عرضه", alert=True)
        await c_q.answer()
        front_vid = search_data.get(str(index))
        await c_q.edit(
            text=front_vid.get("message"),
            file=await get_ytthumb(front_vid.get("video_id")),
            buttons=yt_search_btns(
                data_key=data_key,
                page=index,
                vid=front_vid.get("video_id"),
                total=total,
            ),
            parse_mode="html",
        )
    elif choosen_btn == "listall":
        await c_q.answer("العرض تغير الى :  📜  اللستة", alert=False)
        list_res = "".join(
            search_data.get(vid_s).get("list_view") for vid_s in search_data
        )

        telegraph = await post_to_telegraph(
            f"يتم عرض {total} من الفيديوهات على اليوتيوب حسب طلبك ...",
            list_res,
        )
        await c_q.edit(
            file=await get_ytthumb(search_data.get("1").get("video_id")),
            buttons=[
                (
                    Button.url(
                        "↗️  اضغط للتحميل",
                        url=telegraph,
                    )
                ),
                (
                    Button.inline(
                        "📰  عرض التفاصيل",
                        data=f"ytdl_detail_{data_key}_{page}",
                    )
                ),
            ],
        )
    else:  # Detailed
        index = 1
        await c_q.answer("تم تغيير العرض الى:  📰  التفاصيل", alert=False)
        first = search_data.get(str(index))
        await c_q.edit(
            text=first.get("message"),
            file=await get_ytthumb(first.get("video_id")),
            buttons=yt_search_btns(
                del_back=True,
                data_key=data_key,
                page=index,
                vid=first.get("video_id"),
                total=total,
            ),
            parse_mode="html",
        )
