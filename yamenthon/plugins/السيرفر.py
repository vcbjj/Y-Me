import asyncio
import glob
import os

from . import zedub
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.utils import _zedutils
from ..sql_helper.globals import delgvar
from . import BOTLOG, BOTLOG_CHATID, mention

plugin_category = "الادوات"

# قاموس التحويل من الاسماء المبسطة إلى التوكنات الفعلية
var_yamenthon = {
    "البوت": "TG_BOT_TOKEN",
}

config = "./config.py"
var_checker = [
    "APP_ID",
    "PM_LOGGER_GROUP_ID",
    "PRIVATE_CHANNEL_BOT_API_ID",
    "PRIVATE_GROUP_BOT_API_ID",
]
exts = ["jpg", "png", "webp", "webm", "m4a", "mp4", "mp3", "tgs"]

cmds = [
    "rm -rf downloads",
    "mkdir downloads",
]

# ========================================================================

@zedub.zed_cmd(
    pattern="(ضع|جلب) توكن ([\\s\\S]*)",
    command=("توكن", plugin_category),
    info={
        "header": "To manage config vars.",
        "flags": {
            "set": "To set new var in vps or modify the old var",
            "get": "To show the already existing var value.",
            "del": "To delete the existing value",
        },
        "usage": [
            "{tr}ضع توكن <اسم توكن> <قيمة توكن>",
            "{tr}جلب توكن <اسم توكن>",
            
        ],
        "examples": [
            "{tr}جلب توكن ALIVE_NAME",
        ],
    },
)
async def variable(event):
    """
    Manage most of ConfigVars setting, set new var, get current var, or delete var...
    """
    if not os.path.exists(config):
        return await edit_delete(
            event,
            "**- عـذراً .. لايـوجـد هنـالك ملـف كـونفـج 📁🖇**\n\n"
            "**- هـذه الاوامـر خـاصـة فقـط بالمنصبيـن ع السيـرفـر 📟💡**"
        )

    cmd = event.pattern_match.group(1)
    string = ""
    match = None

    with open(config, "r") as f:
        configs = f.readlines()

    # ===== جلب توكن =====
    if cmd == "جلب":
        cat = await edit_or_reply(event, "**⌔∮ جاري الحصول على توكن البوت.... **")
        await asyncio.sleep(1)
        variable = event.pattern_match.group(2).split()[0]
        for i in configs:
            if variable in i:
                _, val = i.split("= ")
                return await cat.edit(
                    "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - 𝗖𝗼𝗻𝗳𝗶𝗴 𝗩𝗮𝗿𝘀 𓆪\n"
                    "𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻"
                    f"\n\n**⌔∮الفـار** `{variable} = {val}`"
                )
        await cat.edit(
            "𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 - 𝗖𝗼𝗻𝗳𝗶𝗴 𝗩𝗮𝗿𝘀 𓆪\n"
            "𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻"
            f"\n\n**⌔∮الفـار :** -> {variable} **غيـر موجود**❌"
        )

    # ===== ضع توكن =====
    elif cmd == "ضع":
        user_input = "".join(event.text.split(maxsplit=2)[2:])
        cat = await edit_or_reply(event, "**⌔∮جـارِ إعـداد البوت المساعد الجديد\n.......♻️**")
        if not user_input:
            return await cat.edit("**⌔∮** `.ضع توكن ` **+ توكن بوتك**")
        try:
            delgvar("y_assistant")
        except Exception as e:
            print(f"خطأ أثناء حذف z_assistant: {e}")    

        # أول جزء هو اسم توكن (بالعربي أو الانجليزي)
        variable = "".join(user_input.split(maxsplit=1)[0])
        # ثاني جزء هو القيمة
        value = "".join(user_input.split(maxsplit=1)[1:])

        # تحويل الاسم إذا كان مبسط
        variable = var_yamenthon.get(variable, variable)

        if variable not in var_checker:
            value = f"'{value}'"
            if not value:
                return await cat.edit("**⌔∮** `.ضع توكن ` **+ توكن بوتك**")

        await asyncio.sleep(1)
        match = False
        for i in configs:
            if variable in i:
                string += f"    {variable} = {value}\n"
                match = True
            else:
                string += f"{i}"

        if match:
            await cat.edit(
                f"**- تم تغيـر** `{variable}` **:**\n"
                f" **- المتغيـر :** `{value}` \n"
                "**- يتم الان اعـادة تشغيـل بـوت يمن ثون "
                "يستغـرق الامر 5-8 دقيقـه ▬▭ ...**"
            )
        else:
            string += f"    {variable} = {value}\n"
            await cat.edit(
                f"**- تم إضـافـة** `{variable}` **:**\n"
                f" **- المضـاف اليـه :** `{value}` \n"
                "**- يتم الان اعـادة تشغيـل بـوت يمن ثون "
                "يستغـرق الامر 5-8 دقيقـه ▬▭ ...**"
            )

        with open(config, "w") as f1:
            f1.write(string)

        if os.path.exists("SESION_REFZ_BOT.session"):
            os.remove("SESION_REFZ_BOT.session")

        await event.client.reload(cat)


# ========================================================================

@zedub.zed_cmd(
    pattern="(ري|كلين) لود$",
    command=("لود", plugin_category),
    info={
        "header": "To reload your bot in vps/ similar to restart",
        "الاوامر المضافه لـ لـود": {
            "ري": "restart your bot without deleting junk files",
            "كلين": "delete all junk files & restart",
        },
        "الاسـتخـدام": [
            "{tr}ري لود",
            "{tr}كلين لود",
        ],
    },
)
async def _(event):
    "لـ اعـادة اشغيـل البـوت في السيـرفـر"
    cmd = event.pattern_match.group(1)
    zed = await edit_or_reply(
        event,
        f"**⌔∮ اهـلا عـزيـزي** - {mention}\n\n"
        f"**⌔∮ يتـم الان اعـادة تشغيـل بـوت يمنثون "
        f"فـي السيـرفـر قـد يستغـرق الامـر 2-3 دقيقـه ▬▭ ...**",
    )
    if cmd == "كلين":
        for file in exts:
            removing = glob.glob(f"./*.{file}")
            for i in removing:
                os.remove(i)
        for i in cmds:
            await _zedutils.runcmd(i)

    await event.client.reload(zed)
 
