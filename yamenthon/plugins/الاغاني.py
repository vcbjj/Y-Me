import os
import requests
import subprocess
from telethon import types
from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..helpers.utils import reply_id
from . import zedub
import yt_dlp

plugin_category = "البحث"
LOGS = logging.getLogger(__name__)

API_BASE = "https://api.dfkz.xo.je/apis/v3/download.php?url="

def search_youtube(query: str):
    """بحث سريع عن الفيديو باستخدام yt_dlp"""
    ydl_opts = {"quiet": True, "skip_download": True}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch1:{query}", download=False)
        if "entries" in info and len(info["entries"]) > 0:
            video = info["entries"][0]
            return {
                "url": video["webpage_url"],
                "title": video.get("title"),
                "thumb": video.get("thumbnail")
            }
    return None

# ----------------------- تحميل صوت -----------------------
@zedub.zed_cmd(pattern="(?:بحث|اغنيه)(?:\s|$)([\s\S]*)")
async def yt_search_audio(event):
    reply_to_id = await reply_id(event)
    query = event.pattern_match.group(1)
    if not query:
        return await edit_or_reply(event, "**⚠️ الرجاء كتابة اسم الأغنية أو الرابط.**")

    zedevent = await edit_or_reply(event, "🎵 **جاري البحث عن الأغنية...**")

    if not query.startswith("http"):
        result = search_youtube(query)
        if not result:
            return await zedevent.edit("❌ لم أجد نتائج للبحث.")
        video_url = result["url"]
        title = result["title"]
        thumb = result["thumb"]
    else:
        video_url = query
        title = "أغنية من يوتيوب"
        thumb = None

    try:
        api_res = requests.get(f"{API_BASE}{video_url}").json()
        links = api_res.get("links", [])
        if not links:
            return await zedevent.edit("❌ لم أتمكن من جلب رابط التحميل من API.")

        video_link = next((l["url"] for l in links if l.get("type") == "video"), None)
        if not video_link:
            return await zedevent.edit("❌ لم أجد رابط فيديو صالح.")

        audio_file = "temp_audio.mp3"
        cmd = ["ffmpeg", "-i", video_link, "-vn", "-ab", "192k", "-ar", "44100", "-y", audio_file]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(audio_file):
            return await zedevent.edit("❌ فشل استخراج الصوت من الفيديو.")

        await event.client.send_file(
            event.chat_id,
            file=audio_file,
            caption=f"🎶 **العنوان:** {title}\n📺 [فتح على يوتيوب]({video_url})",
            thumb=thumb if thumb else None,
            reply_to=reply_to_id
        )
        await zedevent.delete()
    except Exception as e:
        LOGS.error(str(e))
        await zedevent.edit("❌ حدث خطأ أثناء التحميل.")
    finally:
        if os.path.exists(audio_file):
            os.remove(audio_file)

# ----------------------- تحميل فيديو -----------------------
@zedub.zed_cmd(pattern="فيديو(?:\s|$)([\s\S]*)")
async def yt_search_video(event):
    reply_to_id = await reply_id(event)
    query = event.pattern_match.group(1)
    if not query:
        return await edit_or_reply(event, "**⚠️ الرجاء كتابة اسم الفيديو أو الرابط.**")

    zedevent = await edit_or_reply(event, "📹 **جاري البحث عن الفيديو...**")

    if not query.startswith("http"):
        result = search_youtube(query)
        if not result:
            return await zedevent.edit("❌ لم أجد نتائج للبحث.")
        video_url = result["url"]
        title = result["title"]
        thumb = result["thumb"]
    else:
        video_url = query
        title = "فيديو من يوتيوب"
        thumb = None

    try:
        api_res = requests.get(f"{API_BASE}{video_url}").json()
        links = api_res.get("links", [])
        if not links:
            return await zedevent.edit("❌ لم أتمكن من جلب رابط التحميل من API.")

        video_link = next((l["url"] for l in links if l.get("type") == "video"), None)
        if not video_link:
            return await zedevent.edit("❌ لم أجد رابط فيديو صالح.")

        await event.client.send_file(
            event.chat_id,
            file=video_link,
            caption=f"🎬 **العنوان:** {title}",
            thumb=thumb if thumb else None,
            supports_streaming=True,
            reply_to=reply_to_id
        )
        await zedevent.delete()
    except Exception as e:
        LOGS.error(str(e))
        await zedevent.edit("❌ حدث خطأ أثناء التحميل.")
