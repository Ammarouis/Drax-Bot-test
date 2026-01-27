from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_user, get_referral_stats, get_setting
from utils.keyboards import main_menu_keyboard
from handlers.common import check_subscription, check_bot_active

async def referral_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        await update.message.reply_text("⚠️ يجب الاشتراك في القناة أولاً")
        return ConversationHandler.END
    
    if not await check_bot_active(update, context):
        await update.message.reply_text("⚠️ البوت متوقف حالياً")
        return ConversationHandler.END
    
    user_id = update.effective_user.id
    bot_username = (await context.bot.get_me()).username
    referral_link = f"https://t.me/{bot_username}?start={user_id}"
    
    referral_count = await get_referral_stats(user_id)
    commission = await get_setting("referral_commission")
    
    await update.message.reply_text(
        f"👥 نظام الإحالة\n\n"
        f"🔗 رابط الإحالة الخاص بك:\n{referral_link}\n\n"
        f"📊 إحصائياتك:\n"
        f"👤 عدد المدعوين: {referral_count}\n"
        f"💰 نسبة العمولة: {commission}%\n\n"
        f"ℹ️ ستحصل على {commission}% من كل عملية شحن محفظة يقوم بها المدعوين",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END
