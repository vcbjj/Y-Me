# سورس يمنثون - تحديث السورس
from .. import zedub
from ..core.managers import edit_or_reply
import asyncio
import os
import sys
import subprocess
import git  # تحتاج تثبيت مكتبة GitPython: pip install GitPython

# ----------------------------------------
# دوال مساعدة لتعويض الدوال المفقودة
# ----------------------------------------

# دالة تنفيذ أوامر الباش
async def bash(cmd: str):
    """تشغيل أمر باش بشكل غير متزامن"""
    process = await asyncio.create_subprocess_shell(cmd)
    await process.communicate()


# دالة التحقق من التحديثات
def check_update():
    """ترجع True إذا هناك تحديثات متاحة"""
    try:
        repo = git.Repo(os.getcwd())
        origin = repo.remotes.origin
        origin.fetch()
        local = repo.head.commit
        remote = repo.remotes.origin.refs[repo.active_branch.name].commit
        return local.hexsha != remote.hexsha
    except Exception:
        return False


# دالة الحصول على الريموت URL
def get_remote_url():
    """ترجع رابط الريبو الحالي"""
    try:
        repo = git.Repo(os.getcwd())
        return next(repo.remote().urls)
    except Exception:
        return ""


# ----------------------------------------
# كود التحديث نفسه
# ----------------------------------------

@zedub.zed_cmd(pattern=r"تحديث(?:\s+(.*)|$)")
async def update_yamenthon(event):
    xx = await edit_or_reply(event, "**⌔∮ جار البحث عن تحديثات لسورس يـــمنثون**")
    cmd = event.pattern_match.group(1).strip() if event.pattern_match.group(1) else ""

    # التحديث السريع أو الخفيف
    if cmd and ("سريع" in cmd or "خفيف" in cmd):
        await bash("git pull -f")
        await xx.edit("**⌔∮ جار التحديث الخفيف يرجى الأنتظار**")
        os.execl(sys.executable, sys.executable, "-m", "yamenthon")
        return

    # التحقق من التحديثات
    await xx.edit("**⌔∮ جاري التحقق من التحديثات...**")
    await asyncio.sleep(1)

    remote_url = get_remote_url()
    if remote_url.endswith(".git"):
        remote_url = remote_url[:-4]

    has_update = check_update()
    if not has_update:
        return await xx.edit(
            f'<strong>سورس يـــمنثون مُحدث بأخر أصدار</strong>',
            parse_mode="html",
            link_preview=False,
        )

    # رسائل التقدم أثناء التحديث
    steps = [
     (10, "**⌔∮ جاري تحميل التحديثات...🌐**\n\n%10 ▬▭▭▭▭▭▭▭▭▭"),
     (20, "**⌔∮ جاري تحميل التحديثات...🌐**\n\n%20 ▬▬▭▭▭▭▭▭▭▭"),
     (30, "**⌔∮ جاري تحميل التحديثات...🌐**\n\n%30 ▬▬▬▭▭▭▭▭▭▭"),
     (40, "**⌔∮ جاري تحميل التحديثات...🌐**\n\n%40 ▬▬▬▬▭▭▭▭▭▭"),
     (50, "**⌔∮ جاري تطبيق التحديثات...🌐**\n\n%50 ▬▬▬▬▬▭▭▭▭▭"),
     (60, "**⌔∮ جاري تطبيق التحديثات...🌐**\n\n%60 ▬▬▬▬▬▬▭▭▭▭"),
     (70, "**⌔∮ جاري تثبيت المتطلبات...🌐**\n\n%70 ▬▬▬▬▬▬▬▭▭▭"),
     (80, "**⌔∮ جاري تثبيت المتطلبات...🌐**\n\n%80 ▬▬▬▬▬▬▬▬▭▭"),
     (90, "**⌔∮ جاري الانتهاء من التحديث...🌐**\n\n%90 ▬▬▬▬▬▬▬▬▬▭"),
     (100, "**⌔∮ تم التحديث بنجاح! جاري إعادة التشغيل...🔄**\n\n%100 ▬▬▬▬▬▬▬▬▬▬💯")
]

    for percent, message in steps:
        await xx.edit(message)
        await asyncio.sleep(1)

    await perform_update(xx)


async def perform_update(xx):
    try:
        # المحاولة الأولى: تحديث عادي
        await bash("git pull")
    except Exception:
        # لو فشل التحديث العادي: تحديث إجباري
        await xx.edit("**⚠️ التحديث العادي فشل بسبب تعديلات محلية.**\n**⌔∮ جاري فرض التحديث...**\n**مميزه التحديث الإجباري حصرية بسورس يمنثون عكس جميع السورسات 🇾🇪**")
        await bash("git fetch --all && git reset --hard origin/HEAD")

    # تثبيت المتطلبات بعد التحديث
    await bash(f"{sys.executable} -m pip install -r requirements.txt")
    await xx.edit("✅ <strong>✅ تم تجهيز السورس للعمل انتظر قليلا حتى يصلك اشعار في مجموعة السجل تفيد بأن السورس بدا في العمل.</strong>", parse_mode="html")

    # إعادة تشغيل السورس
    os.execl(sys.executable, sys.executable, "-m", "yamenthon")
