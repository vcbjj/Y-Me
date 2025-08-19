import asyncio
from ..Config import Config
from ..core.managers import edit_or_reply as eor
from .. import zedub
from telethon.errors import FloodWaitError

hl = "."
plugin_category = "الإسبام"

async def validate_input(event, pattern_length, min_parts=2, example=""):
    """تحقق من صحة المدخلات الأساسية"""
    msg_ = event.text[pattern_length:].strip()
    if not msg_ or len(msg_.split()) < min_parts:
        await eor(event, f"❗ **يجب كتابة {min_parts} أجزاء على الأقل.**\nمثال: `{example}`")
        return None
    return msg_

async def get_spam_params(event, msg_, counter_index=0, text_index=1):
    """استخراج عدد الرسائل والنص من المدخلات"""
    try:
        parts = msg_.split()
        counter = int(parts[counter_index])
        spam_message = " ".join(parts[text_index:])
        return counter, spam_message
    except (ValueError, IndexError):
        await eor(event, "❗ **خطأ في المدخلات. تأكد من كتابة الأرقام والنص بشكل صحيح.**")
        return None, None

@zedub.zed_cmd(pattern="سبام(?:\s|$)([\s\S]*)")
async def spammer(event):
    """إرسال رسالة عدد معين من المرات (حتى 100)"""
    lg_id = Config.LOGGER_ID
    msg_ = await validate_input(event, 6, example=f"{hl}سبام 5 مرحبًا")
    if not msg_:
        return

    counter, spam_message = await get_spam_params(event, msg_)
    if counter is None:
        return

    if counter > 100:
        await eor(event, f"❗ الحد الأقصى هو 100 رسالة.\nاستخدم: `{hl}سبام_كبير` للأعداد الكبيرة")
        return

    reply_message = await event.get_reply_message()
    msg = await eor(event, f"🔁 جارِ الإرسال ({counter} رسالة)...")
    
    try:
        for _ in range(counter):
            await event.client.send_message(
                event.chat_id,
                spam_message,
                reply_to=reply_message
            )
        await msg.delete()
        await event.client.send_message(lg_id, f"#SPAM\nتم إرسال {counter} رسالة.")
    except Exception as e:
        await eor(event, f"❌ خطأ: {str(e)}")

@zedub.zed_cmd(pattern="سبام_كبير(?:\s|$)([\s\S]*)")
async def bigspam(event):
    """سبام بعدد كبير بدون حد (قد يسبب حظر مؤقت)"""
    lg_id = Config.LOGGER_ID
    msg_ = await validate_input(event, 11, example=f"{hl}سبام_كبير 500 هجوم")
    if not msg_:
        return

    counter, spam_message = await get_spam_params(event, msg_)
    if counter is None:
        return

    reply_msg = await event.get_reply_message()
    message_to_send = reply_msg if reply_msg else spam_message
    
    try:
        for _ in range(counter):
            await event.client.send_message(
                event.chat_id,
                message_to_send,
                reply_to=reply_msg
            )
        await event.delete()
        await event.client.send_message(lg_id, f"#BIGSPAM\nتم إرسال {counter} رسالة.")
    except Exception as e:
        await eor(event, f"❌ خطأ: {str(e)}")

@zedub.zed_cmd(pattern="سبام_مؤقت(?:\s|$)([\s\S]*)")
async def delay_spam(event):
    """سبام بفاصل زمني بين كل رسالة"""
    lg_id = Config.LOGGER_ID
    msg_ = await validate_input(event, 12, min_parts=3, example=f"{hl}سبام_مؤقت 1 10 اهلا")
    if not msg_:
        return

    try:
        parts = msg_.split(" ", 2)
        delay = float(parts[0])
        counter = int(parts[1])
        spam_message = parts[2]
    except Exception:
        await eor(event, f"❗ **تنسيق غير صحيح.**\nمثال: `{hl}سبام_مؤقت 1 10 اهلا`")
        return

    await event.delete()
    
    try:
        for _ in range(counter):
            await event.client.send_message(event.chat_id, spam_message)
            await asyncio.sleep(delay)
        await event.client.send_message(lg_id, f"#DELAYSPAM\nتم إرسال {counter} رسالة بفاصل {delay} ثانية.")
    except Exception as e:
        await event.client.send_message(lg_id, f"❌ فشل الإسبام المؤقت: {str(e)}")

@zedub.zed_cmd(pattern="سبام_لا_نهائي(?:\s|$)([\s\S]*)")
async def uspam(event):
    """إرسال رسالة بشكل لا نهائي حتى حدوث FloodWait"""
    lg_id = Config.LOGGER_ID
    reply_msg = await event.get_reply_message()
    msg_text = event.text[13:].strip()
    input_msg = reply_msg.message if reply_msg else msg_text

    if not input_msg:
        await eor(event, f"❗ **يجب كتابة نص أو الرد على رسالة.**\nمثال: `{hl}سبام_لا_نهائي اهلا`")
        return

    await event.client.send_message(
        lg_id,
        "#UNLIMITED_SPAM\nبدأ الإسبام غير النهائي. سيتم التوقف عند حدوث FloodWait."
    )

    try:
        while True:
            await event.client.send_message(event.chat_id, input_msg)
    except FloodWaitError as e:
        await event.client.send_message(lg_id, f"⏳ توقف بسبب FloodWait: {e.seconds} ثانية")
    except Exception as e:
        await event.client.send_message(lg_id, f"❌ خطأ: {str(e)}")

@zedub.zed_cmd(pattern="سبام_مجزأ(?:\s|$)([\s\S]*)")
async def bspam(event):
    """إرسال سبام مجزأ لتفادي الحظر (دفعات مع تأخير)"""
    lg_id = Config.LOGGER_ID
    msg_ = await validate_input(event, 12, example=f"{hl}سبام_مجزأ 500 اهلا")
    if not msg_:
        return

    counter, spam_message = await get_spam_params(event, msg_)
    if counter is None:
        return

    reply_msg = await event.get_reply_message()
    spam_message = reply_msg.message if reply_msg else spam_message

    rest = counter % 100
    sets = counter // 100
    delay = 30

    try:
        for _ in range(sets):
            for __ in range(100):
                await event.client.send_message(event.chat_id, spam_message)
            delay += 2
            await asyncio.sleep(delay)

        for _ in range(rest):
            await event.client.send_message(event.chat_id, spam_message)

        await event.delete()
        await event.client.send_message(lg_id, f"#BREAK_SPAM\nتم إرسال {counter} رسالة مجزأة.")
    except Exception as e:
        await eor(event, f"❌ خطأ: {str(e)}")

@zedub.zed_cmd(pattern="سبام_ميديا(?:\s|$)([\s\S]*)")
async def mspam(event):
    """إرسال وسائط (صور/ملصقات/فيديوهات) مكررة"""
    lg_id = Config.LOGGER_ID
    reply_msg = await event.get_reply_message()
    arg = (event.pattern_match.group(1) or "").strip()

    if not arg or not arg.isdigit():
        await eor(event, f"❗ **يجب تحديد عدد التكرارات.**\nمثال: `{hl}سبام_ميديا 10` مع الرد على ميديا")
        return

    count = int(arg)

    if not reply_msg or not reply_msg.media:
        await eor(event, "❗ **يجب الرد على صورة، ملصق، فيديو أو GIF**")
        return
    
    try:
        media = reply_msg.media
        for _ in range(count):
            await event.client.send_file(event.chat_id, media)
        await event.delete()
        await event.client.send_message(lg_id, f"#MEDIA_SPAM\nتم إرسال الوسائط {count} مرة.")
    except Exception as e:
        await eor(event, f"❌ خطأ في إرسال الميديا: {str(e)}")
