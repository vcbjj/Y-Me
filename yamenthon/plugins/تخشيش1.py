import os
import shutil
from asyncio import sleep
import random

from telethon import events

from yamenthon import zedub
from yamenthon.core.logger import logging
from ..Config import Config
from ..core.managers import edit_or_reply, edit_delete
from ..helpers import reply_id, get_user_from_event
from . import BOTLOG, BOTLOG_CHATID
plugin_category = "الادوات"
LOGS = logging.getLogger(__name__)


async def ge(user, event):
    if isinstance(user, str):
        user = int(user)
    try:
        user_obj = await event.client.get_entity(user)
    except (TypeError, ValueError) as err:
        await event.edit(str(err))
        return None
    return user_obj

zel_dev = (6669024587,)


import random

from telethon import events





@zedub.zed_cmd(pattern="رفع مرتي(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"🚻 ** ᯽︙  المستخدم => • ** [{zedth2}](tg://user?id={user.id}) \n ☑️ **᯽︙  تم رفعها مرتك بواسطه  :**{my_mention} 👰🏼‍♀️.\n**᯽︙  يلا حبيبي امشي نخلف بيبي 👶🏻🤤** ")

@zedub.zed_cmd(pattern="رفع كلب(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه كلب 🐶 بواسطة :** {my_mention} \n**᯽︙  خليه خله ينبح 😂**")

@zedub.zed_cmd(pattern="رفع تاج(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"᯽︙ المستخدم [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه تاج بواسطة :** {my_mention} 👑🔥")
@zedub.zed_cmd(pattern="رفع قرد(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"᯽︙ المستخدم [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه قرد واعطائه موزة 🐒🍌 بواسطة :** {my_mention}")

@zedub.zed_cmd(pattern="رفع بكلبي(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه بكلـبك 🤍 بواسطة :** {my_mention} \n**᯽︙  انت حبي الابدي 😍**")
    
    

@zedub.zed_cmd(pattern="رفع مطي(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه مطي 🐴 بواسطة :** {my_mention} \n**᯽︙  تعال حبي استلم  انه **")
    



@zedub.zed_cmd(pattern="رفع زوجي(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه زوجج بواسطة :** {my_mention} \n**᯽︙  يلا حبيبي امشي نخلف 🤤🔞**")
    

@zedub.zed_cmd(pattern="رفع زاحف(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفع المتهم زاحف اصلي بواسطة :** {my_mention} \n**᯽︙  ها يلزاحف شوكت تبطل سوالفك حيوان 😂🐍**")

@zedub.zed_cmd(pattern="رفع كحبة(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفع المتهم كحبة 👙 بواسطة :** {my_mention} \n**᯽︙  ها يلكحبة طوبز خلي انيجك/ج**")

@zedub.zed_cmd(pattern="رفع فرخ(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه فرخ الكروب بواسطة :** {my_mention} \n**᯽︙  لك الفرخ استر على خمستك ياهو اليجي يزورهاً 👉🏻👌🏻**")

@zedub.zed_cmd(pattern="رفع حاته(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـها حاته الكروب 🤤😻 بواسطة :** {my_mention} \n**᯽︙  تعاي يعافيتي اريد حضن دافي 😽**")

@zedub.zed_cmd(pattern="رفع هايشة(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه المتهم هايشة 🐄 بواسطة :** {my_mention} \n**᯽︙  ها يلهايشة خوش بيك حليب تعال احلبك 😂**")

@zedub.zed_cmd(pattern="رفع صاك(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه صاك 🤤 بواسطة :** {my_mention} \n**᯽︙  تعال يلحلو انطيني بوسة من رگبتك 😻🤤**")

@zedub.zed_cmd(
    pattern="مصه(?:\s|$)([\s\S]*)",
    command=("مصه", plugin_category),
)
async def permalink(mention): 
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . بلا مفتاله حقك هاذا مطور السورس يا مجنون😒  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . بلا مفتاله حقك هاذا مطور السورس يا مجنون😒  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . بلا مفتاله حقك هاذا مطور السورس يا مجنون😒  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    await edit_or_reply(mention, f"** ⣠⡶⠚⠛⠲⢄⡀\n⣼⠁      ⠀⠀⠀⠳⢤⣄\n⢿⠀⢧⡀⠀⠀⠀⠀⠀⢈⡇\n⠈⠳⣼⡙⠒⠶⠶⠖⠚⠉⠳⣄\n⠀⠀⠈⣇⠀⠀⠀⠀⠀⠀⠀⠈⠳⣄\n⠀⠀⠀⠘⣆       ⠀⠀⠀⠀⠀⠈⠓⢦⣀\n⠀⠀⠀⠀⠈⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⠲⢤\n⠀⠀⠀⠀⠀⠀⠙⢦⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢧\n⠀⠀⠀⠀⠀⠀⠀    ⠓⠦⠀⠀⠀⠀**\n**🚹 ¦ تعال مصه عزيزي ** [{zedth2}](tg://user?id={user.id})")

@zedub.zed_cmd(pattern="سيد(?: |$)(.*)")
async def permalink(mention):
    await edit_or_reply(mention, f"سماحة السيد الاسطوره عاشق الصمت مطور سورس يمنثون @T_A_Tl")

@zedub.zed_cmd(pattern="رفع ايجة(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه ايچة 🤤 بواسطة :** {my_mention} \n**᯽︙  ها يلأيچة تطلعين درب بـ$25 👙**")

@zedub.zed_cmd(pattern="رفع زبال(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعـه زبال الكروب 🧹 بواسطة :** {my_mention} \n**᯽︙  تعال يلزبال اكنس الكروب لا أهينك 🗑😹**")

@zedub.zed_cmd(pattern="رفع كواد(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعه كواد بواسطة :** {my_mention} \n**᯽︙  تعال يكواد عرضك مطشر اصير حامي عرضك ؟😎**")

@zedub.zed_cmd(pattern="رفع ديوث(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ المستخدم** [{zedth2}](tg://user?id={user.id}) \n**᯽︙  تـم رفعه ديوث الكروب بواسطة :** {my_mention} \n**᯽︙  تعال يلديوث جيب اختك خلي اتمتع وياها 🔞**")

@zedub.zed_cmd(pattern="رفع مميز(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ الحلو** 「[{zedth2}](tg://user?id={user.id})」 \n**᯽︙  تـم رفعه مميز بواسطة :** {my_mention}")

@zedub.zed_cmd(pattern="رفع ادمن(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ الحلو** 「[{zedth2}](tg://user?id={user.id})」 \n**᯽︙  تـم رفعه ادمن بواسطة :** {my_mention}")

@zedub.zed_cmd(pattern="رفع منشئ(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ الحلو** 「[{zedth2}](tg://user?id={user.id})」 \n**᯽︙  تـم رفعه منشئ بواسطة :** {my_mention}")

@zedub.zed_cmd(pattern="رفع مالك(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙ الحلو** 「[{zedth2}](tg://user?id={user.id})」 \n**᯽︙  تـم رفعه مالك الكروب بواسطة :** {my_mention}")

@zedub.zed_cmd(pattern="رفع مجنب(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f" ** ᯽︙  المستخدم => • ** [{zedth2}](tg://user?id={user.id}) \n ☑️ **᯽︙  تم رفعه مجنب بواسطه  :**{my_mention} .\n**᯽︙  كوم يلمجنب اسبح مو عيب تضرب جلغ 😹** ")

@zedub.zed_cmd(pattern="رفع وصخ(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"** ᯽︙  المستخدم => • ** [{zedth2}](tg://user?id={user.id}) \n ☑️ **᯽︙  تم رفعه وصخ الكروب 🤢 بواسطه  :**{my_mention} .\n**᯽︙  لك دكوم يلوصخ اسبح مو ريحتك كتلتنا 🤮 ** ")

@zedub.zed_cmd(pattern="زواج(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"᯽︙ ** لقد تم زواجك/ج من : **[{zedth2}](tg://user?id={user.id}) 💍\n**᯽︙  الف الف مبروك الان يمكنك اخذ راحتك ** ")

@zedub.zed_cmd(pattern="طلاك(?: |$)(.*)")
async def zed(mention):
    user, custom = await get_user_from_event(mention)
    if not user:
        return
    if user.id in zel_dev:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا احـد المطـورين المساعديـن  ❏╰**")
    if user.id == 5571722913:
        return await edit_or_reply(mention, f"**╮ ❐ لك دي . . هـذا مطـور السـورس  ❏╰**")
    zedth2 = user.first_name.replace("\u2060", "") if user.first_name else user.username
    me = await mention.client.get_me()
    my_first = me.first_name
    my_mention = f"[{me.first_name}](tg://user?id={me.id})"
    await edit_or_reply(
        mention,
        f"**᯽︙  انتِ [{zedth2}](tg://user?id={user.id}) طالق طالق طالق 🙎🏻‍♂️ من  :**{my_mention} .\n**᯽︙  لقد تم طلاقها بلثلاث وفسخ زواجكما الان الكل حر طليق ** ")
