import json
import os
import asyncio
import aiohttp
import random
from telethon.tl.types import Chat, Channel
from .. import zedub  # نفس استدعاء سورس يمنثون

ADHKAR_FILE = "adhkar_chats.json"

def load_adhkar_chats():
    if os.path.exists(ADHKAR_FILE):
        with open(ADHKAR_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_adhkar_chats(data):
    with open(ADHKAR_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

adhkar_chats = load_adhkar_chats()

async def get_random_zekr():
    url = "https://raw.githubusercontent.com/Ashqalsmt/azkar/main/azkar.json"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                data = await resp.json()
                all_azkar = []
                for category in data.values():
                    for zekr in category:
                        all_azkar.append(zekr["content"])
                if all_azkar:
                    return random.choice(all_azkar)
    except:
        return None
    return None

@zedub.zed_cmd(pattern="تفعيل الاذكار$")
async def enable_adhkar(event):
    chat_id = event.chat_id
    if chat_id not in adhkar_chats:
        adhkar_chats.append(chat_id)
        save_adhkar_chats(adhkar_chats)
        await event.reply("✅ تم تفعيل الأذكار في هذه المجموعة/القناة")
    else:
        await event.reply("ℹ️ الأذكار مفعلة بالفعل هنا")

@zedub.zed_cmd(pattern="تعطيل الاذكار$")
async def disable_adhkar(event):
    adhkar_chats.clear()
    save_adhkar_chats(adhkar_chats)
    await event.reply("⛔ تم تعطيل الأذكار في جميع المجموعات والقنوات")

@zedub.zed_cmd(pattern="الاذكار المفعله$")
async def list_adhkar_chats(event):
    if not adhkar_chats:
        return await event.reply("ℹ️ لا يوجد أي مجموعات أو قنوات مفعّل فيها نشر الأذكار")

    result = "**📜 قائمة المجموعات والقنوات المفعلة:**\n\n"
    for idx, chat_id in enumerate(adhkar_chats, start=1):
        try:
            entity = await event.client.get_entity(chat_id)
            if isinstance(entity, Channel):
                name = entity.title
            elif isinstance(entity, Chat):
                name = entity.title
            else:
                name = f"محادثة خاصة {chat_id}"
            result += f"{idx}. {name} (`{chat_id}`)\n"
        except:
            result += f"{idx}. غير معروف (`{chat_id}`)\n"

    await event.reply(result)

async def adhkar_loop():
    while True:
        if adhkar_chats:
            zekr = await get_random_zekr()
            if zekr:
                for chat_id in list(adhkar_chats):
                    try:
                        await zedub.send_message(chat_id, zekr)
                    except:
                        pass
        await asyncio.sleep(300)  # 5 دقائق

zedub.loop.create_task(adhkar_loop())
