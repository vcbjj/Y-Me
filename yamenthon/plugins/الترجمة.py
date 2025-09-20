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

# عدلت بعض الأكواد الخاطئة هنا ووضعت بعض الأسماء الشائعة
langs = {
    'عربي': 'ar',
    'انجليزي': 'en',
    'انكليزي': 'en',
    'انجليزية': 'en',
    'فارسي': 'fa',
    'فارسية': 'fa',
    'بلغاري': 'bg',
    'صيني مبسط': 'zh-CN',
    'صيني تقليدي': 'zh-TW',
    'صيني': 'zh-CN',
    'كرواتي': 'hr',
    'دنماركي': 'da',
    'الماني': 'de',
    'ألماني': 'de',
    'فنلندي': 'fi',    # صححتها
    'فلبيني': 'fil',
    'فرنسي': 'fr',
    'يوناني': 'el',
    'هنغاري': 'hu',
    'كوري': 'ko',
    'ايطالي': 'it',
    'ايطاليه': 'it',
    'ياباني': 'ja',
    'نرويجي': 'no',
    'بولندي': 'pl',
    'برتغالي': 'pt',
    'روسي': 'ru',
    'سلوفيني': 'sl',
    'اسباني': 'es',
    'اسبانية': 'es',
    'سويدي': 'sv',
    'تركي': 'tr',
    'هندي': 'hi',      # صححتها (hi للـ Hindi)
    'كردي': 'ku',
    # ممكن تضيف المزيد من الأسماء/المرادفات هنا
}

async def gtrans(text, lan_code):
    try:
        # قبول رموز طويلة او قصيرة (GoogleTranslator يتعامل مع معظم الرموز)
        translated = GoogleTranslator(source="auto", target=lan_code).translate(text)
        return translated
    except Exception as er:
        # ارجع الاستثناء كنص حتى نقدر نشوف السبب عند الاختبار
        return f"حدث خطأ أثناء الترجمة: {er}"

@zedub.zed_cmd(
    pattern="ترجمة ([\s\S]*)",
    command=("ترجمة", "tools"),
    info={
        "header": "To translate the text to required language.",
        "note": "اكتب اسم اللغة بالعربي أو رمزها (مثال: ترجمة انجليزي أو ترجمة en).",
        "usage": [
            "{tr}ترجمة <اللغة> ; <النص>",
            "{tr}ترجمة <اللغة> (بالرد على نص)",
        ],
        "examples": "{tr}ترجمة انجليزي ; اهلا بك",
    },
)
async def _(event):
    input_str = event.pattern_match.group(1).strip()

    # إذا الأمر كان بالرد
    if event.reply_to_msg_id:
        previous_message = await event.get_reply_message()
        # حاول الحصول على النص من أكثر من حقل (حالة الميديا)
        text = previous_message.message or previous_message.text or ""
        lan = input_str or "انجليزي"
    elif ";" in input_str:
        lan, text = input_str.split(";", 1)
    else:
        return await edit_delete(
            event, "**˖✧˚ قم بالرد على الرسالة للترجمة أو استخدم ; للفصل**", time=5
        )

    text = deEmojify(text.strip())
    lan = lan.strip()

    # إذا المستخدم أدخل رمز لغة مختصر مثل 'en' أو 'ru'، اسمقته مباشرة
    lan_lower = lan.lower()
    if lan_lower in langs:
        lan_code = langs[lan_lower]
    elif lan in langs:
        lan_code = langs[lan]
    else:
        # قبول رموز اللغة المباشرة (مثل "en", "ru", "ar", "zh-CN")
        # نتأكد أن المدخل عبارة عن رمز مكون من 1-5 أحرف / شرطات
        import re
        if re.fullmatch(r"[A-Za-z\-]{1,10}", lan):
            lan_code = lan
        else:
            return await edit_delete(event, f"**˖✧˚ اللغة '{lan}' غير مدعومة!**", time=5)

    if not text or len(text) < 1:
        return await edit_delete(event, "**˖✧˚قم بكتابة ما تريد ترجمته!**", time=5)

    try:
        trans = await gtrans(text, lan_code)
        # لو كانت النتيجة نص خطأ ناتج عن Exception قم بعرضه للمساعدة في التصحيح
        if isinstance(trans, str) and trans.startswith("حدث خطأ"):
            return await edit_delete(event, f"**˖✧˚ {trans}**", time=6)

        output_str = f"**˖✧˚ تمت الترجمة الى {lan}**\n`{trans}`"
        await edit_or_reply(event, output_str)
    except Exception as exc:
        await edit_delete(event, f"**خطا:**⚠️⚠️ {exc}", time=5)
