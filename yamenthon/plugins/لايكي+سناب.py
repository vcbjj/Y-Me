#الملف حقوق وكتابه الاسطوره عاشق الصمت 
#تبي تخمط الملف تابع لسورس يمنثون 
#احترم عقلك وكتب كود تحميـل ترا سهل 
#بس شغلكم تخميط بس ههههه😂
#خذ الكود عادي بس لا تقول انه تبعك
# سورس يمنثون - عاشق الصمت
from .. import zedub
from ..core.managers import edit_or_reply
from telethon import events
import aiohttp
import mimetypes
import tempfile
import os
import re

API_BASE = "https://secretv1.sbs/api/v9?url="

async def download_and_send(event, platform, link):
    zed = await edit_or_reply(event, f"⏳ جاري التحميل من {platform}...")

    try:
        # جلب الملف من API
        async with aiohttp.ClientSession() as session:
            async with session.get(API_BASE + link) as resp:
                if resp.status != 200:
                    return await zed.edit("⚠️ لم أستطع جلب الوسائط، تأكد من الرابط.")
                
                content_type = resp.headers.get("Content-Type", "").lower()
                ext = mimetypes.guess_extension(content_type.split(";")[0]) or ".mp4"

                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                temp_file.write(await resp.read())
                temp_file.close()

        # إرسال الملف
        await event.client.send_file(
            event.chat_id,
            file=temp_file.name,
            caption=f"𝑶𝑲📥𝑫𝑶𝑾𝑵𝑳𝑶𝑨𝑫 {platform} \n[➧𝙎𝙊𝙐𝙍𝘾𝙀 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉](https://t.me/YamenThon)"
        )

        # حذف الملف المؤقت
        os.remove(temp_file.name)
        await zed.delete()

    except Exception as e:
        await zed.edit(f"❌ خطأ: {str(e)}")

def register_command(pattern, platform_name, domain_pattern):
    @zedub.zed_cmd(pattern=pattern)
    async def handler(event):
        reply = await event.get_reply_message()
        link = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else (reply.text.strip() if reply else "")

        if not link or not re.search(domain_pattern, link):
            return await edit_or_reply(event, f"📌 أرسل رابط {platform_name} بعد الأمر أو بالرد على الرابط.")

        await download_and_send(event, platform_name, link)

# تسجيل الأوامر
register_command(r"سناب(?:\s+|$)(.*)", "𝑺𝑵𝑨𝑷 𝑪𝑯𝑨𝑻", r"(snapchat\.com)")
register_command(r"لايكي(?:\s+|$)(.*)", "𝑳𝑰𝑲𝑬𝑬", r"(likee\.video|likee\.app)")
register_command(r"فيس(?:\s+|$)(.*)", "𝑭𝑨𝑪𝑬𝑩𝑶𝑶𝑲", r"(facebook\.com|fb\.watch)")
register_command(r"تويتر(?:\s+|$)(.*)", "𝑻𝑾𝑰𝑻𝑻𝑬𝑹⍣𝑿", r"(twitter\.com|x\.com)")
