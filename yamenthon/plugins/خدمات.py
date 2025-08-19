
import requests
import asyncio
import os
import sys
import urllib.request
from datetime import timedelta
from telethon import events
from telethon.errors import FloodWaitError
from telethon.tl.functions.messages import GetHistoryRequest, ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.contacts import UnblockRequest as unblock
from telethon.tl.functions.messages import ImportChatInviteRequest as Get

from yamenthon import zedub
from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

plugin_category = "الخدمات"

@zedub.zed_cmd(pattern="تطبيق(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return
    if event.reply_to_msg_id:
        reply = await event.get_reply_message()
        d_link = reply.text
    else:
        return await event.edit("**    ⃟⁞⃟⟢ ╎قم بكتـابة رابـط + اسـم التطبيـق اولاً ...**\n**    ⃟⁞⃟⟢ ╎او ارسـل .تطبيق بالـرد ع رابـط التطبيـق ...**")
    if "preview" in d_link or "google" in d_link:
        await event.edit("**    ⃟⁞⃟⟢ ╎جـارِ تحميـل التطبيق ...**")
    else:
        return
    chat = "@apkdl_bot"
    async with borg.conversation(chat) as conv: 
        try:
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(d_link)
            await asyncio.sleep(3)
            zelzal = await conv.get_response()
            if "Version:" in zelzal.text:
                await zelzal.click(text='Download')
                await asyncio.sleep(5)
                zelzal = await conv.get_response()
                resources = zelzal.text
                if "above 50MB" in zelzal.text:
                    aa = resources.replace(".apk filesize is above 50MB so you can download only using link", "**- حجم التطبيق اكبر من 50MB ؟!\n- قم بتحميل التطبيق عبـر البوت\n- ادخل للبوت @uploadbot وارسل الرابـط بالاسفـل**\n\n") 
                    zz = aa.replace(" if you still want it as file copy the link and send to @UploadBot", "\n\n**- قنـاة السـورس : @yamen**") 
                    await event.delete()
                    return await borg.send_message(event.chat_id, zz)
                await event.delete()
                await borg.send_file(
                    event.chat_id,
                    zelzal,
                    caption=f"**{zelzal.text}\nBy: @yamen**",
                )

            else:
                await event.edit("**- لـم استطـع العثـور على نتائـج ؟!**\n**- حـاول مجـدداً في وقت لاحـق ...**")
        except YouBlockedUserError:
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message(d_link)
            await asyncio.sleep(3)
            zelzal = await conv.get_response()
            if "Version:" in zelzal.text:
                await zelzal.click(text='Download')
                await asyncio.sleep(5)
                zelzal = await conv.get_response()
                resources = zelzal.text
                if "above 50MB" in zelzal.text:
                    aa = resources.replace(".apk filesize is above 50MB so you can download only using link", "**- حجم التطبيق اكبر من 50MB ؟!\n- قم بتحميل التطبيق عبـر البوت\n- ادخل للبوت @uploadbot وارسل الرابـط بالاسفـل**\n\n") 
                    zz = aa.replace(" if you still want it as file copy the link and send to @UploadBot", "\n\n**- قنـاة السـورس : @yamen**") 
                    await event.delete()
                    return await borg.send_message(event.chat_id, zz)
                await event.delete()
                await borg.send_file(
                    event.chat_id,
                    zelzal,
                    caption=f"**{zelzal.text}\nBy: @yamen**",
                )

            else:
                await event.edit("**- لـم استطـع العثـور على نتائـج ؟!**\n**- حـاول مجـدداً في وقت لاحـق ...**")




@zedub.zed_cmd(pattern="رابط(?:\s|$)([\s\S]*)")
async def song2(event):
    song = event.pattern_match.group(1)
    chat = "@apkdl_bot" # code by t.me/zzzzl1l
    reply_id_ = await reply_id(event)
    zed = await edit_or_reply(event, "**    ⃟⁞⃟⟢ ╎جـارِ البحث عن روابـط التطبيق ...**")
    async with event.client.conversation(chat) as conv:
        try:
            await conv.send_message(song)
        except YouBlockedUserError:
            await zedub(unblock("apkdl_bot"))
            await conv.send_message(song)
        await asyncio.sleep(5)
        response = await conv.get_response()
        await event.client.send_read_acknowledge(conv.chat_id)
        await event.client.send_message(event.chat_id, f"**- قم بالضغـط ع اول رابـط يبـدأ ب /preview\n- ثم ارسـل .تطبيق بالـرد ع الرابـط**\n\n{response.message}")
        await zed.delete()



@zedub.zed_cmd(
    pattern="فلم ([\s\S]*)",
    command=("فلم", plugin_category),
    info={
        "header": "لـ البحـث عـن الافـلام",
        "الاستـخـدام": "{tr}فلم + اسم",
    },
)
async def zed(event):
    if event.fwd_from:
        return
    zedr = event.pattern_match.group(1)
    zelzal = "@TGFilmBot"
    if event.reply_to_msg_id:
        await event.get_reply_message()
    tap = await bot.inline_query(zelzal, zedr)
    await tap[0].click(event.chat_id)
    await event.delete()


