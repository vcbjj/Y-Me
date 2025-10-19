import os
import requests
import subprocess
from telethon import types
from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..helpers.utils import reply_id
from . import zedub
from googleapiclient.discovery import build  # البحث عبر YouTube API

plugin_category = "البحث"
LOGS = logging.getLogger(__name__)

API_BASE = "https://api.dfkz.xo.je/apis/v3/download.php?url="
YOUTUBE_API_KEY = "AIzaSyBBhDdMwgH9I9_4uIZe8vYCWPMLHiKh4l0"  # ضع مفتاحك هنا

# ----------------------- البحث عن الفيديو عبر YouTube API -----------------------
def search_youtube(query: str):
    try:
        youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
        request = youtube.search().list(
            q=query,
            part="snippet",
            maxResults=1,
            type="video"
        )
        response = request.execute()
        items = response.get("items")
        if items:
            video = items[0]
            video_id = video["id"]["videoId"]
            title = video["snippet"]["title"]
            thumb = video["snippet"]["thumbnails"]["high"]["url"]
            url = f"https://www.youtube.com/watch?v={video_id}"
            return {"url": url, "title": title, "thumb": thumb}
    except Exception as e:
        LOGS.error(f"خطأ في البحث عن الفيديو: {e}")
    return None

# ----------------------- تحميل صوت -----------------------
@zedub.zed_cmd(pattern="(?:بحث|اغنيه)(?:\s|$)([\s\S]*)")
async def yt_search_audio(event):
    reply_to_id = await reply_id(event)
    query = event.pattern_match.group(1)
    if not query:
        return await edit_or_reply(event, "**⚠️ الرجاء كتابة اسم الأغنية أو الرابط.**")

    zedevent = await edit_or_reply(event, "🎵 **جاري البحث عن الأغنية...**")

    audio_file = None  # <- هنا تعريف المتغير مسبقًا

    if not query.startswith("http"):
        result = search_youtube(query)
        if not result:
            return await zedevent.edit("❌ لم أجد نتائج للبحث.")
        video_url, title, thumb = result["url"], result["title"], result["thumb"]
    else:
        video_url, title, thumb = query, "أغنية من يوتيوب", None

    try:
        # تحميل الفيديو عبر API dfkz
        api_res = requests.get(f"{API_BASE}{video_url}").json()
        video_link = api_res.get("url")
        if not video_link:
            return await zedevent.edit("❌ لم أتمكن من جلب رابط التحميل من API.")

        # تحويل الفيديو إلى صوت mp3
        audio_file = "temp_audio.mp3"
        cmd = ["ffmpeg", "-i", video_link, "-vn", "-ab", "192k", "-ar", "44100", "-y", audio_file]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(audio_file):
            return await zedevent.edit("❌ فشل استخراج الصوت من الفيديو.")

        await event.client.send_file(
            event.chat_id,
            file=audio_file,
            caption=f"🎶 **العنوان:** {title}\n📺 [فتح على يوتيوب]({video_url})",
            thumb=thumb,
            reply_to=reply_to_id
        )
        await zedevent.delete()
    except Exception as e:
        LOGS.error(str(e))
        await zedevent.edit("❌ حدث خطأ أثناء التحميل.")
    finally:
        if audio_file and os.path.exists(audio_file):
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
        video_url, title, thumb = result["url"], result["title"], result["thumb"]
    else:
        video_url, title, thumb = query, "فيديو من يوتيوب", None

    try:
        api_res = requests.get(f"{API_BASE}{video_url}").json()
        video_link = api_res.get("url")
        if not video_link:
            return await zedevent.edit("❌ لم أتمكن من جلب رابط التحميل من API.")

        await event.client.send_file(
            event.chat_id,
            file=video_link,
            caption=f"🎬 **العنوان:** {title}",
            thumb=thumb,
            supports_streaming=True,
            reply_to=reply_to_id
        )
        await zedevent.delete()
    except Exception as e:
        LOGS.error(str(e))
        await zedevent.edit("❌ حدث خطأ أثناء التحميل.")
