import json
import os
import asyncio
from telethon.errors import YouBlockedUserError
from yamenthon import zedub
from ..utils import is_admin
from ..helpers.utils import _format
from ..core.managers import edit_delete, edit_or_reply
from ..helpers import get_user_from_event, sanga_seperator

START_FLAG_FILE = os.path.join(os.path.dirname(__file__), "sangmata_started.json")

def has_started():
    return os.path.exists(START_FLAG_FILE)

def set_started():
    try:
        with open(START_FLAG_FILE, "w") as f:
            json.dump({"started": True}, f)
    except Exception:
        pass

@zedub.zed_cmd(pattern="الاسماء(ألف)?(?:\s|$)([\s\S]*)")
async def _(event):
    input_str = "".join(event.text.split(maxsplit=1)[1:])
    reply_message = await event.get_reply_message()
    if not input_str and not reply_message:
        return await edit_delete(event, "**♛ ⦙ قم بالـرد على رسالـة لمستخـدم ...**")

    user, rank = await get_user_from_event(event, secondgroup=True)
    if not user:
        return

    uid = user.id
    chat = "@SangMata_BOT"
    zedevent = await edit_or_reply(event, "**♛ ⦙ جـاري المعالجـة ↯**")

    async with event.client.conversation(chat) as conv:
        try:
            if not has_started():
                await conv.send_message("/start")
                await asyncio.sleep(0.5)
                set_started()

            await conv.send_message(str(uid))

        except YouBlockedUserError:
            return await edit_delete(event, "**♛ ⦙ قم بإلغـاء حظـر @SangMata_BOT ثم حـاول !!**")
        except Exception as e:
            return await edit_delete(event, f"**♛ ⦙ حدث خطأ: {str(e)}**")

        responses = []
        while True:
            try:
                response = await conv.get_response(timeout=9)
            except asyncio.TimeoutError:
                break
            responses.append(response.text)

        await event.client.send_read_acknowledge(conv.chat_id)

    if not responses:
        return await edit_delete(event, "**♛ ⦙ لا يستطيـع البـوت جلـب النتائـج ⚠️**")
    if "No records found" in responses:
        return await edit_delete(event, "**♛ ⦙ المستخـدم ليـس لديـه أيّ سجـل ✕**")

    names, usernames = await sanga_seperator(responses)
    cmd = event.pattern_match.group(1)
    sandy = None
    check = usernames if cmd == "u" else names
    for i in check:
        if sandy:
            await event.reply(i, parse_mode=_format.parse_pre)
        else:
            sandy = True
            await zedevent.edit(i, parse_mode=_format.parse_pre)
