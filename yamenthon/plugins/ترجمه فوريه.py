import re
import json
import os
from telethon import events
from deep_translator import GoogleTranslator

from . import zedub
from ..core.managers import edit_or_reply

# ملف تخزين بيانات الترجمة
TRANSLATE_FILE = "translate_settings.json"

# تحميل البيانات
if os.path.exists(TRANSLATE_FILE):
    with open(TRANSLATE_FILE, "r", encoding="utf-8") as f:
        translate_data = json.load(f)
else:
    translate_data = {"chats": {}, "enabled": []}


def save_data():
    with open(TRANSLATE_FILE, "w", encoding="utf-8") as f:
        json.dump(translate_data, f, ensure_ascii=False, indent=2)


# أمر ضبط اللغة
@zedub.zed_cmd(pattern="لغه الترجمه(?:\s+(\w+))?")
async def set_lang(event):
    lang = event.pattern_match.group(1)
    chat_id = str(event.chat_id)

    if not lang:
        return await edit_or_reply(
            event,
            "✧ أرسل اللغة التي تريد ضبطها.\nمثال:\n`.لغه الترجمه en` للإنجليزية\n`.لغه الترجمه ar` للعربية"
        )

    # حفظ اللغة
    translate_data["chats"][chat_id] = lang
    save_data()
    await edit_or_reply(event, f"✧ تم ضبط لغة الترجمة إلى **{lang}** في هذه الدردشة ✅")


# أمر تفعيل الترجمة
@zedub.zed_cmd(pattern="تفعيل الترجمه$")
async def enable_translate(event):
    chat_id = str(event.chat_id)
    lang = translate_data["chats"].get(chat_id)

    if not lang:
        return await edit_or_reply(
            event,
            "✧ يجب أولاً ضبط لغة الترجمة باستخدام:\n`.لغه الترجمه <رمز_اللغة>`"
        )

    if chat_id not in translate_data["enabled"]:
        translate_data["enabled"].append(chat_id)
        save_data()

    await edit_or_reply(event, f"✧ تم تفعيل الترجمة الفورية إلى **{lang}** في هذه الدردشة ✅")


# أمر إيقاف الترجمة
@zedub.zed_cmd(pattern="ايقاف الترجمه$")
async def disable_translate(event):
    if translate_data["enabled"]:
        translate_data["enabled"].clear()
        save_data()
        await edit_or_reply(event, "✧ تم إيقاف الترجمة الفورية من جميع الدردشات ❌")
    else:
        await edit_or_reply(event, "✧ الترجمة الفورية متوقفة بالفعل ❌")


# فلتر للرسائل العادية
@zedub.on(events.NewMessage(incoming=True))
async def auto_translate(event):
    chat_id = str(event.chat_id)

    # التأكد أن الترجمة مفعلة في هذه الدردشة
    if chat_id not in translate_data["enabled"]:
        return

    if not event.message.message or event.message.message.startswith("."):
        return

    text = event.message.message

    # استثناء الإيموجي فقط
    if re.fullmatch(r"[\W_]+", text):
        return

    lang = translate_data["chats"].get(chat_id, "en")

    try:
        translated = GoogleTranslator(source="auto", target=lang).translate(text)
        if translated and translated.strip() != text.strip():
            await event.reply(f"🌍 {translated}")
    except Exception as e:
        await event.reply(f"⚠️ خطأ في الترجمة: {e}")
