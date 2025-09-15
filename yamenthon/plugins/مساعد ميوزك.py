import asyncio
import os
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    ApiIdInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
    AuthKeyUnregisteredError,
)

from . import zedub
from ..core.managers import edit_delete, edit_or_reply

# استيراد متغيرات الكونفج
import config  

plugin_category = "الادوات"

# القاموس للتحويل
var_yamenthon = {
    "ميوزك": "VC_SESSION",
}

config_file = "./config.py"


async def check_telethon_session(session_string):
    """
    يتحقق من صحة جلسة Telethon باستخدام APP_ID و API_HASH من config.py
    """
    try:
        client = TelegramClient(
            StringSession(session_string),
            int(Config.APP_ID),
            Config.API_HASH
        )
        await client.connect()
        if not await client.is_user_authorized():
            await client.disconnect()
            return False
        await client.disconnect()
        return True
    except (ApiIdInvalidError, PhoneNumberInvalidError, SessionPasswordNeededError, AuthKeyUnregisteredError):
        return False
    except Exception as e:
        print(f"خطأ التحقق من الجلسة: {e}")
        return False

# ========================================================================

@zedub.zed_cmd(
    pattern="(جلب|حذف) مساعد ([\\s\\S]*)",
    command=("مساعد", plugin_category),
    info={
        "header": "To manage config vars.",
        "flags": {
            "set": "To set new var in vps or modify the old var",
            "get": "To show the already existing var value.",
            "del": "To delete the existing value",
        },
        "usage": [
            "{tr}ضع مساعد <اسم مساعد> <قيمة مساعد>",
            "{tr}جلب مساعد <اسم مساعد>",
            "{tr}حذف مساعد <اسم مساعد>",
        ],
        "examples": [
            "{tr}جلب مساعد VC_SESSION",
        ],
    },
)
async def variable(event):
    if not os.path.exists(config_file):
        return await edit_delete(
            event,
            "**- عـذراً .. لايـوجـد هنـالك ملـف كـونفـج 📁🖇**\n\n"
            "**- هـذه الاوامـر خـاصـة فقـط بالمنصبيـن ع السيـرفـر 📟💡**"
        )

    cmd = event.pattern_match.group(1)

    with open(config_file, "r") as f:
        configs = f.readlines()

    # ===== جلب مساعد =====
    if cmd == "جلب":
        cat = await edit_or_reply(event, "**⌔∮ جاري الحصول على المعلومات. **")
        await asyncio.sleep(1)
        variable = event.pattern_match.group(2).split()[0]
        variable = var_yamenthon.get(variable, variable)

        for i in configs:
            if i.strip().startswith(variable):
                _, val = i.split("=", 1)
                val = val.strip()
                return await cat.edit(
                    "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - 𝗖𝗼𝗻𝗳𝗶𝗴 𝗩𝗮𝗿𝘀 𓆪\n"
                    "𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻"
                    f"\n\n**⌔∮الفـار** `{variable} = {val}`"
                )
        return await cat.edit(
            "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - 𝗖𝗼𝗻𝗳𝗶𝗴 𝗩𝗮𝗿𝘀 𓆪\n"
            "𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻"
            f"\n\n**⌔∮الفـار :** -> {variable} **غيـر موجود**❌"
        )

    # ===== حذف مساعد =====
    elif cmd == "حذف":
        cat = await edit_or_reply(
            event,
            "**⌔∮جـارِ الحصول على معلومات لحذف المتغير الفـار من السيـرفـر ...**"
        )
        await asyncio.sleep(1)
        variable = event.pattern_match.group(2).split()[0]
        variable = var_yamenthon.get(variable, variable)

        match = False
        string = ""
        for i in configs:
            if i.strip().startswith(variable):
                match = True
            else:
                string += i

        with open(config_file, "w") as f1:
            f1.write(string)

        if match:
            await cat.edit(
                f"**- الفـار** `{variable}`  **تم حذفه بنجاح.**\n\n"
                "**- يتم الان اعـادة تشغيـل بـوت يمن ثون "
                "يستغـرق الامر 2-1 دقيقـه ▬▭ ...**"
            )
        else:
            await cat.edit(
                "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - 𝗖𝗼𝗻𝗳𝗶𝗴 𝗩𝗮𝗿𝘀 𓆪\n"
                "𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻"
                f"\n\n**⌔∮الفـار :** -> {variable} **غيـر موجود**❌"
            )

        await event.client.reload(cat)

# ========================================================================

@zedub.zed_cmd(
    pattern="ضع مساعد ([\\s\\S]*)",
    command=("مساعد", plugin_category),
    info={
        "header": "لإضافة جلسات المساعدين (مثل VC_SESSION).",
        "usage": [
            "{tr}ضع مساعد ميوزك (بالرد على كود جلسة تيليثون فقط)"
        ],
    },
)
async def set_helper_var(event):
    reply = await event.get_reply_message()
    if not reply or not reply.text:
        return await edit_delete(event, "**⌔∮ بالرد على جلسة تيليثون فقط . . .**")

    session_string = reply.text.strip()
    variable = event.pattern_match.group(1).strip()
    variable = var_yamenthon.get(variable, variable)

    cat = await edit_or_reply(event, "**⌔∮ جاري التحقق من الجلسة...**")

    valid = await check_telethon_session(session_string)
    if not valid:
        return await cat.edit("**✘ الجلسة غير صالحة أو تالفة.**")

    with open(config_file, "r") as f:
        configs = f.readlines()

    string = ""
    match = False
    for i in configs:
        if i.strip().startswith(variable):
            string += f"{variable} = '{session_string}'\n"
            match = True
        else:
            string += i

    if not match:
        string += f"{variable} = '{session_string}'\n"

    with open(config_file, "w") as f:
        f.write(string)

    await cat.edit(
        f"**✔ تم حفظ جلسة `{variable}` بنجاح.**\n\n"
        "**- يتم الان اعـادة تشغيـل بـوت يمن ثون "
        "يستغـرق الامر 5-8 دقيقـه ▬▭ ...**"
    )

    await event.client.reload(cat)
