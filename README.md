# 𝔻𝕣𝕒𝕩 𝕥𝕙𝕖 𝔻𝕖𝕤𝕥𝕣𝕠𝕪𝕖𝕣 Bot 🦾

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Telegram](https://img.shields.io/badge/Telegram-Bot-26A5E4?style=for-the-badge&logo=telegram)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)

**بوت تيليجرام متكامل لإدارة حسابات iChancy مع نظام محفظة ذكي**

</div>

---

## ⚡ نظرة عامة

DRAX هو بوت تيليجرام قوي ومتطور تم تصميمه وبرمجته لتوفير تجربة سلسة في إدارة حسابات الألعاب والمحافظ الإلكترونية. يتميز بواجهة عربية بالكامل وأداء عالي.

## 🚀 المميزات

- 🎮 **تكامل iChancy** - إنشاء وإدارة حسابات iChancy
- 💰 **نظام المحفظة** - شحن وسحب عبر Syriatel Cash و ShamCash
- 👥 **نظام الإحالة** - عمولات تلقائية للمحيلين
- 🎁 **أكواد الهدايا** - نظام هدايا متكامل
- 🛡️ **لوحة تحكم** - إدارة كاملة للمدراء
- 📊 **تتبع العمليات** - سجل شامل لجميع المعاملات

## 🛠️ التقنيات المستخدمة

```
├── Python 3.11+
├── python-telegram-bot (Async)
├── SQLite + aiosqlite
├── httpx (Async HTTP)
└── Clean Architecture
```

## 📦 التثبيت

```bash
# استنساخ المشروع
git clone https://github.com/YOUR_USERNAME/drax-bot.git
cd drax-bot

# تثبيت المتطلبات
pip install -r requirements.txt

# إعداد المتغيرات البيئية
export BOT_TOKEN="your_bot_token"

# تشغيل البوت
python main.py
```

## 📁 هيكل المشروع

```
drax-bot/
├── main.py                 # نقطة البداية
├── config.py               # الإعدادات
├── requirements.txt        # المتطلبات
├── database/
│   └── db.py              # عمليات قاعدة البيانات
├── handlers/
│   ├── common.py          # المعالجات المشتركة
│   ├── ichancy.py         # معالجات iChancy
│   ├── wallet.py          # معالجات المحفظة
│   ├── referral.py        # نظام الإحالة
│   ├── gift.py            # نظام الهدايا
│   ├── admin.py           # لوحة الإدارة
│   ├── callbacks.py       # Inline callbacks
│   └── misc.py            # معالجات متنوعة
└── utils/
    ├── ichancy_api.py     # تكامل iChancy API
    └── keyboards.py       # لوحات المفاتيح
```

## 👨‍💻 المطور

<div align="center">

**تم التصميم والبرمجة بواسطة**

[![Developer](https://img.shields.io/badge/Developer-Ammar_Satouf-purple?style=for-the-badge)](https://github.com/Ammar-Satouf)

</div>

---

<div align="center">

⭐ **إذا أعجبك المشروع، لا تنسَ إضافة نجمة!** ⭐

</div>
