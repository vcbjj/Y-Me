import base64
import contextlib
import io
import os

from ShazamAPI import Shazam
from telethon import types
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from validators.url import url

from ..core.logger import logging
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.functions import delete_conv, yt_search
from ..helpers.tools import media_type
from ..helpers.utils import reply_id
from . import zedub, song_download

plugin_category = "البحث"
LOGS = logging.getLogger(__name__)


SONG_SEARCH_STRING = "<b>╮ جـارِ البحث ؏ـن الاغنيـٓه... 🎧♥️╰</b>"
SONG_NOT_FOUND = "<b>    ⃟⁞⃟⟢ ╎لـم استطـع ايجـاد المطلـوب .. جرب البحث باستخـدام الامـر (.اغنيه)</b>"
SONG_SENDING_STRING = "<b>╮ جـارِ تحميـل الاغنيـٓه... 🎧♥️╰</b>"

@zedub.zed_cmd(
    pattern="ابحث(?:\ع|$)([\s\S]*)",
    command=("ابحث", plugin_category),
    info={
        "header": "To reverse search song.",
        "الوصـف": "Reverse search audio file using shazam api",
        "امـر مضـاف": {"ع": "To send the song of sazam match"},
        "الاستخـدام": [
            "{tr}ابحث بالــرد ع بصمـه او مقطـع صوتي",
            "{tr}ابحث ع بالــرد ع بصمـه او مقطـع صوتي",
        ],
    },
)
async def shazamcmd(event):
    "To reverse search song."
    reply = await event.get_reply_message()
    mediatype = await media_type(reply)
    chat = "@DeezerMusicBot"
    delete = False
    flag = event.pattern_match.group(1)
    if not reply or not mediatype or mediatype not in ["Voice", "Audio"]:
        return await edit_delete(
            event, "**- بالــرد ع مقطـع صـوتي**"
        )
    zedevent = await edit_or_reply(event, "**- جـار تحميـل المقـطع الصـوتي ...**")
    name = "zed.mp3"
    try:
        for attr in getattr(reply.document, "attributes", []):
            if isinstance(attr, types.DocumentAttributeFilename):
                name = attr.file_name
        dl = io.FileIO(name, "a")
        await event.client.fast_download_file(
            location=reply.document,
            out=dl,
        )
        dl.close()
        mp3_fileto_recognize = open(name, "rb").read()
        shazam = Shazam(mp3_fileto_recognize)
        recognize_generator = shazam.recognizeSong()
        track = next(recognize_generator)[1]["track"]
    except Exception as e:
        LOGS.error(e)
        return await edit_delete(
            zedevent, f"**- خطـأ :**\n__{e}__"
        )

    file = track["images"]["background"]
    title = track["share"]["subject"]
    slink = await yt_search(title)
    if flag == "s":
        deezer = track["hub"]["providers"][1]["actions"][0]["uri"][15:]
        async with event.client.conversation(chat) as conv:
            try:
                purgeflag = await conv.send_message("/start")
            except YouBlockedUserError:
                await zedub(unblock("DeezerMusicBot"))
                purgeflag = await conv.send_message("/start")
            await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            await conv.send_message(deezer)
            await event.client.get_messages(chat)
            song = await event.client.get_messages(chat)
            await song[0].click(0)
            await conv.get_response()
            file = await conv.get_response()
            await event.client.send_read_acknowledge(conv.chat_id)
            delete = True
    await event.client.send_file(
        event.chat_id,
        file,
        caption=f"<b>    ⃟⁞⃟⟢ ╎ المقطـع الصـوتي :</b> <code>{title}</code>\n<b>    ⃟⁞⃟⟢ ╎ الرابـط : <a href = {slink}/1>YouTube</a></b>",
        reply_to=reply,
        parse_mode="html",
    )
    await zedevent.delete()
    if delete:
        await delete_conv(event, chat, purgeflag)


