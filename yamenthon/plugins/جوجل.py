# reverse search and google search plugin for yamenthon
import contextlib
import os
import re
import urllib
from datetime import datetime
import asyncio
import random

import requests
from bs4 import BeautifulSoup
from PIL import Image
from search_engine_parser import BingSearch, GoogleSearch, YahooSearch
from search_engine_parser.core.exceptions import NoResultsOrTrafficError

from . import BOTLOG, BOTLOG_CHATID, Convert, zedub

from ..Config import Config
from ..core.managers import edit_delete, edit_or_reply
from ..helpers.functions import deEmojify
from ..helpers.utils import reply_id

opener = urllib.request.build_opener()
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64)",
]
# اختَر User-Agent عشوائي عند تحميل الموديول (يمكن تغييره لاحقًا إن أردت تدوير كل طلب)
opener.addheaders = [("User-Agent", random.choice(user_agents))]

plugin_category = "البحث"


async def ParseSauce(googleurl):
    """Parse/Scrape the HTML code for the info we want."""
    # نستخدم opener (مع User-Agent المحدد أعلاه)
    source = opener.open(googleurl).read()
    soup = BeautifulSoup(source, "html.parser")
    results = {"similar_images": "", "best_guess": ""}
    with contextlib.suppress(BaseException):
        for similar_image in soup.findAll("input", {"class": "gLFyf"}):
            url = "https://www.google.com/search?tbm=isch&q=" + urllib.parse.quote_plus(
                similar_image.get("value")
            )
            results["similar_images"] = url
    for best_guess in soup.findAll("div", attrs={"class": "r5a77d"}):
        results["best_guess"] = best_guess.get_text()
    return results


async def scam(results, lim):
    """
    يقرأ صفحة الصور المماثلة التي حصلنا عليها من ParseSauce ثم يجمع روابط الصور.
    أضفنا sleep عشوائي بين كل طلب لتخفيف الضغط وتقليل فرص الحصول على 429.
    """
    single = opener.open(results["similar_images"]).read()
    decoded = single.decode("utf-8")
    imglinks = []
    counter = 0
    pattern = r"^,\[\"(.*[.png|.jpg|.jpeg])\",[0-9]+,[0-9]+\]$"
    oboi = re.findall(pattern, decoded, re.I | re.M)
    for imglink in oboi:
        counter += 1
        if counter <= int(lim):
            imglinks.append(imglink)
            # تأخير عشوائي بسيط بين طلب وآخر حتى لا يبدو الاتّصال بوتي جداً
            await asyncio.sleep(random.uniform(1.5, 3.5))
        else:
            break
    return imglinks


async def reverse_image_search(image_path, lim=3):
    """
    تحميل الصورة إلى Google Reverse Image Search أولًا.
    إذا نجح: ترجع ("google", results_dict, fetchUrl)
    إذا فشل (مثل 429) → ترجع fallback رسالة لـ Bing/Yandex بشكل مقروء:
        ("bing", ["رسالة توضيحية"], None)
    """
    # جرب Google أولًا
    try:
        # افتح الملف بطريقة تضمن إغلاقه
        with open(image_path, "rb") as f:
            multipart = {"encoded_image": (image_path, f), "image_content": ""}
            searchUrl = "https://www.google.com/searchbyimage/upload"
            response = requests.post(searchUrl, files=multipart, allow_redirects=False, timeout=30)

        # تحقق من حالة الرد
        # Google عادة يعيد 302 مع ترويسة Location التي تُمثّل صفحة النتائج
        if response.status_code == 429:
            # حُدّث Rate limit
            raise Exception("Google rate limit (429)")

        if "Location" not in response.headers:
            # لم نحصل على رابط نتائج Google — نعتبرها فشل
            raise Exception(f"Unexpected Google response: {response.status_code}")

        fetchUrl = response.headers.get("Location")
        # احصل على نتائج ParseSauce من الصفحة المحوّلة
        results = await ParseSauce(f"{fetchUrl}&preferences?hl=en&fg=1#languages")
        # إرجاع نتائج Google مع رابط الصفحة (fetchUrl)
        return ("google", results, fetchUrl)

    except Exception as google_err:
        # لو فشل Google — لا نحاول رفع الصورة إلى Bing لأن search_engine_parser لا يدعم Reverse Image مباشرة
        # لذلك نُرجع رسالة بديلة تقترح الحلول للمستخدم (fallback)
        try:
            # بديل نصي: نستخدم Bing/GSearch text search كحل مؤقت (لن يكون بحث عكسي حقيقي)
            # لكن نستطيع محاولة استخراج "أقرب وصف" من اسم الملف أو تحذير المستخدم
            # هنا سنُعيد رسالة توضيحية لـ Bing
            bing_msg = [
                "تعذر الحصول على نتيجة مباشرة من Google (سبب: {}).".format(str(google_err)),
                "كحل مؤقت: حاول استخدام نتائج البحث النصي في Bing أو استخدام Yandex reverse image عبر المتصفح.",
                "ملاحظة: مكتبة search_engine_parser لا تدعم رفع صور للبحث العكسي في Bing، لذلك البحث اليدوي قد يكون الضروري."
            ]
            return ("bing", bing_msg, None)
        except Exception:
            # في حال فشل كل شيء نعيد رسالة موحّدة
            return ("yandex", ["ما قدرت أجيب نتائج من Google أو Bing 😅 — جرّب البحث اليدوي في Yandex أو الموقع المباشر."], None)


@zedub.zed_cmd(
    pattern="جو ([\s\S]*)",
    command=("جو", plugin_category),
    info={
        "header": "Google search command.",
        "امر مضاف": {
            "-l": "for number of search results.",
            "-p": "for choosing which page results should be showed.",
        },
        "الاسـتخـدام": [
            "{tr}جو + الامر المضاف + كلمـه",
            "{tr}جو + كلمـه",
        ],
        "مثــال": [
            "{tr}جو صدام حسين",
            "{tr}جو عدد6 صدام حسين",
            "{tr}جو صفحه2 صدام حسين",
            "{tr}جو صفحه2 عدد7 صدام حسين",
        ],
    },
)
async def gsearch(q_event):
    "Google search command."
    zedevent = await edit_or_reply(q_event, "**- جـارِ البحـث في جوجــل...**")
    match = q_event.pattern_match.group(1)
    page = re.findall(r"صفحه\d+", match)
    lim = re.findall(r"عدد\d+", match)
    try:
        page = page[0]
        page = page.replace("صفحه", "")
        match = match.replace(f"صفحه{page}", "")
    except IndexError:
        page = 1
    try:
        lim = lim[0]
        lim = lim.replace("عدد", "")
        match = match.replace(f"عدد{lim}", "")
        lim = int(lim)
        if lim <= 0:
            lim = 5
    except IndexError:
        lim = 5
    #     smatch = urllib.parse.quote_plus(match)
    smatch = match.replace(" ", "+")
    search_args = str(smatch), page
    gsearch = GoogleSearch()
    bsearch = BingSearch()
    ysearch = YahooSearch()
    try:
        gresults = await gsearch.async_search(*search_args)
    except NoResultsOrTrafficError:
        try:
            gresults = await bsearch.async_search(*search_args)
        except NoResultsOrTrafficError:
            try:
                gresults = await ysearch.async_search(*search_args)
            except Exception as e:
                return await edit_delete(zedevent, f"**- خطـأ :**\n`{e}`", time=10)
    msg = ""
    for i in range(lim):
        if i > len(gresults["links"]):
            break
        try:
            title = gresults["titles"][i]
            link = gresults["links"][i]
            desc = gresults["descriptions"][i]
            msg += f"👉[{title}]({link})\n`{desc}`\n\n"
        except IndexError:
            break
    await edit_or_reply(
        zedevent,
        "**- بحث جوجــل :**\n`" + match + "`\n\n**- النتائـج :**\n" + msg,
        link_preview=False,
        aslink=True,
        linktext=f"**- نتـائـج البحـث عن الكلمــه **__{match}__ **هـي :**",
    )
    if BOTLOG:
        await q_event.client.send_message(
            BOTLOG_CHATID,
            f"**- تم البحث عن الكلمـه ** `{match}` **بنجـاح✓**",
        )


@zedub.zed_cmd(
    pattern="مصادر ([\s\S]*)",
    command=("مصادر", plugin_category),
    info={
        "header": "Google search in image format",
        "الاسـتخـدام": "{tr}gis <query>",
        "مثــال": "{tr}gis cat",
    },
)
async def _(event):
    "To search in google and send result in picture."


@zedub.zed_cmd(
    pattern="مصادر$",
    command=("مصادر", plugin_category),
    info={
        "header": "Google reverse search command.",
        "الاسـتخـدام": "{tr}grs",
    },
)
async def grs(event):
    "Google Reverse Search"
    start = datetime.now()
    OUTPUT_STR = "Reply to an image to do Google Reverse Search"
    if event.reply_to_msg_id:
        zedevent = await edit_or_reply(event, "Pre Processing Media")
        previous_message = await event.get_reply_message()
        previous_message_text = previous_message.message
        BASE_URL = "http://www.google.com"
        if previous_message.media:
            photo = await Convert.to_image(
                event,
                previous_message,
                dirct="./temp",
                file="grs.png",
            )
            if photo[1] is None:
                return await edit_delete(
                    photo[0], "__Unable to extract image from the replied message.__"
                )
            SEARCH_URL = f"{BASE_URL}/searchbyimage/upload"
            multipart = {
                "encoded_image": (
                    photo[1],
                    open(photo[1], "rb"),
                ),
                "image_content": "",
            }
            # https://stackoverflow.com/a/28792943/4723940
            google_rs_response = requests.post(
                SEARCH_URL, files=multipart, allow_redirects=False
            )
            the_location = google_rs_response.headers.get("Location")
            os.remove(photo[1])
        else:
            previous_message_text = previous_message.message
            SEARCH_URL = "{}/searchbyimage?image_url={}"
            request_url = SEARCH_URL.format(BASE_URL, previous_message_text)
            google_rs_response = requests.get(request_url, allow_redirects=False)
            the_location = google_rs_response.headers.get("Location")
        await zedevent.edit("Found Google Result. Pouring some soup on it!")
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:84.0) Gecko/20100101 Firefox/84.0"
        }
        response = requests.get(the_location, headers=headers)
        soup = BeautifulSoup(response.text, "html.parser")
        # document.getElementsByClassName("r5a77d"): PRS
        try:
            prs_div = soup.find_all("div", {"class": "r5a77d"})[0]
            prs_anchor_element = prs_div.find("a")
            prs_url = BASE_URL + prs_anchor_element.get("href")
            prs_text = prs_anchor_element.text
            # document.getElementById("jHnbRc")
            img_size_div = soup.find(id="jHnbRc")
            img_size = img_size_div.find_all("div")
        except Exception:
            return await edit_delete(
                zedevent, "`Sorry. I am unable to find similar images`"
            )
        end = datetime.now()
        ms = (end - start).seconds
        OUTPUT_STR = """{img_size}
<b>Possible Related Search : </b> <a href="{prs_url}">{prs_text}</a> 
<b>More Info : </b> Open this <a href="{the_location}">Link</a> 
<i>fetched in {ms} seconds</i>""".format(
            **locals()
        )
    else:
        zedevent = event
    await edit_or_reply(zedevent, OUTPUT_STR, parse_mode="HTML", link_preview=False)


@zedub.zed_cmd(
    pattern="تحليل(?:\s|$)([\s\S]*)",
    command=("تحليل", plugin_category),
    info={
        "header": "Google reverse search command.",
        "الوصـف": "reverse search replied image or sticker in google and shows results. if count is not used then it send 1 image by default.",
        "الاستخـدام": "{tr}reverse <count>",
    },
)
async def reverse(event):
    "Google Reverse Search"
    reply_to = await reply_id(event)
    if os.path.isfile("okgoogle.png"):
        os.remove("okgoogle.png")
    message = await event.get_reply_message()
    if not message and not message.media:
        return await edit_or_reply(event, "**بالرد على الصـورة للبحث عن شبيهاتها في جوجل ريـفرس**")
    photo = await Convert.to_image(
        event,
        message,
        dirct="./temp",
        file="reverse.png",
    )
    if photo[1] is None:
        return await edit_delete(
            photo[0], "__Unable to extract image from the replied message.__"
        )
    catevent = await edit_or_reply(event, "** ⌔∮جـارِ البـحث عن المصادر 🎆♥️ ...**")
    try:
        image = Image.open(photo[1])
        os.remove(photo[1])
    except OSError:
        return await catevent.edit("**- ملف غيـر مدعـوم ؟!**")
    name = "okgoogle.png"
    image.save(name, "PNG")
    image.close()

    # عدد الصور المطلوب إرسالها (مبدئيًا 3 إذا لم يُكتب عدد)
    lim = event.pattern_match.group(1) or 3
    try:
        lim = int(lim)
    except Exception:
        lim = 3

    # استدعاء دالة البحث المعتمدة على Google (مع fallback توضيحي)
    source, results, fetchUrl = await reverse_image_search(name, lim=int(lim))

    if source == "google":
        # نتائج Google هي dict من ParseSauce: يحتوي على best_guess و similar_images
        guess = results.get("best_guess", "لا يوجد تخمين")
        imgspage = results.get("similar_images", "")
        # استخدم fetchUrl المعاد لعرض رابط صفحة النتائج (لو وُجد)
        if fetchUrl:
            await catevent.edit(f"[{guess}]({fetchUrl})\n\n**البحث عن هذه الصورة ...**")
        else:
            await catevent.edit(f"**أفضل تخمين:** {guess}\n\n**البحث عن هذه الصورة ...**")

        # جلب روابط الصور المشابهة ثم إرسالهـا
        images = await scam(results, lim)
        yeet = []
        for i in images:
            try:
                k = requests.get(i, timeout=30)
                yeet.append(k.content)
            except Exception:
                # تجاهل أي رابط فاشل
                continue

        with contextlib.suppress(TypeError):
            await event.client.send_file(
                entity=await event.client.get_input_entity(event.chat_id),
                file=yeet,
                reply_to=reply_to,
            )

        # عرض رابط صفحة الصور المشابهة (إن وُجد)
        if imgspage:
            if fetchUrl:
                await catevent.edit(
                    f"[{guess}]({fetchUrl})\n\n[لصـور مشابهـه اخـرى اضغط هنا...]({imgspage})"
                )
            else:
                await catevent.edit(
                    f"**أفضل تخمين:** {guess}\n\n[لصـور مشابهـه اخـرى اضغط هنا...]({imgspage})"
                )
    elif source == "bing":
        # عرض رسالة بديلة لأننا لا نملك بحث عكسي مباشر هنا
        # results هو قائمة رسائل إيضاحية
        msg = "\n".join(results) if isinstance(results, (list, tuple)) else str(results)
        await catevent.edit(f"✧ fallback (Bing) — ملاحظة:\n\n{msg}")
    else:
        # fallback عام أو yandex
        msg = results[0] if isinstance(results, (list, tuple)) else str(results)
        await catevent.edit(f"✧ fallback (Yandex) — ملاحظة:\n\n{msg}")

    # احذف الملف المؤقت
    try:
        os.remove(name)
    except Exception:
        pass


@zedub.zed_cmd(
    pattern="جوجل(?:\s|$)([\s\S]*)",
    command=("جوجل", plugin_category),
    info={
        "header": "To get link for google search",
        "الاسـتخـدام": [
            "{tr}جوجل + كلمـه",
        ],
    },
)
async def google_search(event):
    "Will show you google search link of the given query."
    input_str = event.pattern_match.group(1)
    reply_to_id = await reply_id(event)
    if not input_str:
        return await edit_delete(
            event, "**- قم باضافة كلمـة للبحث ...**"
        )
    input_str = deEmojify(input_str).strip()
    if len(input_str) > 195 or len(input_str) < 1:
        return await edit_delete(
            event,
            "__Plox your search query exceeds 200 characters or you search query is empty.__",
        )
    query = f"#12{input_str}"
    results = await event.client.inline_query("@StickerizerBot", query)
    await results[0].click(event.chat_id, reply_to=reply_to_id, hide_via=True)
    await event.delete()

AsheqSearch_cmd = (
"[ᯓ 𝗬𝗮𝗺𝗲𝗻𝗧𝗵𝗼𝗻 𝗨𝘀𝗲𝗿𝗯𝗼𝘁 - اوامــر البحــث 🔎 ](t.me/YamenThon) ."
"**⋆─┄─┄─┄─┄──┄─┄─┄─┄─⋆**\n"

"⚉ `.جو <كلمة>`\n"
"**⪼ الوصف:** البحث في جوجل (مع دعم تحديد عدد النتائج والصفحة).\n"
"**⪼ الاستخدام:**\n"
"`.جو صدام حسين`\n"
"`.جو عدد6 صدام حسين`\n"
"`.جو صفحه2 صدام حسين`\n"
"`.جو صفحه2 عدد7 صدام حسين`\n\n"

"⚉ `.مصادر <كلمة>`\n"
"**⪼ الوصف:** البحث في جوجل صور (Google Image Search).\n"
"**⪼ الاستخدام:**\n"
"`.مصادر قطة`\n\n"

"⚉ `.مصادر` بالرد على صورة\n"
"**⪼ الوصف:** البحث العكسي في جوجل (Google Reverse Search) عن صورة أو رابط صورة.\n"
"**⪼ الاستخدام:** قم بالرد على صورة أو ملصق ثم أرسل `.مصادر`\n\n"

"⚉ `.تحليل <عدد>`\n"
"**⪼ الوصف:** البحث العكسي (Reverse) للصور عبر جوجل وعرض صور مشابهة.\n"
"**⪼ الاستخدام:** قم بالرد على صورة وأرسل:\n"
"`.تحليل 3` (يجيب 3 صور مشابهة)\n"
"إذا ما كتبت العدد، يتم افتراض العدد = 3.\n\n"

"⚉ `.جوجل <كلمة>`\n"
"**⪼ الوصف:** إنشاء رابط مباشر لبحث جوجل عن الكلمة المحددة.\n"
"**⪼ الاستخدام:**\n"
"`.جوجل الذكاء الاصطناعي`\n\n"

"**⪼ هذه الأوامر تغطي البحث النصي + البحث في الصور + البحث العكسي، والتحديثات مستمرة ✓📥**\n\n"
)

@zedub.zed_cmd(pattern="البحث")
async def cmd(asheqqqq):
    await edit_or_reply(asheqqqq, AsheqSearch_cmd)
