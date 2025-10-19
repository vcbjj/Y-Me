# وش واجي تخمط على الملف وتسمي نفسك مطور ياخماط
# روح تعلم وصير مطور بدل ما تخمط حقوقي
# تأخذ الملف وتخمط عليه بس ليش مسمي نفسك مطور
# الملف تابع لسورس يمنثون حقوق الاسطوره عاشق الصمت @T_A_Tl 

from .. import zedub
from ..core.managers import edit_or_reply
from telethon.tl.types import DocumentAttributeVideo
import re, aiohttp
import os
import asyncio
import subprocess

# حقوق الاسطوره عاشق الصمت @T_A_Tl 
YOUTUBE_URL_RE = re.compile(r'(https?://)?(www\.|m\.)?(youtube\.com|youtu\.be)/[^\s]+', re.IGNORECASE)

def normalize_youtube_url(url: str) -> str:
    url = url.strip()
    if url.startswith("www."):
        url = "https://" + url
    if url.startswith("m.youtube.com"):
        url = url.replace("m.youtube.com", "www.youtube.com", 1)
    if "youtube.com/shorts/" in url:
        vid = url.split("youtube.com/shorts/")[-1].split("?")[0].split("/")[0]
        return f"https://www.youtube.com/watch?v={vid}"
    if "youtu.be/" in url:
        vid = url.split("youtu.be/")[-1].split("?")[0]
        return f"https://www.youtube.com/watch?v={vid}"
    return url

def find_youtube_url(*candidates) -> str | None:
    for text in candidates:
        if not text:
            continue
        m = YOUTUBE_URL_RE.search(str(text))
        if m:
            return normalize_youtube_url(m.group(0))
    return None


# حقوق الاسطوره عاشق الصمت @T_A_Tl 
async def fetch_api(url: str):
    api_url = f"https://api.dfkz.xo.je/apis/v3/download.php?url={url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception(f"API error {resp.status}")
            return await resp.json()


def pick_link(data: dict, want_audio=False):
    """اختيار أول رابط مناسب من القائمة"""
    for link in data.get("links", []):
        if want_audio:
            # نتأكد إنه صوت (حتى لو الـ type = video)
            if link.get("type") == "audio" or "audio" in link.get("quality", "").lower():
                return link
        else:
            if link.get("type") == "video" and "mp4" in link.get("ext", ""):
                return link
    return None


# حقوق الاسطوره عاشق الصمت @T_A_Tl 
# 🔹 هاندلر تحميل الفيديو فقط
@zedub.zed_cmd(pattern="تحميل(?: |$)(?!فديو)(.*)")
async def cmd_download_video(event):
    reply = await event.get_reply_message()
    raw = (event.pattern_match.group(1) or "").strip()
    url = find_youtube_url(raw, getattr(reply, "raw_text", None))

    if not url:
        return await edit_or_reply(event, "✘ يرجى تزويد **رابط يوتيوب** أو الرد على رسالة تحتوي رابط.")

    m = await edit_or_reply(event, "⏳ جاري جلب الفيديو ...")
    try:
        data = await fetch_api(url)
        link = pick_link(data, want_audio=False)
        if not link:
            return await m.edit("✘ لم أجد رابط فيديو مناسب في JSON")

        await event.client.send_file(
            event.chat_id,
            file=link["url"],
            caption=f"✔ تم التحميل: {data.get('title','')}\n 📥[𝒀𝑨𝑴𝑬𝑵𝑻𝑯𝑶𝑵𖤍](https://t.me/YamenThon)",
            attributes=[DocumentAttributeVideo(
                duration=int(float(link.get("dur", 0))),
                w=1280,
                h=720,
                supports_streaming=True
            )]
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"✘ خطأ: {e}")



# 🔹 هاندلر تحميل الصوت فقط
@zedub.zed_cmd(pattern="تحميل صوت(?: |$)(.*)")
async def cmd_download_audio(event):
    reply = await event.get_reply_message()
    raw = (event.pattern_match.group(1) or "").strip()
    url = find_youtube_url(raw, getattr(reply, "raw_text", None))

    if not url:
        return await edit_or_reply(event, "✘ يرجى تزويد **رابط يوتيوب** أو الرد على رسالة تحتوي رابط.")

    m = await edit_or_reply(event, "⏳ جاري جلب الصوت ...")
    try:
        data = await fetch_api(url)
        links = data.get("links", [])

        if not links:
            return await m.edit("✘ لم أجد أي روابط داخل JSON")

        # 🔹 نختار رابط صوت حقيقي إن وجد
        audio_link = None
        for link in links:
            if link.get("type") == "audio" or "audio" in link.get("quality", "").lower() or link.get("ext") in ["mp3", "m4a"]:
                audio_link = link
                break

        if not audio_link:
            audio_link = min(links, key=lambda x: int(x.get("clen", "999999999")))

        video_url = audio_link["url"]
        audio_file = "temp_audio.mp3"

        # 🔸 التحميل والتحويل إلى MP3 باستخدام ffmpeg مباشرة
        cmd = [
            "ffmpeg", "-i", video_url,
            "-vn", "-ab", "192k", "-ar", "44100",
            "-y", audio_file
        ]
        subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if not os.path.exists(audio_file):
            return await m.edit("✘ فشل استخراج الصوت")

        await event.client.send_file(
            event.chat_id,
            file=audio_file,
            caption=f"🎶 {data.get('title','')}",
            voice_note=False
        )

        await m.delete()
    except Exception as e:
        await m.edit(f"✘ خطأ: {e}")
    finally:
        if os.path.exists("temp_audio.mp3"):
            os.remove("temp_audio.mp3")
