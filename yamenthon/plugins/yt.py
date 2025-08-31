from .. import zedub
from ..core.managers import edit_or_reply
from telethon.tl.types import DocumentAttributeVideo
import re, aiohttp, os, asyncio


# ====== أدوات مساعدة ======
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


# ====== تحميل عبر API ======
async def fetch_api(url: str, audio: bool = False):
    api_url = f"https://sii3.moayman.top/api/do.php?url={url}"
    async with aiohttp.ClientSession() as session:
        async with session.get(api_url) as resp:
            if resp.status != 200:
                raise Exception(f"API error {resp.status}")
            data = await resp.json()
            if not data.get("status"):
                raise Exception("فشل جلب الرابط من API")
            return data


# ====== أوامر ZedUB ======
@zedub.zed_cmd(pattern="تحميل(?: فيديو)?(?: |$)(.*)")
async def cmd_download_video(event):
    reply = await event.get_reply_message()
    raw = (event.pattern_match.group(1) or "").strip()
    url = find_youtube_url(raw, getattr(reply, "raw_text", None))

    if not url:
        return await edit_or_reply(event, "✘ يرجى تزويد **رابط يوتيوب** أو الرد على رسالة تحتوي رابط.")

    m = await edit_or_reply(event, "⏳ جاري جلب الفيديو ...")
    try:
        data = await fetch_api(url, audio=False)
        dl_url = data.get("url")
        title = data.get("title", "Video")

        await event.client.send_file(
            event.chat_id,
            file=dl_url,
            caption=f"✔ تم التحميل: {title}",
            attributes=[DocumentAttributeVideo(
                duration=int(data.get("duration", 0)),
                w=1280,
                h=720,
                supports_streaming=True
            )]
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"✘ خطأ: {e}")


@zedub.zed_cmd(pattern="تحميل(?: صوت)?(?: |$)(.*)")
async def cmd_download_audio(event):
    reply = await event.get_reply_message()
    raw = (event.pattern_match.group(1) or "").strip()
    url = find_youtube_url(raw, getattr(reply, "raw_text", None))

    if not url:
        return await edit_or_reply(event, "✘ يرجى تزويد **رابط يوتيوب** أو الرد على رسالة تحتوي رابط.")

    m = await edit_or_reply(event, "⏳ جاري جلب الصوت ...")
    try:
        data = await fetch_api(url, audio=True)
        dl_url = data.get("audio") or data.get("url")
        title = data.get("title", "Audio")

        await event.client.send_file(
            event.chat_id,
            file=dl_url,
            caption=f"🎶 {title}",
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"✘ خطأ: {e}")
