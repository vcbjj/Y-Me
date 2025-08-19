import asyncio
from yamenthon import zedub
from telethon import events, TelegramClient
from telethon.tl.custom import Button
from telethon.sessions import StringSession
from ..Config import Config

plugin_category = "البوتات"

# ┈┅━╍╍━━┅┈┅━━╍╍━┅┈ #
#     الدوال المساعدة     #
# ┈┅━╍╍━━┅┈┅━━╍╍━┅┈ #

async def interact_with_botfather_step_by_step(client, steps):
    try:
        async with client.conversation('BotFather', timeout=30) as conv:
            responses = []
            for step in steps:
                await conv.send_message(step['command'])
                response = await conv.get_response()
                responses.append(response.text)
            return responses
    except asyncio.TimeoutError:
        return "⏳ انتهت المهلة أثناء انتظار الرد من بوت فاذر"
    except Exception as e:
        return f"⚠️ حدث خطأ أثناء التفاعل مع بوت فاذر: {str(e)}"

# ┈┅━╍╍━━┅┈┅━━╍╍━┅┈ #
#     صنع بوت جديد     #
# ┈┅━╍╍━━┅┈┅━━╍╍━┅┈ #

@zedub.on(events.NewMessage(pattern=r'\.صنع بوت (.*)'))
async def create_bot(event):
    try:
        input_str = event.pattern_match.group(1)
        
        # التحقق من صحة المدخلات
        if ' ' not in input_str:
            await event.respond(
                "**⎉╎خطأ في الصيغة!**\n"
                "**⎉╎يجب كتابة اسم البوت ويوزره مع المسافة بينهم**\n"
                "**⎉╎مثال:** `.صنع بوت MyBot mybot`\n"
                "**⎉╎ملاحظة:** اليوزر يجب أن ينتهي بـ `bot` أو `_bot`"
            )
            return
            
        name, username = input_str.split(' ', 1)
        if username.startswith('@'):
            username = username[1:]
        
        # التحقق من صحة اليوزرنيم
        if not (username.lower().endswith('bot') or username.lower().endswith('_bot')):
            await event.respond(
                "**⎉╎خطأ في اليوزر!**\n"
                "**⎉╎يجب أن ينتهي يوزر البوت بـ `bot` أو `_bot`**\n"
                "**⎉╎مثال:** `mybot` أو `my_bot`"
            )
            return

        async with TelegramClient(StringSession(Config.STRING_SESSION), Config.APP_ID, Config.API_HASH) as client:
            # خطوات إنشاء البوت
            steps = [
                {'command': '/newbot'},
                {'command': name},
                {'command': username}
            ]
            
            results = await interact_with_botfather_step_by_step(client, steps)
            
            if not results or len(results) < 3:
                await event.respond(
                    "**⎉╎فشل في إنشاء البوت!**\n"
                    "**⎉╎لم يتم الحصول على ردود كافية من بوت فاذر**"
                )
                return
                
            final_response = results[-1]
            
            if any(keyword in final_response for keyword in ["Done!", "تم!", "token"]):
                # الحصول على التوكن
                token_steps = [
                    {'command': '/token'},
                    {'command': f'@{username}'}
                ]

                token_results = await interact_with_botfather_step_by_step(client, token_steps)

                if not token_results or len(token_results) < 2:
                    await event.respond(
                        f"**⎉╎تم إنشاء البوت بنجاح!**\n"
                        f"**⎉╎اليوزر:** @{username}\n"
                        f"**⎉╎ولكن لم يتم الحصول على التوكن**"
                    )
                    return

                token_response = token_results[1]
                
                if "Use this token" in token_response or "استخدم هذا الرمز" in token_response:
                    # استخراج التوكن بدقة
                    token = None
                    if '`' in token_response:
                        token = token_response.split('`')[1]
                    else:
                        for line in token_response.split('\n'):
                            if len(line) > 30 and 'bot' in line.lower():
                                token = line.strip()
                                break

                    if token:
                        await event.respond(
                            "**⎉╎تم إنشاء البوت بنجاح!** ✅\n\n"
                            f"**⎉╎اسم البوت:** `{name}`\n"
                            f"**⎉╎يوزر البوت:** @{username}\n"
                            f"**⎉╎توكن البوت:** `{token}`\n\n"
                            "**⎉╎يمكنك التحكم في البوت باستخدام الأمر:**\n"
                            f"`.تعديل @{username}`",
                            parse_mode='md'
                        )
                    else:
                        await event.respond(
                            f"**⎉╎تم إنشاء البوت!**\n"
                            f"**⎉╎اليوزر:** @{username}\n"
                            "**⎉╎ولكن لم يتم الحصول على التوكن**\n"
                            f"**⎉╎الرد:** `{token_response[:100]}...`"
                        )
                else:
                    await event.respond(
                        f"**⎉╎تم إنشاء البوت!**\n"
                        f"**⎉╎اليوزر:** @{username}\n"
                        "**⎉╎ولكن لم يتم الحصول على التوكن**"
                    )
            else:
                await event.respond(
                    "**⎉╎فشل في إنشاء البوت!** ❌\n"
                    "**⎉╎قد يكون اليوزر محجوزاً أو غير صالح**\n\n"
                    f"**⎉╎الرد من بوت فاذر:**\n`{final_response}`"
                )
                
    except Exception as e:
        await event.respond(
            "**⎉╎حدث خطأ غير متوقع!** ‼️\n"
            f"**⎉╎الخطأ:** `{str(e)}`"
        )

# ┈┅━╍╍━━┅┈┅━━╍╍━┅┈ #
#    إدارة البوتات    #
# ┈┅━╍╍━━┅┈┅━━╍╍━┅┈ #

@zedub.on(events.NewMessage(pattern=r'\.تعديل (@?\w+)'))
async def manage_bot(event):
    try:
        username = event.pattern_match.group(1)
        if not username.startswith('@'):
            username = f"@{username}"
        
        buttons = [
            [Button.inline("🔄 تغيير اسم البوت", b"change_name")],
            [Button.inline("📝 تغيير وصف البوت", b"change_desc")],
            [Button.inline("🖼️ تغيير صورة البوت", b"change_pic")],
            [Button.inline("🗑️ حذف البوت", b"delete_bot")],
            [Button.inline("🔑 الحصول على التوكن", b"get_token")],
        ]
        
        await event.respond(
            f"**⎉╎مرحباً بك في لوحة تحكم البوت** {username}\n"
            "**⎉╎اختر الإجراء الذي تريد تنفيذه:**",
            buttons=buttons
        )
    except Exception as e:
        await event.respond(
            "**⎉╎حدث خطأ!** ‼️\n"
            f"**⎉╎الخطأ:** `{str(e)}`"
        )

# ┈┅━╍╍━━┅┈┅━━╍╍━┅┈ #
#    معالجة الأزرار    #
# ┈┅━╍╍━━┅┈┅━━╍╍━┅┈ #

@zedub.on(events.CallbackQuery(data=b"change_name"))
async def change_name_handler(event):
    try:
        async with event.client.conversation(event.sender_id) as conv:
            await conv.send_message(
                "**⎉╎أرسل الاسم الجديد للبوت:**\n"
                "**⎉╎ملاحظة:** يجب أن يكون الاسم بين 3-64 حرف"
            )
            name_response = await conv.get_response()
            new_name = name_response.text
            
            original_msg = await event.get_message()
            username = original_msg.text.split()[-1]
            
            async with TelegramClient(StringSession(Config.STRING_SESSION), Config.APP_ID, Config.API_HASH) as client:
                steps = [
                    {'command': f'/setname {username}'},
                    {'command': new_name}
                ]
                result = await interact_with_botfather_step_by_step(client, steps)
                
                if result and any(keyword in result[-1] for keyword in ["Done!", "تم!"]):
                    await event.respond(
                        f"**⎉╎تم تغيير اسم البوت بنجاح!** ✅\n"
                        f"**⎉╎اليوزر:** {username}\n"
                        f"**⎉╎الاسم الجديد:** `{new_name}`"
                    )
                else:
                    await event.respond(
                        "**⎉╎فشل في تغيير الاسم!** ❌\n"
                        f"**⎉╎الرد:** `{result[-1] if result else 'لا يوجد رد'}`"
                    )
    except Exception as e:
        await event.respond(
            "**⎉╎حدث خطأ!** ‼️\n"
            f"**⎉╎الخطأ:** `{str(e)}`"
        )

# باقي الدوال بنفس النمط مع الزخارف...

@zedub.on(events.CallbackQuery(data=b"change_desc"))
async def change_desc_handler(event):
    try:
        async with event.client.conversation(event.sender_id) as conv:
            await conv.send_message(
                "**⎉╎أرسل الوصف الجديد للبوت:**\n"
                "**⎉╎ملاحظة:** يمكن أن يصل طول الوصف إلى 512 حرف"
            )
            desc_response = await conv.get_response()
            new_desc = desc_response.text
            
            original_msg = await event.get_message()
            username = original_msg.text.split()[-1]
            
            async with TelegramClient(StringSession(Config.STRING_SESSION), Config.APP_ID, Config.API_HASH) as client:
                steps = [
                    {'command': f'/setdescription {username}'},
                    {'command': new_desc}
                ]
                result = await interact_with_botfather_step_by_step(client, steps)
                
                if result and any(keyword in result[-1] for keyword in ["Done!", "تم!"]):
                    await event.respond(
                        f"**⎉╎تم تغيير وصف البوت بنجاح!** ✅\n"
                        f"**⎉╎اليوزر:** {username}"
                    )
                else:
                    await event.respond(
                        "**⎉╎فشل في تغيير الوصف!** ❌\n"
                        f"**⎉╎الرد:** `{result[-1] if result else 'لا يوجد رد'}`"
                    )
    except Exception as e:
        await event.respond(
            "**⎉╎حدث خطأ!** ‼️\n"
            f"**⎉╎الخطأ:** `{str(e)}`"
        )

# يمكنك إضافة باقي الدوال بنفس النمط...


@zedub.on(events.CallbackQuery(data=b"change_pic"))
async def change_pic_handler(event):
    try:
        async with event.client.conversation(event.sender_id) as conv:
            await conv.send_message("⎉╎أرسل لي الصورة الجديدة للبوت (كصورة وليس كملف):")
            pic_response = await conv.get_response()
            
            original_msg = await event.get_message()
            username = original_msg.text.split()[-1]
            
            if pic_response.photo or pic_response.document.mime_type.startswith('image/'):
                async with TelegramClient(StringSession(Config.STRING_SESSION), Config.APP_ID, Config.API_HASH) as client:
                    await client.send_file(
                        'BotFather',
                        pic_response.media,
                        caption=f"/setuserpic {username}"
                    )
                    await asyncio.sleep(5)
                    await event.respond(f"⎉╎✅ تم استلام الصورة ومعالجتها للبوت {username}")
            else:
                await event.respond("⎉╎❌ لم يتم إرسال صورة صالحة!")
    except Exception as e:
        await event.respond(f"⎉╎❌ حدث خطأ: {str(e)}")

@zedub.on(events.CallbackQuery(data=b"delete_bot"))
async def delete_bot_handler(event):
    try:
        original_msg = await event.get_message()
        username = original_msg.text.split()[-1]
        
        confirm_buttons = [
            [Button.inline("✅ نعم، احذف البوت", b"confirm_delete")],
            [Button.inline("❌ إلغاء", b"cancel_delete")]
        ]
        
        await event.respond(
            f"⎉╎هل أنت متأكد من حذف البوت {username}؟ لا يمكن التراجع عن هذا الإجراء!",
            buttons=confirm_buttons
        )
    except Exception as e:
        await event.respond(f"⎉╎❌ حدث خطأ: {str(e)}")

@zedub.on(events.CallbackQuery(data=b"confirm_delete"))
async def confirm_delete_handler(event):
    try:
        original_msg = await event.get_message()
        username = original_msg.text.split()[-2]
        
        async with TelegramClient(StringSession(Config.STRING_SESSION), Config.APP_ID, Config.API_HASH) as client:
            result = await interact_with_botfather(
                client,
                f"/deletebot {username}",
                wait_for=True
            )
            
            if result and ("Done!" in result or "تم!" in result):
                await event.respond(f"⎉╎✅ تم حذف البوت {username} بنجاح")
            else:
                await event.respond(f"⎉╎❌ فشل في حذف البوت.\nالرد: {result if result else 'لا يوجد رد'}")
    except Exception as e:
        await event.respond(f"⎉╎❌ حدث خطأ: {str(e)}")

@zedub.on(events.CallbackQuery(data=b"cancel_delete"))
async def cancel_delete_handler(event):
    try:
        await event.respond("⎉╎تم إلغاء عملية الحذف")
    except Exception as e:
        await event.respond(f"⎉╎❌ حدث خطأ: {str(e)}")

@zedub.on(events.CallbackQuery(data=b"get_token"))
async def get_token_handler(event):
    try:
        original_msg = await event.get_message()
        username = original_msg.text.split()[-1]
        
        async with TelegramClient(StringSession(Config.STRING_SESSION), Config.APP_ID, Config.API_HASH) as client:
            token_msg = await interact_with_botfather(
                client,
                f"/token {username}",
                wait_for=True
            )
            
            if token_msg and ("Use this token" in token_msg or "استخدم هذا الرمز" in token_msg):
                token = token_msg.split('\n')[-1].strip()
                await event.respond(
                    f"⎉╎✅ توكن البوت {username}:\n\n`{token}`",
                    parse_mode='md'
                )
            else:
                await event.respond(f"⎉╎❌ لم يتم الحصول على التوكن.\nالرد: {token_msg if token_msg else 'لا يوجد رد'}")
    except Exception as e:
        await event.respond(f"⎉╎❌ حدث خطأ: {str(e)}")
