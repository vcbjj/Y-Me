import base64
import contextlib
import io
import os
import requests
import re

from telethon import types
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from validators.url import url

from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.functions import delete_conv
from ..helpers.utils import reply_id
from . import zedub

plugin_category = "البحث"
LOGS = logging.getLogger(__name__)

SONG_SEARCH_STRING = "<b>╮ جـارِ البحث ؏ـن الاغنيـٓه... 🎧♥️╰</b>"
SONG_NOT_FOUND = "<b>⎉╎لـم استطـع ايجـاد المطلـوب .. جرب البحث باستخـدام الامـر (.اغنيه)</b>"
SONG_SENDING_STRING = "<b>╮ جـارِ تحميـل الاغنيـٓه... 🎧♥️╰</b>"

API_URL = "https://api.dfkz.xo.je/apis/v3/download.php?url="


# 🔧 دالة البحث الجديدة التي تعمل فعليًا وتعيد أول فيديو من نتائج YouTube
async def yt_search(query: str):
    try:
        response = requests.get(
            "https://www.youtube.com/results",
            params={"search_query": query},
            timeout=10,
        )
        video_ids = re.findall(r"watch\?v=(\S{11})", response.text)
        if not video_ids:
            return None
        return f"https://www.youtube.com/watch?v={video_ids[0]}"
    except Exception:
        return None


@zedub.zed_cmd(
    pattern="بحث(320)?(?:\s|$)([\s\S]*)",
    command=("بحث", plugin_category),
    info={
        "header": "لـ تحميـل الاغـانـي مـن يـوتيـوب",
        "امـر مضـاف": {"320": "لـ البحـث عـن الاغـانـي وتحميـلهـا بـدقـه عـاليـه 320k"},
        "الاسـتخـدام": "{tr}بحث + اسـم الاغنيـه",
        "مثــال": "{tr}بحث حسين الجسمي احبك",
    },
)
async def song(event):
    reply_to_id = await reply_id(event)
    reply = await event.get_reply_message()
    query = event.pattern_match.group(2) or (reply.message if reply else None)
    if not query:
        return await edit_or_reply(event, "**⎉╎قم باضافـة الاغنيـه للامـر .. بحث + اسـم الاغنيـه**")

    zedevent = await edit_or_reply(event, SONG_SEARCH_STRING)
    video_link = await yt_search(str(query))
    if not video_link or not url(video_link):
        return await zedevent.edit(f"**⎉╎عـذراً .. لـم استطـع ايجـاد** {query}")

    await zedevent.edit(SONG_SENDING_STRING)

    try:
        api_response = requests.get(API_URL + video_link).json()
        if not api_response.get("success"):
            return await zedevent.edit("❌ فشل التحميل من API.")
        download_url = api_response.get("audio") or api_response.get("url")
        title = api_response.get("title", "اغنية")
        thumb = api_response.get("thumb")

        if not download_url:
            return await zedevent.edit("❌ لم يتم العثور على رابط التحميل الصوتي.")

        await event.client.send_file(
            event.chat_id,
            download_url,
            caption=f"**⎉╎البحث :** `{title}`",
            thumb=thumb if thumb else None,
            force_document=False,
            supports_streaming=True,
            reply_to=reply_to_id,
        )
        await zedevent.delete()
    except Exception as e:
        await zedevent.edit(f"⚠️ حدث خطأ أثناء التحميل:\n`{e}`")


@zedub.zed_cmd(
    pattern="فيديو(?:\s|$)([\s\S]*)",
    command=("فيديو", plugin_category),
    info={
        "header": "لـ تحميـل مقـاطـع الفيـديـو مـن يـوتيـوب",
        "الاسـتخـدام": "{tr}فيديو + اسـم المقطـع",
        "مثــال": "{tr}فيديو حالات واتس",
    },
)
async def vsong(event):
    reply_to_id = await reply_id(event)
    reply = await event.get_reply_message()
    query = event.pattern_match.group(1) or (reply.message if reply else None)
    if not query:
        return await edit_or_reply(event, "**⎉╎قم باضافـة الاغنيـه للامـر .. فيديو + اسـم الفيديـو**")

    zedevent = await edit_or_reply(event, "**╮ جـارِ البحث ؏ـن الفيديـو... 🎧♥️╰**")
    video_link = await yt_search(str(query))
    if not video_link or not url(video_link):
        return await zedevent.edit(f"**⎉╎عـذراً .. لـم استطـع ايجـاد** {query}")

    await zedevent.edit("**╮ جـارِ تحميـل الفيديـو... 🎧♥️╰**")

    try:
        api_response = requests.get(API_URL + video_link).json()
        if not api_response.get("success"):
            return await zedevent.edit("❌ فشل التحميل من API.")
        download_url = api_response.get("video") or api_response.get("url")
        title = api_response.get("title", "فيديو")
        thumb = api_response.get("thumb")

        if not download_url:
            return await zedevent.edit("❌ لم يتم العثور على رابط التحميل الفيديو.")

        await event.client.send_file(
            event.chat_id,
            download_url,
            caption=f"**⎉╎البحث :** `{title}`",
            thumb=thumb if thumb else None,
            supports_streaming=True,
            reply_to=reply_to_id,
        )
        await zedevent.delete()
    except Exception as e:
        await zedevent.edit(f"⚠️ حدث خطأ أثناء التحميل:\n`{e}`")
