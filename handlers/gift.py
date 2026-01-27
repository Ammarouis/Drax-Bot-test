from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import STATES
from database.db import get_user, use_gift_code, get_setting, update_wallet, add_transaction
from utils.keyboards import main_menu_keyboard, cancel_keyboard
from handlers.common import check_subscription, check_bot_active

async def gift_code_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        await update.message.reply_text("⚠️ يجب الاشتراك في القناة أولاً")
        return ConversationHandler.END
    
    if not await check_bot_active(update, context):
        await update.message.reply_text("⚠️ البوت متوقف حالياً")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🎁 تفعيل كود هدية\n\nأدخل الكود:",
        reply_markup=cancel_keyboard()
    )
    return STATES["GIFT_CODE"]

async def gift_code_enter(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    
    success, result = await use_gift_code(text, update.effective_user.id)
    
    if success:
        await add_transaction(
            update.effective_user.id,
            "gift_code",
            result,
            "completed",
            f"كود هدية: {text}"
        )
        await update.message.reply_text(
            f"✅ تم تفعيل الكود بنجاح!\n\n"
            f"💰 تمت إضافة {result:.2f} ل.س إلى محفظتك",
            reply_markup=main_menu_keyboard()
        )
    else:
        error_messages = {
            "already_used": "⚠️ لقد استخدمت هذا الكود من قبل",
            "not_found": "⚠️ الكود غير موجود",
            "exhausted": "⚠️ تم استنفاد عدد استخدامات هذا الكود"
        }
        await update.message.reply_text(
            error_messages.get(result, "⚠️ خطأ في تفعيل الكود"),
            reply_markup=main_menu_keyboard()
        )
    
    return ConversationHandler.END

async def gift_points_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        await update.message.reply_text("⚠️ يجب الاشتراك في القناة أولاً")
        return ConversationHandler.END
    
    if not await check_bot_active(update, context):
        await update.message.reply_text("⚠️ البوت متوقف حالياً")
        return ConversationHandler.END
    
    gifting_enabled = await get_setting("gifting_enabled")
    if not gifting_enabled:
        await update.message.reply_text(
            "⚠️ خاصية الإهداء متوقفة حالياً",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END
    
    user = await get_user(update.effective_user.id)
    min_gift = await get_setting("min_gift")
    commission = await get_setting("gift_commission")
    
    await update.message.reply_text(
        f"🎈 إهداء نقاط\n\n"
        f"💰 رصيدك: {user['wallet_balance']:.2f} ل.س\n"
        f"📉 الحد الأدنى: {min_gift} ل.س\n"
        f"💸 العمولة: {commission}%\n\n"
        f"أدخل معرف المستخدم (Telegram ID):",
        reply_markup=cancel_keyboard()
    )
    return STATES["GIFT_POINTS_USER"]

async def gift_points_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    
    try:
        target_id = int(text)
    except:
        await update.message.reply_text(
            "⚠️ أدخل معرفاً صحيحاً (أرقام فقط)",
            reply_markup=cancel_keyboard()
        )
        return STATES["GIFT_POINTS_USER"]
    
    if target_id == update.effective_user.id:
        await update.message.reply_text(
            "⚠️ لا يمكنك إهداء نقاط لنفسك",
            reply_markup=cancel_keyboard()
        )
        return STATES["GIFT_POINTS_USER"]
    
    target_user = await get_user(target_id)
    if not target_user:
        await update.message.reply_text(
            "⚠️ المستخدم غير موجود في البوت",
            reply_markup=cancel_keyboard()
        )
        return STATES["GIFT_POINTS_USER"]
    
    context.user_data['gift_target_id'] = target_id
    
    await update.message.reply_text(
        f"✅ تم العثور على المستخدم\n\nأدخل المبلغ المراد إهداؤه:",
        reply_markup=cancel_keyboard()
    )
    return STATES["GIFT_POINTS_AMOUNT"]

async def gift_points_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=main_menu_keyboard())
        return ConversationHandler.END
    
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except:
        await update.message.reply_text(
            "⚠️ أدخل مبلغاً صحيحاً",
            reply_markup=cancel_keyboard()
        )
        return STATES["GIFT_POINTS_AMOUNT"]
    
    user = await get_user(update.effective_user.id)
    min_gift = await get_setting("min_gift")
    commission = await get_setting("gift_commission")
    
    if amount < min_gift:
        await update.message.reply_text(
            f"⚠️ المبلغ أقل من الحد الأدنى: {min_gift} ل.س",
            reply_markup=cancel_keyboard()
        )
        return STATES["GIFT_POINTS_AMOUNT"]
    
    commission_amount = amount * (commission / 100)
    total_deduct = amount + commission_amount
    
    if total_deduct > user['wallet_balance']:
        await update.message.reply_text(
            f"⚠️ رصيدك غير كافٍ!\n"
            f"المطلوب: {total_deduct:.2f} ل.س (شامل العمولة)\n"
            f"رصيدك: {user['wallet_balance']:.2f} ل.س",
            reply_markup=cancel_keyboard()
        )
        return STATES["GIFT_POINTS_AMOUNT"]
    
    target_id = context.user_data.get('gift_target_id')
    
    await update_wallet(update.effective_user.id, -total_deduct)
    await update_wallet(target_id, amount)
    
    await add_transaction(
        update.effective_user.id,
        "gift_sent",
        -total_deduct,
        "completed",
        f"إهداء إلى {target_id}"
    )
    await add_transaction(
        target_id,
        "gift_received",
        amount,
        "completed",
        f"هدية من {update.effective_user.id}"
    )
    
    try:
        await context.bot.send_message(
            target_id,
            f"🎁 لقد تلقيت هدية!\n\n"
            f"💰 المبلغ: {amount:.2f} ل.س\n"
            f"👤 من: {update.effective_user.id}"
        )
    except:
        pass
    
    await update.message.reply_text(
        f"✅ تم إرسال الهدية بنجاح!\n\n"
        f"👤 إلى: {target_id}\n"
        f"💰 المبلغ: {amount:.2f} ل.س\n"
        f"💸 العمولة: {commission_amount:.2f} ل.س",
        reply_markup=main_menu_keyboard()
    )
    
    return ConversationHandler.END
