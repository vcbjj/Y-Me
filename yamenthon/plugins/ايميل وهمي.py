

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
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import reply_id

plugin_category = "البوت"



@zedub.zed_cmd(pattern="بريد$")
async def zelzal_gpt(event):
    chat = "@TeMail_Robot" 
    zed = await edit_or_reply(event, "**𓆰جـار إنشـاء ايميـل وهمـي 📧...**")
    async with borg.conversation(chat) as conv: 
        try:
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message("📧 Generate Email")
            await asyncio.sleep(5)
            yamen = await conv.get_response()
            malath = yamen.text
            if "📧 Your temporary email" in yamen.text:
                aa = malath.replace("📧 Your temporary email address:", "**𓆰تم انشـاء Email وهمـي بنجـاح ☑️\n𓆰الإيمـيل الوهمـي الخـاص بك هـو 📧 :**") 
                await zed.delete()
                await borg.send_message(event.chat_id, aa)
        except YouBlockedUserError:
            await zedub(unblock("TeMail_Robot"))
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message("📧 Generate Email")
            await asyncio.sleep(5)
            yamen = await conv.get_response()
            malath = yamen.text
            if "📧 Your temporary email" in yamen.text:
                aa = malath.replace("📧 Your temporary email address:", "**𓆰تم انشـاء Email وهمـي بنجـاح ☑️\n𓆰الإيمـيل الوهمـي الخـاص بك هـو 📧 :**") 
                await zed.delete()
                await borg.send_message(event.chat_id, aa)



#YamenThon
@zedub.zed_cmd(pattern="الوارد$")
async def zelzal_gpt(event):
    chat = "@TeMail_Robot" #YamenThon
    zed = await edit_or_reply(event, "**𓆰جـار جلب رسائـل البريـد 📬...**")
    async with borg.conversation(chat) as conv: #YamenThon
        try:
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message("📫 تحقق من OTP")
            await asyncio.sleep(5)
            yamen = await conv.get_response()
            malath = yamen.text
            if "❌ No OTP" in yamen.text:
                aa = malath.replace("❌ لم يتم استلام OTP...", "**𓆰لا يوجـد رسـالة واردة لبريـدك الوهمـي بعـد 📭❌**") 
                await zed.delete()
                return await borg.send_message(event.chat_id, aa)
            if "📬 Inbox" in yamen.text:
                await zed.delete()
                return await borg.send_message(event.chat_id, f"**{malath}**\n\n───────────────────\n𝙔𝘼𝙈   ⃟⁞⃟⟢ 𝗨**ꜱᴇʀʙᴏᴛ** 𝗧**ᴏᴏʟꜱ**\n\t\t\t\t\t\t\t\tmail • البـريد الـوارد")
            await zed.delete()
            await borg.send_message(event.chat_id, f"**{malath}**\n\n───────────────────\n𝙔𝘼𝙈   ⃟⁞⃟⟢  𝗨**ꜱᴇʀʙᴏᴛ** 𝗧**ᴏᴏʟꜱ**\n\t\t\t\t\t\t\t\tmail • البـريد الـوارد")
        except YouBlockedUserError:
            await zedub(unblock("TeMail_Robot"))
            await conv.send_message("/start")
            await conv.get_response()
            await conv.send_message("📫 تحقق من OTP")
            await asyncio.sleep(5)
            yamen = await conv.get_response()
            malath = yamen.text
            if "❌ No OTP" in yamen.text:
                aa = malath.replace("❌ لم يتم استلام OTP...", "**𓆰لا يوجـد رسـالة واردة لبريـدك الوهمـي بعـد 📭❌**") 
                await zed.delete()
                return await borg.send_message(event.chat_id, aa)
            if "📬 Inbox" in yamen.text:
                await zed.delete()
                return await borg.send_message(event.chat_id, f"**{malath}**\n\n───────────────────\n𝙔𝘼𝙈   ⃟⁞⃟⟢ 𝗨**ꜱᴇʀʙᴏᴛ** 𝗧**ᴏᴏʟꜱ**\n\t\t\t\t\t\t\t\tmail • البـريد الـوارد")
            await zed.delete()
            await borg.send_message(event.chat_id, f"**{malath}**\n\n───────────────────\n𝙔𝘼𝙈   ⃟⁞⃟⟢ 𝗨**ꜱᴇʀʙᴏᴛ** 𝗧**ᴏᴏʟꜱ**\n\t\t\t\t\t\t\t\mail • البـريد الـوارد")

