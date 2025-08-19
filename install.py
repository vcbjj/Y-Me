import os
import subprocess

# المتغيرات المطلوبة
variables = {
    "ALIVE_NAME": "اكتب اسمك",
    "API_HASH": "ادخل API_HASH",
    "APP_ID": "ادخل APP_ID",
    "STRING_SESSION": "ادخل كود السيشن",
    "TG_BOT_TOKEN": "ادخل توكن البوت",
    "TIME_ZONE": "Asia/Amman",  # ثابت
    "DATABASE_URL": "ادخل رابط قاعدة البيانات"
}

def main():
    print("🔹 أهلاً بك في مثبت سورس يمنثون 🔹\n")

    env_lines = []
    for key, msg in variables.items():
        if key == "TIME_ZONE":
            value = msg  # ثابت
            print(f"{key} = {value} (ثابت)")
        else:
            value = input(f"{msg}: ").strip()
        env_lines.append(f"{key}={value}")

    # حفظ ملف .env
    with open(".env", "w", encoding="utf-8") as f:
        f.write("\n".join(env_lines))

    print("\n✅ تم إنشاء ملف .env بنجاح")

    # تثبيت المكتبات
    print("\n📦 يتم الآن تثبيت المكتبات من requirements.txt ...\n")
    subprocess.run(["pip3", "install", "-r", "requirements.txt"])

    # تشغيل السورس
    print("\n🚀 يتم الآن تشغيل سورس يمنثون ...\n")
    subprocess.run(["python3", "-m", "yamenthon"])

if __name__ == "__main__":
    main()
