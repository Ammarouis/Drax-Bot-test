from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import STATES, ADMIN_IDS
from database.db import (
    get_user, get_setting, update_setting, get_user_stats, 
    get_all_users, set_wallet, create_gift_code, update_wallet,
    get_total_commission
)
from utils.keyboards import (
    admin_menu_keyboard, main_menu_keyboard, cancel_keyboard,
    min_limits_keyboard, gift_settings_keyboard, payment_codes_keyboard
)
from handlers.common import is_admin
import secrets

async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        await update.message.reply_text("⚠️ غير مصرح لك")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🔐 لوحة التحكم\n\nاختر العملية:",
        reply_markup=admin_menu_keyboard()
    )
    return STATES["ADMIN_MENU"]

async def admin_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 رجوع":
        await update.message.reply_text("تم الخروج", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    
    elif text == "📊 تغيير عمولة الإحالة":
        current = await get_setting("referral_commission")
        await update.message.reply_text(
            f"📊 تغيير عمولة الإحالة\n\nالقيمة الحالية: {current}%\n\nأدخل القيمة الجديدة:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_REFERRAL_COMMISSION"]
    
    elif text == "📉 تعديل الحدود الدنيا":
        await update.message.reply_text(
            "📉 تعديل الحدود الدنيا\n\nاختر النوع:",
            reply_markup=min_limits_keyboard()
        )
        return STATES["ADMIN_MIN_LIMITS"]
    
    elif text == "💰 تغيير رصيد مستخدم":
        await update.message.reply_text(
            "💰 تغيير رصيد مستخدم\n\nأدخل معرف المستخدم (Telegram ID):",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_USER_BALANCE"]
    
    elif text == "📈 إحصائيات المستخدمين":
        stats = await get_user_stats()
        await update.message.reply_text(
            f"📈 إحصائيات المستخدمين\n\n"
            f"👥 إجمالي المستخدمين: {stats['total_users']}\n"
            f"💰 إجمالي الأرصدة: {stats['total_balance']:.2f} ل.س",
            reply_markup=admin_menu_keyboard()
        )
        return STATES["ADMIN_MENU"]
    
    elif text == "🎁 إعدادات الإهداء":
        await update.message.reply_text(
            "🎁 إعدادات الإهداء\n\nاختر الإعداد:",
            reply_markup=gift_settings_keyboard()
        )
        return STATES["ADMIN_GIFT_SETTINGS"]
    
    elif text == "🔄 تشغيل/إيقاف البوت":
        current = await get_setting("bot_active")
        new_status = not current
        await update_setting("bot_active", 1 if new_status else 0)
        status_text = "مفعّل ✅" if new_status else "متوقف ❌"
        await update.message.reply_text(
            f"🔄 تم تغيير حالة البوت\n\nالحالة الجديدة: {status_text}",
            reply_markup=admin_menu_keyboard()
        )
        return STATES["ADMIN_MENU"]
    
    elif text == "💎 إعدادات البونص":
        current = await get_setting("deposit_bonus")
        await update.message.reply_text(
            f"💎 إعدادات البونص\n\nالنسبة الحالية: {current}%\n\nأدخل النسبة الجديدة:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_BONUS_SETTINGS"]
    
    elif text == "📞 تغيير معرف الدعم":
        current = await get_setting("support_username")
        await update.message.reply_text(
            f"📞 تغيير معرف الدعم\n\nالمعرف الحالي: {current}\n\nأدخل المعرف الجديد:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_SUPPORT_USERNAME"]
    
    elif text == "✉️ رسالة لمستخدم":
        await update.message.reply_text(
            "✉️ إرسال رسالة لمستخدم\n\nأدخل معرف المستخدم:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_MESSAGE_USER"]
    
    elif text == "📢 رسالة جماعية":
        await update.message.reply_text(
            "📢 رسالة جماعية\n\nأدخل نص الرسالة:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_BROADCAST"]
    
    elif text == "💱 تغيير سعر صرف الدولار":
        current = await get_setting("exchange_rate_usd")
        await update.message.reply_text(
            f"💱 سعر صرف الدولار\n\nالسعر الحالي: {current} ل.س\n\nأدخل السعر الجديد:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_EXCHANGE_RATE"]
    
    elif text == "📝 تعديل أكواد الدفع":
        await update.message.reply_text(
            "📝 تعديل أكواد الدفع\n\nاختر الكود:",
            reply_markup=payment_codes_keyboard()
        )
        return STATES["ADMIN_PAYMENT_CODES"]
    
    elif text == "🎫 إنشاء كود هدية":
        await update.message.reply_text(
            "🎫 إنشاء كود هدية\n\nأدخل الكود (أو اكتب 'عشوائي' لتوليد كود):",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_CREATE_GIFT_CODE"]
    
    elif text == "💵 العمولات المجمعة":
        total = await get_total_commission()
        await update.message.reply_text(
            f"💵 العمولات المجمعة\n\n"
            f"💰 إجمالي العمولات: {total:.2f} ل.س",
            reply_markup=admin_menu_keyboard()
        )
        return STATES["ADMIN_MENU"]
    
    return STATES["ADMIN_MENU"]

async def admin_referral_commission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        value = float(text)
        if value < 0 or value > 100:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل قيمة صحيحة (0-100)", reply_markup=cancel_keyboard())
        return STATES["ADMIN_REFERRAL_COMMISSION"]
    
    await update_setting("referral_commission", value)
    await update.message.reply_text(
        f"✅ تم تحديث عمولة الإحالة إلى {value}%",
        reply_markup=admin_menu_keyboard()
    )
    return STATES["ADMIN_MENU"]

async def admin_min_limits(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 رجوع":
        await update.message.reply_text("لوحة التحكم", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    limit_mapping = {
        "الحد الأدنى سيريتل": "min_syriatel",
        "الحد الأدنى شام ليرة": "min_shamcash_syp",
        "الحد الأدنى شام دولار": "min_shamcash_usd",
        "الحد الأدنى للسحب": "min_withdraw"
    }
    
    if text in limit_mapping:
        context.user_data['limit_key'] = limit_mapping[text]
        current = await get_setting(limit_mapping[text])
        await update.message.reply_text(
            f"القيمة الحالية: {current}\n\nأدخل القيمة الجديدة:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_MIN_LIMIT_VALUE"]
    
    return STATES["ADMIN_MIN_LIMITS"]

async def admin_min_limit_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        value = float(text)
        if value < 0:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل قيمة صحيحة", reply_markup=cancel_keyboard())
        return STATES["ADMIN_MIN_LIMIT_VALUE"]
    
    key = context.user_data.get('limit_key')
    await update_setting(key, value)
    await update.message.reply_text(
        f"✅ تم التحديث بنجاح",
        reply_markup=admin_menu_keyboard()
    )
    return STATES["ADMIN_MENU"]

async def admin_user_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        user_id = int(text)
    except:
        await update.message.reply_text("⚠️ أدخل معرفاً صحيحاً", reply_markup=cancel_keyboard())
        return STATES["ADMIN_USER_BALANCE"]
    
    user = await get_user(user_id)
    if not user:
        await update.message.reply_text("⚠️ المستخدم غير موجود", reply_markup=cancel_keyboard())
        return STATES["ADMIN_USER_BALANCE"]
    
    context.user_data['target_user_id'] = user_id
    await update.message.reply_text(
        f"👤 المستخدم: {user_id}\n💰 الرصيد الحالي: {user['wallet_balance']:.2f} ل.س\n\nأدخل الرصيد الجديد:",
        reply_markup=cancel_keyboard()
    )
    return STATES["ADMIN_USER_BALANCE_AMOUNT"]

async def admin_user_balance_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        amount = float(text)
    except:
        await update.message.reply_text("⚠️ أدخل مبلغاً صحيحاً", reply_markup=cancel_keyboard())
        return STATES["ADMIN_USER_BALANCE_AMOUNT"]
    
    user_id = context.user_data.get('target_user_id')
    await set_wallet(user_id, amount)
    
    await update.message.reply_text(
        f"✅ تم تحديث رصيد المستخدم {user_id} إلى {amount:.2f} ل.س",
        reply_markup=admin_menu_keyboard()
    )
    return STATES["ADMIN_MENU"]

async def admin_gift_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 رجوع":
        await update.message.reply_text("لوحة التحكم", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    elif text == "تشغيل/إيقاف الإهداء":
        current = await get_setting("gifting_enabled")
        new_status = not current
        await update_setting("gifting_enabled", 1 if new_status else 0)
        status_text = "مفعّل ✅" if new_status else "متوقف ❌"
        await update.message.reply_text(
            f"تم تغيير حالة الإهداء: {status_text}",
            reply_markup=gift_settings_keyboard()
        )
        return STATES["ADMIN_GIFT_SETTINGS"]
    
    elif text == "الحد الأدنى للإهداء":
        current = await get_setting("min_gift")
        await update.message.reply_text(
            f"القيمة الحالية: {current}\n\nأدخل القيمة الجديدة:",
            reply_markup=cancel_keyboard()
        )
        context.user_data['gift_setting'] = 'min_gift'
        return STATES["ADMIN_GIFT_MIN"]
    
    elif text == "عمولة الإهداء":
        current = await get_setting("gift_commission")
        await update.message.reply_text(
            f"القيمة الحالية: {current}%\n\nأدخل القيمة الجديدة:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_GIFT_COMMISSION"]
    
    return STATES["ADMIN_GIFT_SETTINGS"]

async def admin_gift_min(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        value = float(text)
        if value < 0:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل قيمة صحيحة", reply_markup=cancel_keyboard())
        return STATES["ADMIN_GIFT_MIN"]
    
    await update_setting("min_gift", value)
    await update.message.reply_text("✅ تم التحديث", reply_markup=admin_menu_keyboard())
    return STATES["ADMIN_MENU"]

async def admin_gift_commission(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        value = float(text)
        if value < 0 or value > 100:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل قيمة صحيحة (0-100)", reply_markup=cancel_keyboard())
        return STATES["ADMIN_GIFT_COMMISSION"]
    
    await update_setting("gift_commission", value)
    await update.message.reply_text("✅ تم التحديث", reply_markup=admin_menu_keyboard())
    return STATES["ADMIN_MENU"]

async def admin_bonus_settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        value = float(text)
        if value < 0 or value > 100:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل قيمة صحيحة (0-100)", reply_markup=cancel_keyboard())
        return STATES["ADMIN_BONUS_SETTINGS"]
    
    await update_setting("deposit_bonus", value)
    await update.message.reply_text(
        f"✅ تم تحديث نسبة البونص إلى {value}%",
        reply_markup=admin_menu_keyboard()
    )
    return STATES["ADMIN_MENU"]

async def admin_support_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    await update_setting("support_username", text)
    await update.message.reply_text(
        f"✅ تم تحديث معرف الدعم إلى {text}",
        reply_markup=admin_menu_keyboard()
    )
    return STATES["ADMIN_MENU"]

async def admin_message_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        user_id = int(text)
    except:
        await update.message.reply_text("⚠️ أدخل معرفاً صحيحاً", reply_markup=cancel_keyboard())
        return STATES["ADMIN_MESSAGE_USER"]
    
    context.user_data['message_target'] = user_id
    await update.message.reply_text(
        "أدخل نص الرسالة:",
        reply_markup=cancel_keyboard()
    )
    return STATES["ADMIN_MESSAGE_USER_TEXT"]

async def admin_message_user_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    target = context.user_data.get('message_target')
    try:
        await context.bot.send_message(target, f"📬 رسالة من الإدارة:\n\n{text}")
        await update.message.reply_text("✅ تم إرسال الرسالة", reply_markup=admin_menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"❌ فشل الإرسال: {str(e)}", reply_markup=admin_menu_keyboard())
    
    return STATES["ADMIN_MENU"]

async def admin_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    users = await get_all_users()
    success = 0
    failed = 0
    
    for user in users:
        try:
            await context.bot.send_message(user['telegram_id'], f"📢 إعلان:\n\n{text}")
            success += 1
        except:
            failed += 1
    
    await update.message.reply_text(
        f"✅ تم الإرسال\n\n"
        f"✅ نجح: {success}\n"
        f"❌ فشل: {failed}",
        reply_markup=admin_menu_keyboard()
    )
    return STATES["ADMIN_MENU"]

async def admin_exchange_rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        value = float(text)
        if value <= 0:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل قيمة صحيحة", reply_markup=cancel_keyboard())
        return STATES["ADMIN_EXCHANGE_RATE"]
    
    await update_setting("exchange_rate_usd", value)
    await update.message.reply_text(
        f"✅ تم تحديث سعر الصرف إلى {value} ل.س/$",
        reply_markup=admin_menu_keyboard()
    )
    return STATES["ADMIN_MENU"]

async def admin_payment_codes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "🔙 رجوع":
        await update.message.reply_text("لوحة التحكم", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    elif text == "كود سيريتل":
        current = await get_setting("syriatel_code")
        context.user_data['code_type'] = 'syriatel_code'
        await update.message.reply_text(
            f"الكود الحالي: {current}\n\nأدخل الكود الجديد:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_PAYMENT_CODE_VALUE"]
    
    elif text == "كود شام كاش":
        current = await get_setting("shamcash_code")
        context.user_data['code_type'] = 'shamcash_code'
        await update.message.reply_text(
            f"الكود الحالي: {current}\n\nأدخل الكود الجديد:",
            reply_markup=cancel_keyboard()
        )
        return STATES["ADMIN_PAYMENT_CODE_VALUE"]
    
    return STATES["ADMIN_PAYMENT_CODES"]

async def admin_payment_code_value(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    code_type = context.user_data.get('code_type')
    await update_setting(code_type, text)
    await update.message.reply_text("✅ تم التحديث", reply_markup=admin_menu_keyboard())
    return STATES["ADMIN_MENU"]

async def admin_create_gift_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    if text == "عشوائي":
        code = secrets.token_hex(4).upper()
    else:
        code = text
    
    context.user_data['new_gift_code'] = code
    await update.message.reply_text(
        f"الكود: {code}\n\nأدخل عدد النقاط:",
        reply_markup=cancel_keyboard()
    )
    return STATES["ADMIN_GIFT_CODE_POINTS"]

async def admin_gift_code_points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        points = float(text)
        if points <= 0:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل قيمة صحيحة", reply_markup=cancel_keyboard())
        return STATES["ADMIN_GIFT_CODE_POINTS"]
    
    context.user_data['gift_code_points'] = points
    await update.message.reply_text(
        "أدخل عدد الاستخدامات المسموحة:",
        reply_markup=cancel_keyboard()
    )
    return STATES["ADMIN_GIFT_CODE_USES"]

async def admin_gift_code_uses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=admin_menu_keyboard())
        return STATES["ADMIN_MENU"]
    
    try:
        uses = int(text)
        if uses <= 0:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل رقماً صحيحاً", reply_markup=cancel_keyboard())
        return STATES["ADMIN_GIFT_CODE_USES"]
    
    code = context.user_data.get('new_gift_code')
    points = context.user_data.get('gift_code_points')
    
    try:
        await create_gift_code(code, points, uses)
        await update.message.reply_text(
            f"✅ تم إنشاء كود الهدية:\n\n"
            f"🎫 الكود: {code}\n"
            f"💰 النقاط: {points}\n"
            f"🔢 الاستخدامات: {uses}",
            reply_markup=admin_menu_keyboard()
        )
    except:
        await update.message.reply_text("❌ الكود موجود مسبقاً", reply_markup=admin_menu_keyboard())
    
    return STATES["ADMIN_MENU"]
