from telethon import events
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest, GetFullChatRequest
from telethon.tl.functions.stories import CanSendStoryRequest, SendStoryRequest
from telethon.tl.types import InputPrivacyValueAllowAll
from telethon.tl.types import MessageActionChannelMigrateFrom, ChannelParticipantsAdmins, User, UserFull
from telethon.errors import ChannelInvalidError, ChannelPrivateError, ChannelPublicGroupNaError
from telethon.utils import get_input_location
from datetime import datetime
from emoji import emojize
from math import sqrt
import os
from contextlib import suppress
from telethon.tl.functions.users import GetFullUserRequest
from telethon.events import NewMessage
import aiohttp

from yamenthon import zedub
from ..core.managers import edit_or_reply

plugin_category = "الادمن"

API_URL = "https://restore-access.indream.app/regdate"
API_KEY = "e758fb28-79be-4d1c-af6b-066633ded128"

@zedub.zed_cmd(pattern="كشف المجموعة(?: |$)(.*)")
async def info_group(event):
    reply = await edit_or_reply(event, "`جارٍ الفحص ...`")
    chat = await get_chatinfo(event, reply)
    if chat is None:
        return
    caption = await fetch_info(chat, event)
    try:
        await reply.edit(caption, parse_mode="html")
    except Exception:
        await reply.edit("حدث خطأ أثناء عرض النتائج.")


async def get_chatinfo(event, reply):
    chat = event.pattern_match.group(1)
    if not chat and event.reply_to_msg_id:
        replied = await event.get_reply_message()
        if replied.fwd_from and replied.fwd_from.channel_id:
            chat = replied.fwd_from.channel_id
    if not chat:
        chat = event.chat_id
    try:
        return await event.client(GetFullChatRequest(chat))
    except:
        try:
            return await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await reply.edit("`خطأ: القناة أو المجموعة غير صالحة.`")
        except ChannelPrivateError:
            await reply.edit("`خطأ: هذه مجموعة/قناة خاصة أو تم حظرك منها.`")
        except ChannelPublicGroupNaError:
            await reply.edit("`خطأ: المجموعة أو القناة غير موجودة.`")
        return None


async def fetch_info(chat, event):
    obj = await event.client.get_entity(chat.full_chat.id)
    broadcast = getattr(obj, "broadcast", False)
    chat_type = "قناة" if broadcast else "مجموعة"
    title = obj.title
    warn = emojize(":warning:")
    try:
        history = await event.client(GetHistoryRequest(
            peer=obj.id,
            offset_id=0,
            offset_date=datetime(2010, 1, 1),
            add_offset=-1,
            limit=1,
            max_id=0,
            min_id=0,
            hash=0
        ))
    except:
        history = None

    msg_valid = history and history.messages and history.messages[0].id == 1
    creator_valid = msg_valid and history.users
    creator_id = history.users[0].id if creator_valid else None
    creator_name = history.users[0].first_name if creator_valid else "حساب محذوف"
    creator_username = history.users[0].username if creator_valid else None
    created = history.messages[0].date if msg_valid else None
    former_title = (
        history.messages[0].action.title
        if msg_valid and isinstance(history.messages[0].action, MessageActionChannelMigrateFrom)
        and history.messages[0].action.title != title
        else None
    )
    try:
        dc_id, _ = get_input_location(chat.full_chat.chat_photo)
    except:
        dc_id = "غير معروف"

    desc = chat.full_chat.about
    members = getattr(chat.full_chat, "participants_count", getattr(obj, "participants_count", None))
    admins = getattr(chat.full_chat, "admins_count", None)
    banned = getattr(chat.full_chat, "kicked_count", None)
    restricted = getattr(chat.full_chat, "banned_count", None)
    online = getattr(chat.full_chat, "online_count", 0)
    stickers = chat.full_chat.stickerset.title if chat.full_chat.stickerset else None
    msg_count = history.count if history else None
    sent_msgs = getattr(chat.full_chat, "read_inbox_max_id", None)
    alt_sent = getattr(chat.full_chat, "read_outbox_max_id", None)
    exp = getattr(chat.full_chat, "pts", None)
    username = f"@{obj.username}" if getattr(obj, "username", None) else None
    bots = len(chat.full_chat.bot_info) if chat.full_chat.bot_info else 0

    if admins is None:
        try:
            result = await event.client(GetParticipantsRequest(
                channel=chat.full_chat.id,
                filter=ChannelParticipantsAdmins(),
                offset=0,
                limit=0,
                hash=0
            ))
            admins = result.count
        except:
            pass

    caption = "🔹 <b>𓋼 معلومات المجموعة/القناة 𓋼</b>\n"
    caption += "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    caption += f"🆔┊ <b>المعرف:</b> <code>{obj.id}</code>\n"
    caption += f"📛┊ <b>الاسم:</b> {title}\n"
    if former_title:
        caption += f"♻️┊ <b>الاسم السابق:</b> {former_title}\n"
    caption += f"🔐┊ <b>النوع:</b> {'عامة 🌐' if username else 'خاصة 🔒'}\n"
    if username:
        caption += f"🔗┊ <b>الرابط:</b> @{username}\n"
    if creator_username:
        caption += f"👑┊ <b>المنشئ:</b> @{creator_username}\n"
    elif creator_valid:
        caption += f"👑┊ <b>المنشئ:</b> <a href=\"tg://user?id={creator_id}\">{creator_name}</a>\n"
    if created:
        caption += f"📅┊ <b>تاريخ الإنشاء:</b> <code>{created.strftime('%b %d, %Y - %H:%M:%S')}</code>\n"
    caption += f"🏢┊ <b>مركز البيانات:</b> {dc_id}\n"
    if exp:
        level = int((1 + sqrt(1 + 7 * exp / 14)) / 2)
        caption += f"📊┊ <b>المستوى:</b> <code>{level} ⭐</code>\n"
    if msg_count:
        caption += f"📨┊ <b>الرسائل الظاهرة:</b> <code>{msg_count}</code>\n"
    if sent_msgs:
        caption += f"✉️┊ <b>الرسائل المرسلة:</b> <code>{sent_msgs}</code>\n"
    elif alt_sent:
        caption += f"✉️┊ <b>الرسائل المرسلة:</b> <code>{alt_sent}</code> {warn}\n"
    if members:
        caption += f"👥┊ <b>الأعضاء:</b> <code>{members}</code>\n"
    if admins:
        caption += f"🛡️┊ <b>المشرفون:</b> <code>{admins}</code>\n"
    if bots:
        caption += f"🤖┊ <b>البوتات:</b> <code>{bots}</code>\n"
    if online:
        caption += f"🟢┊ <b>المتصلون الآن:</b> <code>{online}</code>\n"
    if restricted:
        caption += f"⚠️┊ <b>المقيدون:</b> <code>{restricted}</code>\n"
    if banned:
        caption += f"🚫┊ <b>المحظورون:</b> <code>{banned}</code>\n"
    if stickers:
        caption += f"🎭┊ <b>الملصقات:</b> {stickers}\n"
    if desc:
        caption += f"\n📝┊ <b>الوصف:</b>\n<code>{desc}</code>\n"
    caption += "\n━━━━━━━━━━━━━━━━━━━━━━"
    return caption

@zedub.zed_cmd(pattern="ستوري(?: |$)(.*)")
async def stories(event):
    replied = await event.get_reply_message()
    reply = await edit_or_reply(event, "**⌔∮ جار تنزيل الستوري يرجى الانتظار �♥️**")
    try:
        username = event.pattern_match.group(1).strip()
    except:
        username = None
    
    if not username:
        if replied and isinstance(replied.sender, User):
            username = replied.sender_id
        else:
            return await reply.edit("**⌔∮ يجب عليك وضع يوزر المستخدم لتنزيل الستوري الخاص به**🧸♥️")
    
    with suppress(ValueError):
        username = int(username)
    
    try:
        full_user = (await event.client(GetFullUserRequest(id=username))).full_user
    except Exception as er:
        await reply.edit(f"**❃ خطأ : {er}**")
        return
    
    stories = full_user.stories
    if not (stories and stories.stories):
        await reply.edit("**⌔∮ لم يتم العثور على ستوري خاص بالمستخدم**🧸♥️")
        return
    
    for story in stories.stories:
        client = event.client
        file = await client.download_media(story.media)
        await event.reply(
            story.caption,
            file=file
        )
        os.remove(file)
    
    await reply.edit("**⌔∮ تم بنجاح تحميل الستوري ✅**")

@zedub.zed_cmd(pattern="الانشا(?:ء)?$")
async def تاريخ_الانشاء(event):
    if not event.is_reply:
        return await edit_or_reply(event, "**⌔∮ يجب الرد على رسالة المستخدم لمعرفة تاريخ الإنشاء**")
    
    reply_msg = await event.get_reply_message()
    user = await reply_msg.get_sender()

    if not user or not user.id:
        return await edit_or_reply(event, "❌ لا يمكن معرفة المستخدم.")

    user_id = int(user.id)

    reply = await edit_or_reply(event, "⏳ جارٍ التحقق من تاريخ الإنشاء...")

    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                "x-api-key": API_KEY,
                "Content-Type": "application/json"
            }
            payload = {
                "telegramId": user_id
            }
            async with session.post(API_URL, json=payload, headers=headers) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    date = result.get("data", {}).get("date")
                    if date:
                        await reply.edit(f"""
✨ **⏳ تـاريـخ إنـشـاء الـحـسـاب ⏳** ✨

▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰  
🗓️ **التـاريـخ:** `{date}`  
▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰▰  

🌌 **سورس يـــمنثون:** ✓

⚡ **قنـاة الـسـورس:**  
↳ [𓏺 𝙎𝙊𝙐𝙍𝘾𝞝 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉](t.me/YamenThon)  

🔮 **تـم جـلـب الـبيـانـات بـأحـدث الـتـقـنـيـات**  
""")
                    else:
                        await reply.edit("❌ لا يمكن تحديد تاريخ الإنشاء من خلال الخدمة.")
                else:
                    await reply.edit(f"⚠️ فشل الاتصال بالخدمة. الكود: {resp.status}")
    except Exception as e:
        await reply.edit(f"❌ حدث خطأ أثناء جلب التاريخ:\n{e}")
