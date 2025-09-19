import re, os
from . import zedub
from telethon.tl.types import MessageService, MessageActionChannelMigrateFrom
from ..core.managers import edit_or_reply
from ..Config import Config

LOGS = logging.getLogger(__name__)

cancel_process = False

from telethon import events

plugin_category = "الحساب"
@zedub.zed_cmd(
    pattern=r"جلب (.+)",
    command=("حفظ_المحتوى", plugin_category),
    info={
        "header": "حفظ الرسالة كاملة (النص + الصور + الفيديو + الملفات).",
        "description": "يحفظ الرسالة أو الألبوم بالكامل من القنوات/المجموعات إلى الرسائل المحفوظة.",
        "usage": "{tr}جلب <رابط الرسالة>",
    },
)
async def save_media(event):
    message_link = event.pattern_match.group(1)

    if not message_link:
        return await edit_or_reply(event, "**⚠️ | يرجى تحديد رابط الرسالة أولاً!.✓**")

    xx = await edit_or_reply(event, "**⧉ | جاري معالجة الرابط وحفظ الرسالة....✓**")

    save_dir = "media"
    os.makedirs(save_dir, exist_ok=True)

    try:
        # استخراج معرف القناة + الرسالة
        if "/c/" in message_link:
            channel_id, message_id = re.search(r"t.me\/c\/(\d+)\/(\d+)", message_link).groups()
            entity = int(f"-100{channel_id}")  # للمجموعات/القنوات الخاصة
        else:
            channel_username, message_id = re.search(r"t.me\/([^\/]+)\/(\d+)", message_link).groups()
            entity = await zedub.get_entity(channel_username)
            channel_id = entity.id

    except Exception as e:
        return await xx.edit(f"**❌ | لم أستطع استخراج البيانات من الرابط!\nالخطأ:𓊈 **⚠️ 𝗘𝗥𝗥𝗢𝗥 ⚠️** 𓊉  **")

    try:
        # جلب الرسالة
        try:
            message = await zedub.get_messages(entity, ids=int(message_id))
        except Exception as e:
            if "CHANNEL_PRIVATE" in str(e) or "CHAT_ADMIN_REQUIRED" in str(e):
                return await xx.edit("🚫 **| لا يمكنك الوصول لهذه الرسالة!**\n**يبدو أنك لست عضوًا في القناة أو المجموعة.**")
            return await xx.edit(f"❌ | حدث خطأ أثناء جلب الرسالة:\n𓊈 **⚠️ 𝗘𝗥𝗥𝗢𝗥 ⚠️** 𓊉  ")

        if not message:
            return await xx.edit("**⚠️ | الرابط غير صالح أو الرسالة غير موجودة.✓!**")

        # ✅ التحقق إذا الرسالة جزء من ألبوم
        if getattr(message, "grouped_id", None):
            album = await zedub.get_messages(
                entity,
                ids=[
                    m.id
                    for m in await zedub.get_messages(
                        entity,
                        max_id=int(message_id) + 1,
                        min_id=int(message_id) - 10,
                    )
                    if m.grouped_id == message.grouped_id
                ],
            )
            album_files = []
            for m in album:
                if m.media:
                    file_path = await zedub.download_media(m, file=save_dir)
                    album_files.append(file_path)

            if album_files:
                await zedub.send_file(
                    "me",
                    file=album_files,
                    caption=message.text or "**📷 ألبوم محفوظ من الرابط**",
                )
                
                for fp in album_files:
                    try:
                        os.remove(fp)
                    except:
                        pass
                await xx.edit(
                    f"[𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 𓆪](https://t.me/YamenThon)\n𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n\n✓** ┊ تم حفظ الألبوم كاملاً في الرسائل المحفوظة!**\n=*┊✓ رابط الرسالة:**\n{message_link}"
                )
            else:
                await xx.edit("⚠️** | الألبوم لا يحتوي على ميديا قابلة للحفظ!.✓**")

        else:
            
            if message.media:
                file_path = await zedub.download_media(message, file=save_dir)
                await zedub.send_file(
                    "me", file=file_path, caption=message.text if message.text else None
                )
                try:
                    os.remove(file_path)
                except:
                    pass
            else:
                await zedub.send_message("me", message.text or "**📌 (رسالة بدون محتوى)**")

            await xx.edit(
                f"[𓆩 𝗦𝗼𝘂𝗿𝗰𝗲 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 𓆪](https://t.me/YamenThon)\n𓍹ⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧⵧ𓍻\n\n**✓ ┊ تم حفظ الرسالة بنجاح في الرسائل المحفوظة!**\n**✓ ┊ رابط الرسالة:**\n{message_link}"
            )

    except Exception as e:
        await xx.edit(f"❌** | حدث خطأ أثناء الحفظ:**\n𓊈 **⚠️ 𝗘𝗥𝗥𝗢𝗥 ⚠️** 𓊉  ")
        
AsheqMusic_cmd = (
"[ᯓ 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - المحتـوى المقيــد 🛡](t.me/YamenThon) ."
"**⋆─┄─┄─┄─┄──┄─┄─┄─┄─⋆**\n"
"⚉ `.جلب`\n"
"**⪼ الامـر + رابـط الرسالة استخــدام الامـر بدون علامـة +**\n\n**وضيفة امـر جلب يمكنــك من جلب اي محتواى حتى لــو كانــت القنــاه او المجــموعه مقيــده الحفــظ و التحــويل** \n\n"
"**⪼ التحــديثات مستمره وكــل فتــره يتــم إضــافه اوامـــر جــديده ✓📥**\n\n"
) 

@zedub.zed_cmd(pattern="المحتوى المقيد")
async def cmd(asheqqqq):
    await edit_or_reply(asheqqqq, AsheqMusic_cmd)
  
@zedub.zed_cmd(pattern="الحفظ")
async def cmd(asheqqqq):
    await edit_or_reply(asheqqqq, AsheqMusic_cmd)   


@zedub.zed_cmd(
    pattern="الغاء سيف$",
    command=("الغاء سيف", "tools"),
    info={
        "header": "إلغاء عملية حفظ الميديا.",
        "description": "يقوم بإلغاء العملية الجارية لحفظ الميديا من القنوات.",
        "usage": "{tr}الغاء سيف",
    },
)
async def _(event):
    global cancel_process
    cancel_process = True
    await edit_or_reply(event, "✔️ تم إلغاء عملية حفظ الميديا.")


# متابعة الأحداث (مثلاً لو القناة ترحّلت)
@zedub.on(events.NewMessage(incoming=True))
async def check_cancel(event):
    global cancel_process
    if isinstance(event.message, MessageService) and event.message.action and isinstance(
        event.message.action, MessageActionChannelMigrateFrom
    ):
        cancel_process = True


# أمر الحفظ
@zedub.zed_cmd(
    pattern="سيف(?: |$)(.*) (\d+)",
    command=("سيف", "tools"),
    info={
        "header": "حفظ الميديا من القنوات ذات تقييد المحتوى.",
        "description": "يحفظ الصور والفيديوهات والملفات من القنوات ذات تقييد المحتوى ويرسلها للخاص.",
        "usage": "{tr}سيف يوزر_القناة العدد",
    },
)
async def _(event):
    global cancel_process
    cancel_process = False  # إعادة ضبط الفلاج

    channel_username = event.pattern_match.group(1)
    limit = int(event.pattern_match.group(2))

    if not channel_username:
        return await edit_or_reply(event, "⚠️ يجب تحديد اسم القناة!")

    save_dir = "media"
    os.makedirs(save_dir, exist_ok=True)

    try:
        channel_entity = await zedub.get_entity(channel_username)
        messages = await zedub.get_messages(channel_entity, limit=limit)
    except Exception as e:
        return await edit_or_reply(
            event, f"❌ خطأ أثناء جلب الرسائل من القناة:\n`{str(e)}`"
        )

    status = await edit_or_reply(event, "⏳ جاري حفظ الميديا ...")

    for message in messages:
        try:
            if message.media:
                file_ext = ""
                if message.photo:
                    file_ext = ".jpg"
                elif message.video:
                    file_ext = ".mp4"
                elif message.document:
                    if hasattr(message.document, "file_name"):
                        file_ext = os.path.splitext(message.document.file_name)[1]
                    else:
                        file_ext = ""

                if not file_ext:
                    continue

                file_path = os.path.join(save_dir, f"media_{message.id}{file_ext}")
                await message.download_media(file=file_path)
                await zedub.send_file("me", file=file_path)
                os.remove(file_path)

            # تحقق من الإلغاء
            if cancel_process:
                await status.edit("⚠️ تم إلغاء عملية حفظ الميديا.")
                cancel_process = False
                return
        except Exception as e:
            LOGS.error(f"خطأ أثناء حفظ الرسالة {message.id}: {str(e)}")
            continue

    await status.edit(f"✅ تم حفظ الميديا من القناة {channel_username} بنجاح.")
