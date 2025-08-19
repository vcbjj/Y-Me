import os
import requests
from telethon import types
from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..helpers.utils import reply_id
from . import zedub

plugin_category = "البحث"
LOGS = logging.getLogger(__name__)

API_BASE = "https://apisyu.com/api/yt"
# الصيغة: /mp3?url=... أو /mp4?url=...

@zedub.zed_cmd(
    pattern="(?:بحث|اغنيه)(?:\s|$)([\s\S]*)",
    command=("بحث", plugin_category),
    info={
        "header": "تحميل أغاني من يوتيوب عبر API خارجي",
        "الاستخدام": "{tr}بحث + رابط أو اسم الأغنية",
        "مثال": "{tr}بحث حسين الجسمي احبك",
    },
)
async def yt_mp3_api(event):
    reply_to_id = await reply_id(event)
    query = event.pattern_match.group(1)
    if not query:
        return await edit_or_reply(event, "**⚠️ الرجاء كتابة اسم الأغنية أو الرابط.**")

    zedevent = await edit_or_reply(event, "🎵 **جاري التحميل من يوتيوب...**")

    # البحث عن رابط الفيديو إن لم يكن رابط مباشر
    if not query.startswith("http"):
        search_url = f"https://apisyu.com/api/yt/search?query={query}"
        search_res = requests.get(search_url).json()
        if not search_res or "data" not in search_res or not search_res["data"]:
            return await zedevent.edit("❌ لم أجد نتائج للبحث.")
        video_url = search_res["data"][0]["url"]
    else:
        video_url = query

    try:
        # جلب رابط mp3
        res = requests.get(f"{API_BASE}/mp3", params={"url": video_url}).json()
        if "url" not in res:
            return await zedevent.edit("❌ حدث خطأ أثناء جلب رابط التحميل.")

        mp3_link = res["url"]
        title = res.get("title", "أغنية من يوتيوب")
        thumb = res.get("thumbnail")

        await event.client.send_file(
            event.chat_id,
            mp3_link,
            caption=f"🎶 **العنوان:** {title}",
            thumb=thumb if thumb else None,
            reply_to=reply_to_id,
        )
        await zedevent.delete()
    except Exception as e:
        LOGS.error(str(e))
        await zedevent.edit("❌ فشل التحميل من API.")

@zedub.zed_cmd(
    pattern="فيديو(?:\s|$)([\s\S]*)",
    command=("فيديو", plugin_category),
    info={
        "header": "تحميل فيديو من يوتيوب عبر API خارجي",
        "الاستخدام": "{tr}فيديو + رابط أو اسم الفيديو",
        "مثال": "{tr}فيديو حالات واتس",
    },
)
async def yt_mp4_api(event):
    reply_to_id = await reply_id(event)
    query = event.pattern_match.group(1)
    if not query:
        return await edit_or_reply(event, "**⚠️ الرجاء كتابة اسم الفيديو أو الرابط.**")

    zedevent = await edit_or_reply(event, "📹 **جاري التحميل من يوتيوب...**")

    if not query.startswith("http"):
        search_url = f"https://apisyu.com/api/yt/search?query={query}"
        search_res = requests.get(search_url).json()
        if not search_res or "data" not in search_res or not search_res["data"]:
            return await zedevent.edit("❌ لم أجد نتائج للبحث.")
        video_url = search_res["data"][0]["url"]
    else:
        video_url = query

    try:
        res = requests.get(f"{API_BASE}/mp4", params={"url": video_url}).json()
        if "url" not in res:
            return await zedevent.edit("❌ حدث خطأ أثناء جلب رابط التحميل.")

        mp4_link = res["url"]
        title = res.get("title", "فيديو من يوتيوب")
        thumb = res.get("thumbnail")

        await event.client.send_file(
            event.chat_id,
            mp4_link,
            caption=f"🎬 **العنوان:** {title}",
            thumb=thumb if thumb else None,
            supports_streaming=True,
            reply_to=reply_to_id,
        )
        await zedevent.delete()
    except Exception as e:
        LOGS.error(str(e))
        await zedevent.edit("❌ فشل التحميل من API.")
