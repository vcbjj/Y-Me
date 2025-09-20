from asyncio import sleep
from deep_translator import GoogleTranslator
import requests
import json
import os
from ..helpers.functions import translate
from . import zedub
from telethon import events, types
from ..sql_helper.globals import addgvar, delgvar, gvarstatus
from ..core.managers import edit_delete, edit_or_reply
from . import deEmojify, reply_id

langs = {
    'عربي': 'ar',
    'فارسي': 'fa',
    'بلغاري': 'bg',
    'صيني مبسط': 'zh-CN',
    'صيني تقليدي': 'zh-TW',
    'كرواتي': 'hr',
    'دنماركي': 'da',
    'الماني': 'de',
    'انجليزي': 'en',
    'فنلندي': 'fi',      
    'فرنسي': 'fr',
    'يوناني': 'el',
    'هنغاري': 'hu',
    'كوري': 'ko',
    'ايطالي': 'it',
    'ياباني': 'ja',
    'نرويجي': 'no',
    'بولندي': 'pl',
    'برتغالي': 'pt',
    'روسي': 'ru',
    'سلوفيني': 'sl',
    'اسباني': 'es',
    'سويدي': 'sv',
    'تركي': 'tr',
    'هندي': 'hi',        
    'كردي': 'ku',
}


async def gtrans(text, lan_code):
    try:
        response = GoogleTranslator(source="auto", target=lan_code).translate(text)
        return response
    except Exception as er:
        return f"حدث خطأ \n{er}"

@zedub.zed_cmd(pattern="event")
async def Reda(event):
    if event.reply_to_msg_id:
        m = await event.get_reply_message()
        with open("reply.txt", "w") as file:
                file.write(str(m))
        await event.client.send_file(event.chat_id, "reply.txt")
        os.remove("reply.txt")

@zedub.zed_cmd(
    pattern="ترجمة ([\s\S]*)",
    command=("ترجمة", "tools"),
    info={
        "header": "To translate the text to required language.",
        "note": "For language codes check [this link](https://bit.ly/2SRQ6WU)",
        "usage": [
            "{tr}ترجمة <اللغة> ; <النص>",
            "{tr}ترجمة <اللغة> (بالرد على نص)",
        ],
        "examples": "{tr}ترجمة انجليزي ; اهلا بك",
    },
)
async def _(event):
    "To translate the text."
    input_str = event.pattern_match.group(1)

    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        text = previous_message.message
        lan = input_str or "انجليزي"
    elif ";" in input_str:
        lan, text = input_str.split(";")
    else:
        return await edit_delete(
            event, "**˖✧˚ قم بالرد على الرسالة للترجمة **", time=5
        )

    text = deEmojify(text.strip())
    lan = lan.strip()

    # ✅ تحقق من القاموس
    if lan not in langs:
        return await edit_delete(event, f"**˖✧˚ اللغة {lan} غير مدعومة!**", time=5)

    lan_code = langs[lan]

    if len(text) < 2:
        return await edit_delete(event, "**˖✧˚قم بكتابة ما تريد ترجمته!**")

    try:
        trans = await gtrans(text, lan_code)
        if not trans:
            return await edit_delete(event, "**˖✧˚ تحقق من رمز اللغة !, لا يوجد هكذا لغة**")      

        output_str = f"**˖✧˚ تمت الترجمة الى {lan}**\n`{trans}`"
        await edit_or_reply(event, output_str)
    except Exception as exc:
        await edit_delete(event, f"**خطا:**⚠️⚠️ {exc}", time=5)

