import json
import math
import os
import random
import re
import time
import asyncio
from pathlib import Path
from uuid import uuid4
from urllib.parse import quote_plus
import requests
from telethon import Button, types, events
from telethon.errors import QueryIdInvalidError
from telethon.events import CallbackQuery, InlineQuery
from youtubesearchpython import VideosSearch
import yt_dlp

from yamenthon import zedub
from ..Config import Config
from ..helpers.functions import rand_key
from ..helpers.functions.utube import (
    download_button,
    get_yt_video_id,
    get_ytthumb,
    result_formatter,
    ytsearch_data,
)
from ..sql_helper.globals import gvarstatus
from ..core.logger import logging

LOGS = logging.getLogger(__name__)

tr = Config.COMMAND_HAND_LER
DOWNLOAD_DIR = "./ytdl_cache"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def get_thumb(name):
    url = f"https://github.com/TgCatUB/CatUserbot-Resources/blob/master/Resources/Inline/{name}?raw=true"
    return types.InputWebDocument(url=url, size=0, mime_type="image/png", attributes=[])

def ibuild_keyboard(buttons):
    keyb = []
    for btn in buttons:
        # btn expected as (text, url, new_row_bool)
        if len(btn) >= 3 and btn[2] and keyb:
            keyb[-1].append(Button.url(btn[0], btn[1]))
        else:
            keyb.append([Button.url(btn[0], btn[1])])
    return keyb

@zedub.tgbot.on(InlineQuery)
async def inline_handler(event):
    builder = event.builder
    result = None
    query = (event.text or "").strip()
    string = query.lower()
    query_user_id = event.query.user_id
    str_y = query.split(" ", 1)

    try:
        if query_user_id == Config.OWNER_ID or query_user_id in Config.SUDO_USERS:
            # "ytdl <query_or_link>"
            if str_y and str_y[0].lower() == "ytdl" and len(str_y) == 2:
                link = get_yt_video_id(str_y[1].strip())
                found_ = True

                if link is None:
                    search = VideosSearch(str_y[1].strip(), limit=15)
                    resp = (search.result()).get("result")
                    if not resp:
                        found_ = False
                    else:
                        outdata = await result_formatter(resp)
                        key_ = rand_key()
                        ytsearch_data.store_(key_, outdata)

                        # choose display index safely (use index 1 if exists, else 0)
                        idx = 1 if len(outdata) > 1 else 0
                        item = outdata[idx]

                        buttons = [
                            Button.inline(f"1 / {len(outdata)}", data=f"ytdl_next_{key_}_1"),
                            Button.inline("القائمـة 📜", data=f"ytdl_listall_{key_}_1"),
                            Button.inline("⬇️  تحميـل", data=f'ytdl_download_{item["video_id"]}_0'),
                        ]
                        caption = item.get("message", str(item.get("title", str_y[1])))
                        photo = await get_ytthumb(item["video_id"])
                else:
                    # if link is a video id or url
                    caption, buttons = await download_button(link, body=True)
                    photo = await get_ytthumb(link)

                if found_:
                    # build markup safely
                    try:
                        markup = event.client.build_reply_markup(buttons)
                    except Exception:
                        # fallback: convert simple list-of-tuples to markup (if needed)
                        try:
                            markup = event.client.build_reply_markup(
                                [[Button.inline(b.text, data=b.data) for b in buttons]]
                            )
                        except Exception:
                            markup = None

                    # prepare photo for inline result
                    photo_input = types.InputWebDocument(url=photo, size=0, mime_type="image/jpeg", attributes=[])
                    # parse message text (wrap in try/except because _parse_message_text may not exist in some clients)
                    try:
                        text, msg_entities = await event.client._parse_message_text(caption, "html")
                    except Exception:
                        text = caption
                        msg_entities = []

                    result = types.InputBotInlineResult(
                        id=str(uuid4()),
                        type="photo",
                        title=str(link or str_y[1]),
                        description="⬇️ اضغـط للتحميـل",
                        thumb=photo_input,
                        content=photo_input,
                        send_message=types.InputBotInlineMessageMediaAuto(
                            reply_markup=markup, message=text, entities=msg_entities
                        ),
                    )
                else:
                    result = builder.article(
                        title="Not Found",
                        text=f"No Results found for `{str_y[1]}`",
                        description="INVALID",
                    )

                try:
                    await event.answer([result] if result else None)
                except QueryIdInvalidError:
                    await event.answer(
                        [
                            builder.article(
                                title="Not Found",
                                text=f"No Results found for `{str_y[1]}`",
                                description="INVALID",
                            )
                        ]
                    )

            elif string == "pmpermit":
                buttons = [Button.inline(text="عـرض الخيـارات", data="show_pmpermit_options")]
                PM_PIC = gvarstatus("pmpermit_pic")
                if PM_PIC:
                    CAT = [x for x in PM_PIC.split()]
                    PIC = list(CAT)
                    CAT_IMG = random.choice(PIC)
                else:
                    CAT_IMG = None

                query_text = gvarstatus("pmpermit_text") or ""
                if CAT_IMG and CAT_IMG.endswith((".jpg", ".jpeg", ".png")):
                    result = builder.photo(CAT_IMG, text=query_text, buttons=buttons)
                elif CAT_IMG:
                    result = builder.document(CAT_IMG, title="Alive cat", text=query_text, buttons=buttons)
                else:
                    result = builder.article(title="Alive cat", text=query_text, buttons=buttons)

                await event.answer([result] if result else None)

        else:
            buttons = [
                (
                    Button.url("قنـاة السـورس", "https://t.me/YamenThon"),
                    Button.url("مطـور السـورس", "https://t.me/T_A_Tl"),
                )
            ]
            try:
                markup = event.client.build_reply_markup(buttons)
            except Exception:
                markup = None

            photo = types.InputWebDocument(
                url="https://i.postimg.cc/HsBGV28T/image.jpg",
                size=0,
                mime_type="image/jpeg",
                attributes=[],
            )
            try:
                text, msg_entities = await event.client._parse_message_text(
                    "𝗗𝗲𝗽𝗹𝗼𝘆 𝘆𝗼𝘂𝗿 𝗼𝘄𝗻 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉⛤.", "md"
                )
            except Exception:
                text = "𝗗𝗲𝗽𝗹𝗼𝘆 𝘆𝗼𝘂𝗿 𝗼𝘄𝗻 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉⛤."
                msg_entities = []

            result = types.InputBotInlineResult(
                id=str(uuid4()),
                type="photo",
                title="𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉⛤ 𓅛",
                description="روابـط التنصـيب",
                url="https://t.me/YamenThon",
                thumb=photo,
                content=photo,
                send_message=types.InputBotInlineMessageMediaAuto(
                    reply_markup=markup, message=text, entities=msg_entities
                ),
            )
            await event.answer([result] if result else None)

    except Exception as exc:
        LOGS.exception("Error in inline_handler: %s", exc)
        try:
            await event.answer(
                [
                    builder.article(
                        title="Error",
                        text="حدث خطأ داخلي أثناء البحث. تواصل مع مطور السورس.",
                        description="ERROR",
                    )
                ]
            )
        except Exception:
            pass

def download_with_api(video_url: str, output_path: str):
    """Try to fetch download links from the external API and download the best mp4 available.
    Raises Exception on failure.
    """
    api_endpoint = "https://sii3.moayman.top/api/do.php"
    headers = {"User-Agent": "Mozilla/5.0 (compatible; YamenThon/1.0)"}
    try:
        resp = requests.get(api_endpoint, params={"url": video_url}, headers=headers, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        raise Exception(f"فشل الوصول للـ API: {e}")

    # try parse json - include fallback debug info
    try:
        data = resp.json()
    except Exception as e:
        raise Exception(f"فشل في تحليل رد الـ API كـ JSON: {e} - النص: {resp.text[:500]}")

    links = data.get("links") or []
    if not links:
        raise Exception(f"❌ الرد من الـ API ما فيه روابط تحميل. payload={json.dumps(data)[:1000]}")

    # Normalize: try to find mp4 links
    mp4_links = []
    for l in links:
        ext = str(l.get("ext") or l.get("format") or "").lower()
        if "mp4" in ext or (str(l.get("url") or l.get("link") or "").lower().endswith(".mp4")):
            mp4_links.append(l)

    # Preferred ordering by resolution keywords
    preferred_res = ("360", "480", "720")
    file_url = None

    for pref in preferred_res:
        for l in mp4_links:
            q = str(l.get("quality") or l.get("resolution") or l.get("label") or "")
            if pref in q:
                file_url = l.get("url") or l.get("link")
                break
        if file_url:
            break

    # fallback to first mp4
    if not file_url and mp4_links:
        file_url = mp4_links[0].get("url") or mp4_links[0].get("link")

    # last resort: any link with url/link
    if not file_url:
        for l in links:
            if l.get("url") or l.get("link"):
                file_url = l.get("url") or l.get("link")
                break

    if not file_url:
        raise Exception("❌ ما لقيت أي رابط صالح للتحميل في بيانات الـ API.")

    # Download the selected file
    try:
        with requests.get(file_url, stream=True, timeout=60) as file_resp:
            file_resp.raise_for_status()
            with open(output_path, "wb") as f:
                for chunk in file_resp.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
    except Exception as e:
        # remove partial file if any
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass
        raise Exception(f"فشل تنزيل الملف من رابط الملف المحدد: {e}")

def download_with_ytdlp_fallback(video_url: str, output_path: str):
    """Use yt-dlp as a fallback if the API approach fails."""
    ydl_opts = {
        "format": "mp4[height<=720]/best[ext=mp4]/best",
        "outtmpl": output_path,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,  # avoid console logs to interfere
        "logger": None,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
    except Exception as e:
        # remove partial file if any
        try:
            if os.path.exists(output_path):
                os.remove(output_path)
        except Exception:
            pass
        raise Exception(f"yt-dlp فشل في التحميل: {e}")

def download_worker(video_url: str, output_path: str):
    """Try API download first, if it fails fall back to yt-dlp.
    This function is synchronous so it should be run in an executor from async code.
    """
    api_err = None  # تهيئة المتغير خارج كتلة الاستثناء لتجنّب الوصول لمتغير غير معرف
    try:
        download_with_api(video_url, output_path)
        return
    except Exception as e:
        api_err = e
        LOGS.warning("API download failed: %s", e)

    # fallback to yt-dlp
    try:
        download_with_ytdlp_fallback(video_url, output_path)
        return
    except Exception as ytdlp_err:
        LOGS.exception("yt-dlp fallback failed: %s", ytdlp_err)
        # ربط الاستثناءات وإعطاء رسالة مفيدة
        raise Exception(
            f"كلا الطريقتين فشلتا: API_error={repr(api_err)}; yt-dlp_error={repr(ytdlp_err)}"
        ) from ytdlp_err

@zedub.tgbot.on(events.CallbackQuery(pattern=r"ytdl_download_(.*)"))
async def ytdl_download_callback(event):
    try:
        # show an immediate alert that the download started
        try:
            await event.answer("🚀 يتم التحميـل من يوتيوب، الرجاء الانتظـار...", alert=True)
        except Exception:
            # sometimes answer with alert may fail (bots vs userbots), ignore
            pass

        data = event.data.decode("utf-8")
        parts = data.split("_")
        if len(parts) < 3:
            return await event.edit("❌ معرف الفيديو غير صالح.")

        video_id = parts[2]
        url = f"https://www.youtube.com/watch?v={video_id}"

        file_name = f"{uuid4()}.mp4"
        video_path = os.path.join(DOWNLOAD_DIR, file_name)

        loop = asyncio.get_running_loop()
        # run the blocking download in a threadpool
        await loop.run_in_executor(None, download_worker, url, video_path)

        # ensure file exists
        if not os.path.exists(video_path):
            return await event.edit("❌ فشل تحميل الملف: الملف غير موجود بعد التنزيل.")

        # check size before sending (Telegram limit for bots ~50MB for file sending via send_file without chunking)
        try:
            size = os.path.getsize(video_path)
        except Exception:
            size = None

        if size and size > 49 * 1024 * 1024:
            try:
                os.remove(video_path)
            except Exception:
                pass
            return await event.edit("❌ الفيديو أكبر من 50MB ولا يمكن للبوت إرساله.")

        caption = f"📹 تم التحميـل من YouTube\n🔗 `{url}`"

        # determine chat id (callback may come from inline message)
        chat = None
        if getattr(event, "chat_id", None):
            chat = event.chat_id
        elif getattr(event, "message", None) and getattr(event.message, "chat_id", None):
            chat = event.message.chat_id
        else:
            # fallback to sender
            chat = event.sender_id

        await event.client.send_file(chat, file=video_path, caption=caption)

        # cleanup
        await asyncio.sleep(2)
        try:
            os.remove(video_path)
        except Exception:
            pass

        # try to edit the original inline message to confirm success (if possible)
        try:
            await event.edit("✅ تم التحميل والإرسال بنجاح.")
        except Exception:
            # may be inline result or not editable
            pass

    except Exception as e:
        LOGS.exception("Error in ytdl_download_callback: %s", e)
        # try to remove partial file safely
        try:
            video_path_local = locals().get('video_path')
            if video_path_local and os.path.exists(video_path_local):
                os.remove(video_path_local)
        except Exception:
            pass
        # send friendly error message
        try:
            await event.edit(f"❌ حدث خطأ أثناء التحميل أو الإرسال:\n`{str(e)}`")
        except Exception:
            # final fallback: answer alert
            try:
                await event.answer(f"❌ حدث خطأ أثناء التحميل:\n{str(e)}", alert=True)
            except Exception:
                pass
