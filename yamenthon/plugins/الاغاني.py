import base64
import contextlib
import io
import os
import requests
import re
import json
import subprocess

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

API_URL = "https://api.dfkz.xo.je/apis/v3/download.php"


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


def parse_api_response(resp):
    """
    يحاول تفسير استجابة الـ API بأمان:
    - إذا كانت JSON ولها keys['links'] يعتبرها ناجحة
    - إذا كانت تحتوي success==True يحترمها
    - يعيد dict أو يعيد خطأ للعرض
    """
    try:
        data = resp.json()
    except ValueError:
        # ليس JSON
        return {"ok": False, "error": "API returned non-json response", "text": resp.text[:1000]}
    except Exception as e:
        return {"ok": False, "error": f"request error: {e}"}

    # إذا وُجد حقل success واختبرناه
    if isinstance(data, dict) and data.get("success") is not None:
        if data.get("success"):
            return {"ok": True, "data": data}
        else:
            # success:false لكن قد يحتوي على links (بعض الـ APIs لا يستخدم success)
            if data.get("links"):
                return {"ok": True, "data": data}
            return {"ok": False, "error": "API returned success=false", "data": data}

    # لا يوجد success — نفترض نجاح إذا وُجد links
    if isinstance(data, dict) and data.get("links"):
        return {"ok": True, "data": data}

    # fallback: لو البنية مختلفة ابحث عن حقل شبيه
    if isinstance(data, dict) and ("result" in data or "data" in data):
        # حاول إعادة تشكيل مبسط إن أمكن
        candidate = data.get("result") or data.get("data")
        if isinstance(candidate, dict) and candidate.get("links"):
            return {"ok": True, "data": candidate}
    return {"ok": False, "error": "API response does not contain links", "data": data}


def extract_first_link(api_response, file_type="audio"):
    """استخراج أول رابط صالح من رد الـ API"""
    links = api_response.get("links", []) or []
    for link in links:
        # link قد يكون dict أو سلسلة
        if isinstance(link, dict):
            if link.get("type") == file_type and link.get("url"):
                return link
        else:
            # لو كان رابط مباشر كـ string
            if file_type in ("video", "audio"):
                return {"type": file_type, "url": str(link)}
    return None


@zedub.zed_cmd(
    pattern=r"(?:بحث|اغنيه)(?:\s+|$)([\s\S]*)",
    command=("بحث","اغنيه", plugin_category),
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
        resp = requests.get(API_URL, params={"url": video_link}, timeout=20)
    except Exception as e:
        return await zedevent.edit(f"❌ فشل التحميل من API.\n`request error: {e}`")

    parsed = parse_api_response(resp)
    if not parsed.get("ok"):
        err = parsed.get("error", "unknown")
        data = parsed.get("data")
        msg = f"❌ فشل التحميل من API.\n`{err}`"
        if data:
            msg += "\n`" + (str(data)[:800].replace("`", "'")) + "`"
        return await zedevent.edit(msg)

    api_response = parsed.get("data", {})
    title = api_response.get("title", "اغنية")
    thumb = api_response.get("thumb")

    # استخراج رابط الفيديو أو الصوت
    link_info = extract_first_link(api_response, "video") or extract_first_link(api_response, "audio")
    if not link_info:
        return await zedevent.edit("❌ لم يتم العثور على رابط التحميل الصوتي.")

    # تأكد أن link_info dict قبل استخدام .get()
    download_url = link_info.get("url") if isinstance(link_info, dict) else str(link_info)
    quality = link_info.get("quality", "غير معروف") if isinstance(link_info, dict) else "غير معروف"
    await zedevent.edit(f"📥 **جاري تحميل الاغنية:**\n🎵 {title}\n💡 الجودة: {quality}")

    safe_title = re.sub(r"[\\/*?\"<>|:]", "_", title)[:200]
    video_path = f"/tmp/{safe_title}.mp4"
    audio_path = f"/tmp/{safe_title}.mp3"

    # تحميل الفيديو
    try:
        dl_resp = requests.get(download_url, stream=True, timeout=30)
        with open(video_path, "wb") as f:
            for chunk in dl_resp.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        return await zedevent.edit(f"⚠️ حدث خطأ أثناء تحميل الفيديو:\n`{e}`")

    # تحويل الفيديو إلى صوت باستخدام ffmpeg
    try:
        cmd = [
            "ffmpeg",
            "-y",
            "-i", video_path,
            "-vn",
            "-ab", "128k",
            "-ar", "44100",
            "-f", "mp3",
            audio_path
        ]
        subprocess.run(cmd, check=True)
    except Exception as e:
        return await zedevent.edit(f"⚠️ حدث خطأ أثناء التحويل إلى صوت:\n`{e}`")
    finally:
        if os.path.exists(video_path):
            os.remove(video_path)

    # إرسال الملف الصوتي
    try:
        await event.client.send_file(
            event.chat_id,
            file=audio_path,
            caption=f"**⎉╎البحث :** `{title}`",
            thumb=thumb if thumb else None,
            supports_streaming=True,
            reply_to=reply_to_id,
        )
    except Exception as e:
        return await zedevent.edit(f"⚠️ حدث خطأ أثناء إرسال الملف الصوتي:\n`{e}`")
    finally:
        if os.path.exists(audio_path):
            os.remove(audio_path)

    await zedevent.delete()    

@zedub.zed_cmd(
    pattern=r"(?:فديو|فيديو)(?:\s+|$)([\s\S]*)",
    command=("فيديو","فديو", plugin_category),
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
        resp = requests.get(API_URL, params={"url": video_link}, timeout=20)
    except Exception as e:
        return await zedevent.edit(f"❌ فشل التحميل من API.\n`request error: {e}`")

    parsed = parse_api_response(resp)
    if not parsed.get("ok"):
        err = parsed.get("error", "unknown")
        data = parsed.get("data")
        msg = f"❌ فشل التحميل من API.\n`{err}`"
        if data:
            msg += "\n`" + (str(data)[:800].replace("`", "'")) + "`"
        return await zedevent.edit(msg)

    api_response = parsed.get("data", {})

    title = api_response.get("title", "فيديو")
    thumb = api_response.get("thumb")

    link_info = extract_first_link(api_response, "video") or extract_first_link(api_response, "audio")
    if not link_info:
        return await zedevent.edit("❌ لم يتم العثور على رابط التحميل الفيديو.")

    download_url = link_info.get("url")
    quality = link_info.get("quality", "غير معروف")

    await zedevent.edit(f"📥 **جاري تحميل الفيديو:**\n🎬 {title}\n💡 الجودة: {quality}")

    try:
        dl_resp = requests.get(download_url, stream=True, timeout=30)
    except Exception as e:
        return await zedevent.edit(f"⚠️ حدث خطأ أثناء التحميل:\n`download request error: {e}`")

    if dl_resp.status_code != 200:
        return await zedevent.edit(f"⚠️ حدث خطأ أثناء التحميل:\n`bad status {dl_resp.status_code}`")

    content_length = dl_resp.headers.get("content-length")
    try:
        if content_length and int(content_length) > 500 * 1024 * 1024:
            return await zedevent.edit("⚠️ الملف أكبر من 500MB. التحميل مُوقوف لمنع استهلاك موارد.")
    except Exception:
        pass

    safe_title = re.sub(r"[\\/*?\"<>|:]", "_", title)[:200]
    file_path = f"/tmp/{safe_title}.mp4" if link_info.get("type") == "video" else f"/tmp/{safe_title}.mp3"

    try:
        with open(file_path, "wb") as f:
            for chunk in dl_resp.iter_content(chunk_size=1024 * 64):
                if chunk:
                    f.write(chunk)
    except Exception as e:
        return await zedevent.edit(f"⚠️ حدث خطأ أثناء كتابة الملف:\n`{e}`")

    try:
        await event.client.send_file(
            event.chat_id,
            file=file_path,
            caption=f"**⎉╎البحث :** `{title}`",
            thumb=thumb if thumb else None,
            supports_streaming=True,
            reply_to=reply_to_id,
        )
    except Exception as e:
        try:
            return await zedevent.edit(f"⚠️ حدث خطأ أثناء إرسال الملف:\n`{e}`\n\nيمكنك محاولة هذا الرابط مباشرة:\n{download_url}")
        finally:
            if os.path.exists(file_path):
                os.remove(file_path)

    if os.path.exists(file_path):
        os.remove(file_path)
    await zedevent.delete()
