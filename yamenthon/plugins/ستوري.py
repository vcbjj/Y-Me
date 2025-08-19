import os
from telethon.tl.functions.stories import CanSendStoryRequest, SendStoryRequest
from telethon.tl.types import InputPrivacyValueAllowAll, InputPhoto
from telethon.tl.functions.photos import UploadProfilePhotoRequest
from .. import zedub

@zedub.zed_cmd(pattern="رفع ستوري$")
async def upload_story(event):
    replied = await event.get_reply_message()
    if not replied:
        return await event.reply("**⌔∮ لازم ترد على صورة أو فيديو عشان يتم رفعه كستوري**")

    reply_msg = await event.reply("**⌔∮ جاري التحقق ورفع الستوري** ⏳")

    try:
        check = await event.client(CanSendStoryRequest())

        if isinstance(check, bool):
            if not check:
                return await reply_msg.edit("**⌔∮ تجاوزت الحد المسموح — تحتاج Premium أو انتظر للإعادة** 🚫")

        elif hasattr(check, "can_send") and not check.can_send:
            wait_minutes = getattr(check, "minutes", None)
            if wait_minutes:
                return await reply_msg.edit(
                    f"**⌔∮ لا يمكنك رفع ستوري الآن، حاول بعد {wait_minutes} دقيقة** 🚫"
                )
            return await reply_msg.edit(
                "**⌔∮ تجاوزت الحد المسموح — تحتاج Premium أو انتظر للإعادة** 🚫"
            )

    except Exception as e:
        return await reply_msg.edit(f"**❌ خطأ أثناء التحقق من الحد:** {e}")

    media = replied.media
    if not media or not (media.photo or (media.document and media.document.mime_type.startswith(("image/", "video/")))):
        return await reply_msg.edit("**⌔∮ الوسائط المسموح بها فقط صور أو فيديوهات**")

    file_path = await event.client.download_media(media)

    try:
        if media.photo:
            # الصورة - ارفعها كـ Photo
            uploaded = await event.client.upload_file(file_path)
            # ترفع الصورة كـ photo story عبر UploadProfilePhotoRequest (نستفيد من نفس نوع رفع الصور)
            uploaded_photo = await event.client(UploadProfilePhotoRequest(file=uploaded))
            input_photo = InputPhoto(id=uploaded_photo.photo.id, access_hash=uploaded_photo.photo.access_hash, file_reference=uploaded_photo.photo.file_reference)

            await event.client(SendStoryRequest(
                media=input_photo,
                caption=replied.text or None,
                privacy_rules=[InputPrivacyValueAllowAll()]
            ))

        else:
            # فيديو أو ملف آخر
            uploaded = await event.client.upload_file(file_path)
            await event.client(SendStoryRequest(
                media=uploaded,
                caption=replied.text or None,
                privacy_rules=[InputPrivacyValueAllowAll()]
            ))

        await reply_msg.edit("**⌔∮ تم رفع الستوري بنجاح ✅**")

    except Exception as e:
        await reply_msg.edit(f"**⚠️ فشل رفع الستوري:** {e}")

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
