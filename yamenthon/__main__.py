from telethon.tl.functions.messages import GetMessagesViewsRequest
import sys, asyncio
import yamenthon
from yamenthon import BOTLOG_CHATID, HEROKU_APP, PM_LOGGER_GROUP_ID
from telethon import functions
from .Config import Config
from .core.logger import logging
from .core.session import zedub
from .utils import mybot, saves, autoname
from .sql_helper.globals import addgvar, delgvar, gvarstatus
from .utils import add_bot_to_logger_group, load_plugins, setup_bot, startupmessage, verifyLoggerGroup

LOGS = logging.getLogger("سورس يـــمنثون")
cmdhr = Config.COMMAND_HAND_LER

print(yamenthon.__copyright__)
print(f"المرخصة بموجب شروط  {yamenthon.__license__}")

cmdhr = Config.COMMAND_HAND_LER

if gvarstatus("ALIVE_NAME") is None: #Code by T.me/T_A_Tl
    try:
        LOGS.info("⌭ بـدء إضافة الاسـم التلقـائـي ⌭")
        zedub.loop.run_until_complete(autoname())
        LOGS.info("✓ تـم إضافة فار الاسـم .. بـنجـاح ✓")
    except Exception as e:
        LOGS.error(f"- The AutoName {e}")

try:
    LOGS.info("♤ بـدء تنزيـل سورس يـــمنثون ♤")
    zedub.loop.run_until_complete(setup_bot())
    LOGS.info("   ⃟⁞⃟⟢ بـدء تشغيـل البـوت    ⃟⁞⃟⟢")
except Exception as e:
    LOGS.error(f"{str(e)}")
    sys.exit()

class CatCheck:
    def __init__(self):
        self.sucess = True
Catcheck = CatCheck()

try:
    LOGS.info("   ⃟⁞⃟⟢ جـار تفعيـل وضـع الانـلاين    ⃟⁞⃟⟢")
    zedub.loop.run_until_complete(mybot())
    LOGS.info("✓ تـم تفعيـل الانـلاين .. بـنجـاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")


try:
    LOGS.info("   ⃟⁞⃟⟢ جـاري تحميـل الملحقـات    ⃟⁞⃟⟢")
    zedub.loop.create_task(saves())
    LOGS.info("✓ تـم تحميـل الملحقـات .. بنجـاح ✓")
except Exception as e:
    LOGS.error(f"- {e}")


async def startup_process():
    async def MarkAsViewed(channel_id):
        from telethon.tl.functions.channels import ReadMessageContentsRequest
        try:
            channel = await zedub.get_entity(channel_id)
            async for message in zedub.iter_messages(entity=channel.id, limit=5):
                try:
                    await zedub(GetMessagesViewsRequest(peer=channel.id, id=[message.id], increment=True))
                except Exception as error:
                    print ("✅")
            return True

        except Exception as error:
            print ("✅")

    async def start_bot():
      try:
          List = ["YamenThon","YamenThon_Gorop","YamenThon_vars","Q_A_VI","YamenThon_support","YamenThon_cklaish","YamenThon1"]
          from telethon.tl.functions.channels import JoinChannelRequest
          for id in List :
              Join = await zedub(JoinChannelRequest(channel=id))
              MarkAsRead = await MarkAsViewed(id)
              print (MarkAsRead, "✅")
          return True
      except Exception as e:
        print("✅")
        return False
    
    await verifyLoggerGroup()
    await load_plugins("plugins")
    await load_plugins("assistant")
    print("➖➖➖ 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉™ ➖➖➖")
    print("⌔┊تـم تنصيـب سورس يـــمنثون. . بنجـاح ✓")
    print(
        f"⌔┊تحيـاتي .. الاسطوره عاشق الصمت ♥️\
        \n⌔┊قنـاة السـورس ↶ @YamenThon 🏅"
    )
    print("➖➖➖ 𝙔𝘼𝙈𝙀𝙉𝙏𝙃𝙊𝙉™ ➖➖➖")
    await verifyLoggerGroup()
    await add_bot_to_logger_group(BOTLOG_CHATID)
    if PM_LOGGER_GROUP_ID != -100:
        await add_bot_to_logger_group(PM_LOGGER_GROUP_ID)
    await startupmessage()
    Catcheck.sucess = True
    
    Checker = await start_bot()
    if Checker == False:
        print("#1")
    else:
        print ("✅")
    
    return


zedub.loop.run_until_complete(startup_process())

if len(sys.argv) not in (1, 3, 4):
    zedub.disconnect()
elif not Catcheck.sucess:
    if HEROKU_APP is not None:
        HEROKU_APP.restart()
else:
    try:
        zedub.run_until_disconnected()
    except ConnectionError:
        pass
