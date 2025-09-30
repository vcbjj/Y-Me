"""
📌 منع التفليش (Anti-Kick Flood) - سورس يمنثون

- الأوامر:
  .منع التفليش   ← تفعيل حماية منع التفليش
  .سماح التفليش  ← تعطيل حماية منع التفليش

- يدعم:
  ✅ المجموعات العادية
  ✅ السوبرجروب
  ✅ القنوات (broadcast + discussion)

- عند محاولة أي مشرف طرد عدة أعضاء بسرعة (تفليش)،
  يتم تنزيله مباشرة من الإدارة وإرسال تنبيه إلى مجموعة السجلات BOTLOG_CHATID.
"""

from datetime import datetime
from telethon import events
from telethon.tl.types import ChatAdminRights, Channel
from telethon.tl.functions.channels import EditAdminRequest, GetAdminLogRequest

from yamenthon import zedub
from . import gvarstatus, addgvar, delgvar, BOTLOG_CHATID

# ===================== المتغيرات =====================
remove_admins_aljoker = {}  # تخزين آخر وقت طرد لكل مشرف


# ===================== مراقبة الطرد =====================
@zedub.on(events.ChatAction)
async def monitor_kicks(event):
    if not gvarstatus("Mn3_Kick"):
        return

    chat = await event.get_chat()
    if not chat:
        return

    # التحقق من النوع: مجموعة / قناة
    is_channel = isinstance(chat, Channel)

    try:
        if event.user_kicked:  # فقط لو في عملية طرد
            user_id = getattr(event.action_message.from_id, "user_id", None)
            if not user_id:
                return

            now = datetime.now()

            # تحقق من معدل الطرد
            if user_id in remove_admins_aljoker:
                if (now - remove_admins_aljoker[user_id]).seconds < 60:
                    try:
                        admin_info = await event.client.get_entity(user_id)
                        yamen_link = (
                            f"[{admin_info.first_name}](tg://user?id={admin_info.id})"
                        )

                        # صلاحيات فارغة لعزل المشرف
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

                        # تنفيذ عزل المشرف
                        await event.client(
                            EditAdminRequest(
                                channel=chat,
                                user_id=user_id,
                                admin_rights=rights,
                                rank=""
                            )
                        )

                        # رسالة تنبيه
                        msg = (
                            "🚨 **تم عزل مشرف بسبب التفليش** 🚨\n\n"
                            f"👤 المشرف: {yamen_link}\n"
                            f"🆔 ايدي: `{admin_info.id}`\n"
                            f"📌 المجموعة/القناة: {getattr(chat, 'title', 'غير معروف')}\n"
                            f"⏰ الوقت: {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                            f"✅ النتيجة: تم سحب صلاحياته بنجاح"
                        )

                        # إرسال الإشعار
                        if BOTLOG_CHATID and int(BOTLOG_CHATID) != 0:
                            await event.client.send_message(BOTLOG_CHATID, msg)
                        else:
                            await event.reply(msg)

                    except Exception as e:
                        await event.reply(
                            f"⚠️ حدث خطأ أثناء محاولة تنزيل المشرف:\n`{str(e)}`"
                        )

                # تحديث الوقت
                remove_admins_aljoker[user_id] = now
            else:
                remove_admins_aljoker[user_id] = now

    except Exception:
        return


# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def enable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    if gvarstatus("Mn3_Kick"):
        return await event.edit("ℹ️︙ حماية منع التفليش مفعلة مسبقًا في هذه المجموعة/القناة")

    addgvar("Mn3_Kick", True)
    await event.edit("✅︙ تم تفعيل حماية منع التفليش في هذه المجموعة/القناة")


@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def disable_antiflash(event):
    chat = await event.get_chat()
    if not chat:
        return await event.edit("⚠️︙ لا يمكن استخدام هذا الأمر هنا")

    if not gvarstatus("Mn3_Kick"):
        return await event.edit("ℹ️︙ حماية منع التفليش معطلة مسبقًا في هذه المجموعة/القناة")

    delgvar("Mn3_Kick")
    await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة/القناة")
