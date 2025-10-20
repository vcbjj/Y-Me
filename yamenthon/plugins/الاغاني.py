import base64
import contextlib
import io
import os
import requests
import re
import json

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


def extract_first_link(api_response, file_type="audio"):
    """استخراج أول رابط صالح من رد الـ API"""
    links = api_response.get("links", [])
    for link in links:
        if link.get("type") == file_type and link.get("url"):
            return link
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

    if not video_link:
        return await zedevent.edit(f"**⎉╎عـذراً .. لـم استطـع ايجـاد** {query}\n\n⚠️ **نتائج البحث:** لا يوجد أي فيديو.")
    else:
        await zedevent.edit(f"**🔍 تم إيجاد الفيديو:**\n`{video_link}`\n\nجاري التحميل...")

    if not url(video_link):
        return await zedevent.edit(f"**⎉╎الرابط غير صالح:** {video_link}")

    await zedevent.edit(SONG_SENDING_STRING)

    try:
        api_response = requests.get(API_URL + video_link, timeout=20).json()
        if not api_response.get("success"):
            return await zedevent.edit("❌ فشل التحميل من API.")

        title = api_response.get("title", "اغنية")
        thumb = api_response.get("thumb")

        # 🔍 استخراج أول رابط صوتي صالح
        link_info = extract_first_link(api_response, "audio") or extract_first_link(api_response, "video")
        if not link_info:
            return await zedevent.edit("❌ لم يتم العثور على رابط التحميل الصوتي.")

        download_url = link_info.get("url")
        quality = link_info.get("quality", "غير معروف")

        await zedevent.edit(f"📥 **جاري تحميل الاغنية:**\n🎵 {title}\n💡 الجودة: {quality}")

        # تحميل مؤقت
        file_path = f"/tmp/{title}.mp3"
        with open(file_path, "wb") as f:
            f.write(requests.get(download_url, timeout=30).content)

        await event.client.send_file(
            event.chat_id,
            file=file_path,
            caption=f"**⎉╎البحث :** `{title}`",
            thumb=thumb if thumb else None,
            supports_streaming=True,
            reply_to=reply_to_id,
        )

        os.remove(file_path)
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

    if not video_link:
        return await zedevent.edit(f"**⎉╎عـذراً .. لـم استطـع ايجـاد** {query}\n\n⚠️ **نتائج البحث:** لا يوجد أي فيديو.")
    else:
        await zedevent.edit(f"**🔍 تم إيجاد الفيديو:**\n`{video_link}`\n\nجاري التحميل...")

    if not url(video_link):
        return await zedevent.edit(f"**⎉╎الرابط غير صالح:** {video_link}")

    await zedevent.edit("**╮ جـارِ تحميـل الفيديـو... 🎧♥️╰**")

    try:
        api_response = requests.get(API_URL + video_link, timeout=20).json()
        if not api_response.get("success"):
            return await zedevent.edit("❌ فشل التحميل من API.")

        title = api_response.get("title", "فيديو")
        thumb = api_response.get("thumb")

        # 🔍 استخراج أول رابط فيديو صالح
        link_info = extract_first_link(api_response, "video") or extract_first_link(api_response, "audio")
        if not link_info:
            return await zedevent.edit("❌ لم يتم العثور على رابط التحميل الفيديو.")

        download_url = link_info.get("url")
        quality = link_info.get("quality", "غير معروف")

        await zedevent.edit(f"📥 **جاري تحميل الفيديو:**\n🎬 {title}\n💡 الجودة: {quality}")

        file_path = f"/tmp/{title}.mp4"
        with open(file_path, "wb") as f:
            f.write(requests.get(download_url, timeout=30).content)

        await event.client.send_file(
            event.chat_id,
            file=file_path,
            caption=f"**⎉╎البحث :** `{title}`",
            thumb=thumb if thumb else None,
            supports_streaming=True,
            reply_to=reply_to_id,
        )

        os.remove(file_path)
        await zedevent.delete()

    except Exception as e:
        await zedevent.edit(f"⚠️ حدث خطأ أثناء التحميل:\n`{e}`")
