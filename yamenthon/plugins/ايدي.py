


import contextlib
import html
import os
import base64
import aiohttp

from telethon.tl.functions.messages import ImportChatInviteRequest as Get
from telethon.tl.types import MessageEntityMentionName

from requests import get
from telethon.tl.functions.photos import GetUserPhotosRequest
from telethon.tl.functions.users import GetFullUserRequest

from yamenthon import zedub
from yamenthon.core.logger import logging

from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete
from ..helpers import reply_id
from ..sql_helper.globals import gvarstatus
from . import spamwatch

plugin_category = "العروض"
LOGS = logging.getLogger(__name__)

ZED_TEXT = gvarstatus("CUSTOM_ALIVE_TEXT") or "•⎚• مـعلومـات المسـتخـدم مـن سورس يـــمنثون"
ZEDM = gvarstatus("CUSTOM_ALIVE_EMOJI") or "✦ "
ZEDF = gvarstatus("CUSTOM_ALIVE_FONT") or "⋆─┄─┄─┄─ يـــمنثون ─┄─┄─┄─⋆"
zed_dev = ( 6669024587, 6669024587)
zel_dev = (6669024587, 6669024587)
zelzal = (5571722913, 5571722913)


async def get_user_from_event(event):
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        user_object = await event.client.get_entity(previous_message.sender_id)
    else:
        user = event.pattern_match.group(1)
        if user.isnumeric():
            user = int(user)
        if not user:
            self_user = await event.client.get_me()
            user = self_user.id
        if event.message.entities:
            probable_user_mention_entity = event.message.entities[0]
            if isinstance(probable_user_mention_entity, MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj
        if isinstance(user, int) or user.startswith("@"):
            user_obj = await event.client.get_entity(user)
            return user_obj
        try:
            user_object = await event.client.get_entity(user)
        except (TypeError, ValueError) as err:
            await event.edit(str(err))
            return None
    return user_object


async def fetch_info(replied_user, event):
    user = replied_user  # تعريف user بناءً على الباراميتر اللي وصل
    """Get details from the User object."""
    FullUser = (await event.client(GetFullUserRequest(replied_user.id))).full_user
    replied_user_profile_photos = await event.client(
        GetUserPhotosRequest(user_id=replied_user.id, offset=42, max_id=0, limit=80)
    )
    replied_user_profile_photos_count = "لا يـوجـد بروفـايـل"
    dc_id = "Can't get dc id"
    with contextlib.suppress(AttributeError):
        replied_user_profile_photos_count = replied_user_profile_photos.count
        dc_id = replied_user.photo.dc_id
    user_id = replied_user.id
    first_name = replied_user.first_name
    full_name = FullUser.private_forward_name
    common_chat = FullUser.common_chats_count
    username = replied_user.username
    user_bio = FullUser.about
    is_bot = replied_user.bot
    restricted = replied_user.restricted
    verified = replied_user.verified
    resources = (await event.client.get_entity(user_id)).premium
    photo = await event.client.download_profile_photo(
        user_id,
        Config.TMP_DOWNLOAD_DIRECTORY + str(user_id) + ".jpg",
        download_big=True,
    )
    # جلب تاريخ إنشاء الحساب من API خارجي
    creation_date = "❌ غير معـروف"
    API_URL = "https://restore-access.indream.app/regdate"
    API_KEY = "e758fb28-79be-4d1c-af6b-066633ded128"
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "x-api-key": API_KEY,
                "Content-Type": "application/json"
            }
            payload = {"telegramId": user_id}
            async with session.post(API_URL, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    date = result.get("data", {}).get("date")
                    if date:
                        creation_date = date
    except Exception:
        pass

    is_premium = "بـريميـوم 🌟" if getattr(user, "premium", False) else "بـريميـوم ❎️"

    rmsg = await bot.get_messages(event.chat_id, 0, from_user=user_id) 
    rrr = rmsg.total
    if rrr < 100: 
        baqr = "غير متفاعل  🗿"
    elif rrr > 200 and rrr < 500:
        baqr = "ضعيف  🗿"
    elif rrr > 500 and rrr < 700:
        baqr = "شد حيلك  🏇"
    elif rrr > 700 and rrr < 1000:
        baqr = "ماشي الحال  🏄🏻‍♂"
    elif rrr > 1000 and rrr < 2000:
        baqr = "ملك التفاعل  🎖"
    elif rrr > 2000 and rrr < 3000:
        baqr = "امبراطور التفاعل  🥇"
    elif rrr > 3000 and rrr < 4000:
        baqr = "غنبله  💣"
    else:
        baqr = "نار وشرر  🏆"
    first_name = (
        first_name.replace("\u2060", "")
        if first_name
        else ("هذا المستخدم ليس له اسم أول")
    )
    full_name = full_name or first_name
    username = "@{}".format(username) if username else ("لا يـوجـد")
    user_bio = "لا يـوجـد" if not user_bio else user_bio

    if user_id in zelzal: 
        rotbat = "⌁ مطـور السـورس 𓄂𓆃 ⌁" 
    elif user_id in zel_dev:
        rotbat = "⌁ مطـور مسـاعـد 𐏕⌁" 
    elif user_id == (await event.client.get_me()).id and user_id not in zed_dev:
        rotbat = "⌁ مـالك الحساب 𓀫 ⌁" 
    else:
        rotbat = "⌁ العضـو 𓅫 ⌁"

    # اجعل بناء caption داخل الدالة أيضًا
    caption = f"<b> {ZED_TEXT} </b>\n"
    caption += f"ٴ<b>{ZEDF}</b>\n"
    caption += f"<b>{ZEDM}الاسـم    ⇠ </b> "
    caption += f'<a href="tg://user?id={user_id}">{full_name}</a>'
    caption += f"\n<b>{ZEDM}المعـرف  ⇠  {username}</b>"
    caption += f"\n<b>{ZEDM}الايـدي   ⇠ </b> <code>{user_id}</code>\n"
    caption += f"<b>{ZEDM}الرتبـــه   ⇠ {rotbat} </b>\n"
    caption += f"<b>{ZEDM}الحسـاب   ⇠</b>  {is_premium}\n"
    caption += f"<b>{ZEDM}الصـور    ⇠ </b> {replied_user_profile_photos_count} 🏞\n"
    if user_id != (await event.client.get_me()).id: 
        caption += f"<b>{ZEDM}الـمجموعات المشتـركة ⇠ </b> {common_chat} 🛰 \n"
    caption += f"<b>{ZEDM}تـاريخ الإنشـاء     ⇠  {creation_date} 📆</b> \n"
    caption += f"<b>{ZEDM}الرسائل   ⇠</b>  {rrr}  💌\n"
    caption += f"<b>{ZEDM}التفاعل   ⇠</b>  {baqr}\n"
    caption += f"<b>{ZEDM}البايـو     ⇠  {user_bio}</b> \n"
    caption += f"ٴ<b>{ZEDF}</b>"
    return photo, caption


@zedub.zed_cmd(
    pattern="ايدي(?: |$)(.*)",
    command=("ايدي", plugin_category),
    info={
        "header": "لـ عـرض معلومـات الشخـص",
        "الاستـخـدام": " {tr}ايدي بالـرد او {tr}ايدي + معـرف/ايـدي الشخص",
    },
)
async def who(event):
    "Gets info of an user"
    zed = await edit_or_reply(event, "⇆")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    replied_user = await get_user_from_event(event)
    try:
        photo, caption = await fetch_info(replied_user, event)
    except (AttributeError, TypeError):
        return await edit_or_reply(zed, "**- لـم استطـع العثــور ع الشخــص ؟!**")
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    try:
        await event.client.send_file(
            event.chat_id,
            photo,
            caption=caption,
            link_preview=False,
            force_document=False,
            reply_to=message_id_to_reply,
            parse_mode="html",
        )
        if not photo.startswith("http"):
            os.remove(photo)
        await zed.delete()
    except TypeError:
        await zed.edit(caption, parse_mode="html")


@zedub.zed_cmd(
    pattern="ا(?: |$)(.*)",
    command=("ا", plugin_category),
    info={
        "header": "امـر مختصـر لـ عـرض معلومـات الشخـص",
        "الاستـخـدام": " {tr}ا بالـرد او {tr}ا + معـرف/ايـدي الشخص",
    },
)
async def who(event):
    "Gets info of an user"
    zed = await edit_or_reply(event, "⇆")
    if not os.path.isdir(Config.TMP_DOWNLOAD_DIRECTORY):
        os.makedirs(Config.TMP_DOWNLOAD_DIRECTORY)
    replied_user = await get_user_from_event(event)
    try:
        photo, caption = await fetch_info(replied_user, event)
    except (AttributeError, TypeError):
        return await edit_or_reply(zed, "**- لـم استطـع العثــور ع الشخــص ؟!**")
    message_id_to_reply = event.message.reply_to_msg_id
    if not message_id_to_reply:
        message_id_to_reply = None
    try:
        await event.client.send_file(
            event.chat_id,
            photo,
            caption=caption,
            link_preview=False,
            force_document=False,
            reply_to=message_id_to_reply,
            parse_mode="html",
        )
        if not photo.startswith("http"):
            os.remove(photo)
        await zed.delete()
    except TypeError:
        await zed.edit(caption, parse_mode="html")


@zedub.zed_cmd(
    pattern="صورته(?:\s|$)([\s\S]*)",
    command=("صورته", plugin_category),
    info={
        "header": "لـ جـلب بـروفـايـلات الشخـص",
        "الاستـخـدام": [
            "{tr}صورته + عدد",
            "{tr}صورته الكل",
            "{tr}صورته",
        ],
    },
)
async def potocmd(event):
    "To get user or group profile pic"
    uid = "".join(event.raw_text.split(maxsplit=1)[1:])
    user = await event.get_reply_message()
    chat = event.input_chat
    if user and user.sender:
        photos = await event.client.get_profile_photos(user.sender)
        u = True
    else:
        photos = await event.client.get_profile_photos(chat)
        u = False
    if uid.strip() == "":
        uid = 1
        if int(uid) > (len(photos)):
            return await edit_delete(
                event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **"
            )
        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    elif uid.strip() == "الكل":
        if len(photos) > 0:
            await event.client.send_file(event.chat_id, photos)
        else:
            try:
                if u:
                    photo = await event.client.download_profile_photo(user.sender)
                else:
                    photo = await event.client.download_profile_photo(event.input_chat)
                await event.client.send_file(event.chat_id, photo)
            except Exception:
                return await edit_delete(event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **")
    else:
        try:
            uid = int(uid)
            if uid <= 0:
                await edit_or_reply(
                    event, "**- رقـم خـاطـئ . . .**"
                )
                return
        except BaseException:
            await edit_or_reply(event, "**- رقـم خـاطـئ . . .**")
            return
        if int(uid) > (len(photos)):
            return await edit_delete(
                event, "**- لا يـوجـد هنـاك صـور لهـذا الشخـص ؟! **"
            )

        send_photos = await event.client.download_media(photos[uid - 1])
        await event.client.send_file(event.chat_id, send_photos)
    await event.delete()

















