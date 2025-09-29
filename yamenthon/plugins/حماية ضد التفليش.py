"""
📌 منع التفليش (Anti-Kick Flood) - سورس يمنثون

- الأوامر:
  .منع التفليش   ← تفعيل حماية منع التفليش
  .سماح التفليش  ← تعطيل حماية منع التفليش

- عند محاولة أي مشرف طرد عدة أعضاء بسرعة (تفليش)،
  يتم تنزيله مباشرة من الإدارة وإرسال تنبيه في المجموعة.

"""

from datetime import datetime
from telethon import events
from yamenthon import zedub
from . import gvarstatus, addgvar, delgvar

# ===================== المتغيرات =====================
# تخزين آخر وقت طرد لكل مشرف
remove_admins_aljoker = {}

# ===================== مراقبة الطرد =====================
@zedub.on(events.ChatAction)
async def Hussein(event):
    if not gvarstatus("Mn3_Kick"):
        return

    try:
        if event.user_kicked:
            # معرف المشرف اللي نفذ الطرد
            user_id = getattr(event.action_message.from_id, "user_id", None)
            if not user_id:
                return

            chat = await event.get_chat()
            if not chat:
                return

            now = datetime.now()

            # إذا المشرف سبق وطرد خلال آخر دقيقة
            if user_id in remove_admins_aljoker:
                if (now - remove_admins_aljoker[user_id]).seconds < 60:
                    try:
                        admin_info = await event.client.get_entity(user_id)
                        yamen_link = f"[{admin_info.first_name}](tg://user?id={admin_info.id})"
                        await event.reply(
                            f"**᯽︙ تم تنزيل المشرف {yamen_link} بسبب قيامه بمحاولة تفليش 🤣**"
                        )

                        # تنزيله من الإدارة
                        await event.client.edit_admin(
                            chat,
                            user_id,
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
                            other=False,
                        )
                    except Exception as e:
                        await event.reply(f"⚠️ حدث خطأ أثناء محاولة تنزيل المشرف: {str(e)}")

                # تحديث الوقت الأخير
                remove_admins_aljoker[user_id] = now
            else:
                # تسجيل أول محاولة
                remove_admins_aljoker[user_id] = now
    except Exception:
        return

# ===================== الأوامر =====================
@zedub.zed_cmd(pattern="منع التفليش", require_admin=True)
async def Hussein_aljoker_on(event):
    addgvar("Mn3_Kick", True)
    await event.edit("✅︙ تم تفعيل حماية منع التفليش في هذه المجموعة")

@zedub.zed_cmd(pattern="سماح التفليش", require_admin=True)
async def Hussein_aljoker_off(event):
    delgvar("Mn3_Kick")
    await event.edit("🛑︙ تم تعطيل حماية منع التفليش في هذه المجموعة")
