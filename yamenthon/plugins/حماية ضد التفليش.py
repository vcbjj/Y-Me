from datetime import datetime
from telethon import events
from telethon.tl.types import ChatAdminRights, Channel, ChannelAdminLogEvent
from telethon.tl.functions.channels import EditAdminRequest, GetAdminLogRequest

from yamenthon import zedub
from . import gvarstatus, addgvar, delgvar, BOTLOG_CHATID

# ===================== المتغيرات =====================
remove_admins_aljoker = {}  # تخزين آخر وقت طرد لكل مشرف

# ===================== دالة عزل المشرف =====================
async def demote_admin(client, chat, user_id, admin_info):
    rights = ChatAdminRights(
        change_info=False,
        post_messages=False,
        edit_messages=False,
        delete_messages=False,
        ban_users=False,
        invite_users=False,
        pin_messages=False,
        add_admins=False,
        manage_call=False,
        anonymous=False,
    )
    await client(
        EditAdminRequest(channel=chat, user_id=user_id, admin_rights=rights, rank="")
    )

    yamen_link = f"[{admin_info.first_name}](tg://user?id={admin_info.id})"
    now = datetime.now()
    msg = (
        "🚨 **تم عزل مشرف بسبب التفليش** 🚨\n\n"
        f"👤 المشرف: {yamen_link}\n"
        f"🆔 ايدي: `{admin_info.id}`\n"
        f"📌 المجموعة/القناة: {getattr(chat, 'title', 'غير معروف')}\n"
        f"⏰ الوقت: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"✅ النتيجة: تم سحب صلاحياته بنجاح"
    )

    if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
        await client.send_message(BOTLOG_CHATID, msg)
    else:
        await client.send_message(chat.id, msg)

# ===================== مراقبة الطرد =====================
@zedub.on(events.ChatAction)
async def monitor_kicks(event):
    chat = await event.get_chat()
    if not chat or not gvarstatus(f"Mn3_Kick_{chat.id}"):
        return

    is_channel = isinstance(chat, Channel)
    now = datetime.now()

    # --- مجموعات / سوبرجروب ---
    if getattr(event, "user_kicked", False):
        user_id = getattr(getattr(event.action_message, "from_id", None), "user_id", None)
        if not user_id:
            return

        if user_id in remove_admins_aljoker and (now - remove_admins_aljoker[user_id]).seconds < 60:
            try:
                admin_info = await event.client.get_entity(user_id)
                await demote_admin(event.client, chat, user_id, admin_info)
            except Exception as e:
                await event.reply(f"⚠️ خطأ عند محاولة عزل المشرف:\n`{str(e)}`")

        remove_admins_aljoker[user_id] = now
        return

    # --- القنوات ---
    if is_channel:
        try:
            result = await event.client(
                GetAdminLogRequest(channel=chat, q="", max_id=0, min_id=0, limit=10)
            )
            for entry in getattr(result, "events", []):
                if isinstance(entry, ChannelAdminLogEvent) and entry.action:
                    action_name = entry.action.__class__.__name__
                    if "ParticipantBan" in action_name:
                        actor = entry.user_id
                        if actor in remove_admins_aljoker and (now - remove_admins_aljoker[actor]).seconds < 60:
                            try:
                                admin_info = await event.client.get_entity(actor)
                                await demote_admin(event.client, chat, actor, admin_info)
                            except Exception as e:
                                await event.client.send_message(chat.id, f"⚠️ خطأ عند العزل:\n`{str(e)}`")
                        remove_admins_aljoker[actor] = now
        except Exception:
            pass

# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")
    if gvarstatus(f"Mn3_Kick_{chat.id}"):
        return await event.edit("ℹ️︙ حماية منع التفليش مفعلة مسبقًا هنا")
    addgvar(f"Mn3_Kick_{chat.id}", True)
    await event.edit("✅︙ تم تفعيل حماية منع التفليش في هذه المجموعة/القناة")

@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def disable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")
    if not gvarstatus(f"Mn3_Kick_{chat.id}"):
        return await event.edit("ℹ️︙ حماية منع التفليش معطلة مسبقًا هنا")
    delgvar(f"Mn3_Kick_{chat.id}")
    await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة/القناة")
