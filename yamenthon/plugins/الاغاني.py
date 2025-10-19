import os
import requests
import subprocess
from telethon import types
from ..core.logger import logging
from ..core.managers import edit_or_reply
from ..helpers.utils import reply_id
from . import zedub
from youtubesearchpython import VideosSearch  # مكتبة البحث الثابتة

plugin_category = "البحث"
LOGS = logging.getLogger(__name__)

API_BASE = "https://api.dfkz.xo.je/apis/v3/download.php?url="

# ----------------------- تحميل صوت -----------------------
@zedub.zed_cmd(pattern="(?:بحث|اغنيه)(?:\s|$)([\s\S]*)")
async def yt_search_audio(event):
    reply_to_id = await reply_id(event)
    query = event.pattern_match.group(1)
    if not query:
        return await edit_or_reply(event, "**⚠️ الرجاء كتابة اسم الأغنية أو الرابط.**")

    zedevent = await edit_or_reply(event, "🎵 **جاري البحث عن الأغنية...**")

    # البحث عن الفيديو
    if not query.startswith("http"):
        try:
            search = VideosSearch(query, limit=1)
            result = search.result()["result"][0]
            video_url = result["link"]
            title = result["title"]
            thumb = result["thumbnails"][0]["url"]
        except Exception as e:
            LOGS.error(f"خطأ في البحث عن الفيديو: {e}")
            return await zedevent.edit("❌ لم أجد نتائج للبحث.")
    else:
        video_url = query
        title = "أغنية من يوتيوب"
        thumb = None

    try:
        # التحميل عبر API dfkz
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

    # البحث عن الفيديو
    if not query.startswith("http"):
        try:
            search = VideosSearch(query, limit=1)
            result = search.result()["result"][0]
            video_url = result["link"]
            title = result["title"]
            thumb = result["thumbnails"][0]["url"]
        except Exception as e:
            LOGS.error(f"خطأ في البحث عن الفيديو: {e}")
            return await zedevent.edit("❌ لم أجد نتائج للبحث.")
    else:
        video_url = query
        title = "فيديو من يوتيوب"
        thumb = None

    try:
        api_res = requests.get(f"{API_BASE}{video_url}").json()
        video_link = api_res.get("url")
        if not video_link:
            return await zedevent.edit("❌ لم أتمكن من جلب رابط التحميل من API.")

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
