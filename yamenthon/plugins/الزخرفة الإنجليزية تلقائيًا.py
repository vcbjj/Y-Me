from telethon import events

from yamenthon import zedub

from ..sql_helper.globals import addgvar, delgvar, gvarstatus


@zedub.zed_cmd(pattern="تفعيل الزخرفة الانجليزية")
async def zakrafaon(event):
    if not gvarstatus("enzakrafa"):
        addgvar("enzakrafa", "on")
        await edit_delete(event, "**⪼ تـم تـفعـيل الزخـرفـة الإنـجليـزيـة تلقائـيّا**")
        return
    if gvarstatus("enzakrafa"):
        await edit_delete(event, "**⪼ الزخـرفـة الإنـجـليزيـة مفـعلـة سـابـقًا**")
        return


@zedub.zed_cmd(pattern="ايقاف الزخرفة الانجليزية")
async def zakrafaoff(event):
    if not gvarstatus("enzakrafa"):
        await edit_delete(event, "*⪼ عـذرًا عـزيـزي أنـت لـم تقـم بتـعطيل الزخـرفـة الإنجلـيزية تلقـائيًا**")
        return
    if gvarstatus("enzakrafa"):
        delgvar("enzakrafa")
        await edit_delete(event, "**⪼ تـم تـعطـيل الزخرفـة الإنـجليـزيـة تلقـائيًا**")
        return


@zedub.on(events.NewMessage(outgoing=True))
async def zakrafarun(event):
    if gvarstatus("enzakrafa"):
        text = event.message.message
        uppercase_text = (
            text.replace("a", "𝗮").replace("A", "𝗔")
            .replace("b", "𝗯").replace("B", "𝗕")
            .replace("c", "𝗰").replace("C", "𝗖")
            .replace("d", "𝗱").replace("D", "𝗗")
            .replace("e", "𝗲").replace("E", "𝗘")
            .replace("f", "𝗳").replace("F", "𝗙")
            .replace("g", "𝗴").replace("G", "𝗚")
            .replace("h", "𝗵").replace("H", "𝗛")
            .replace("i", "𝗶").replace("I", "𝗜")
            .replace("j", "𝗷").replace("J", "𝗝")
            .replace("k", "𝗸").replace("K", "𝗞")
            .replace("l", "𝗹").replace("L", "𝗟")
            .replace("m", "𝗺").replace("M", "𝗠")
            .replace("n", "𝗻").replace("N", "𝗡")
            .replace("o", "𝗼").replace("O", "𝗢")
            .replace("p", "𝗽").replace("P", "𝗣")
            .replace("q", "𝗾").replace("Q", "𝗤")
            .replace("r", "𝗿").replace("R", "𝗥")
            .replace("s", "𝘀").replace("S", "𝗦")
            .replace("t", "𝘁").replace("T", "𝗧")
            .replace("u", "𝘂").replace("U", "𝗨")
            .replace("v", "𝘃").replace("V", "𝗩")
            .replace("w", "𝘄").replace("W", "𝗪")
            .replace("x", "𝘅").replace("X", "𝗫")
            .replace("y", "𝘆").replace("Y", "𝗬")
            .replace("z", "𝘇").replace("Z", "𝗭")
        )
        await event.edit(uppercase_text)
