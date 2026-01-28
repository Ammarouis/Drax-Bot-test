from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from database.db import get_user, get_transactions, get_setting, cancel_pending_requests
from utils.keyboards import main_menu_keyboard
from handlers.common import require_subscription, require_bot_active

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return ConversationHandler.END
    
    if not await require_bot_active(update, context):
        return ConversationHandler.END
    
    transactions = await get_transactions(update.effective_user.id, 5)
    
    if not transactions:
        await update.message.reply_text(
            "📜 السجل فارغ\n\nلا توجد عمليات سابقة",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END
    
    history_text = "📜 آخر 5 عمليات:\n\n"
    
    type_names = {
        'wallet_deposit': 'شحن محفظة',
        'wallet_withdraw': 'سحب من المحفظة',
        'ichancy_deposit': 'شحن iChancy',
        'ichancy_withdraw': 'سحب من iChancy',
        'gift_code': 'كود هدية',
        'gift_sent': 'إهداء نقاط',
        'gift_received': 'استلام هدية',
        'referral_commission': 'عمولة إحالة'
    }
    
    status_names = {
        'pending': '⏳ قيد الانتظار',
        'approved': '✅ تمت الموافقة',
        'completed': '✅ مكتمل',
        'rejected': '❌ مرفوض',
        'cancelled': '🚫 ملغي'
    }
    
    for i, trans in enumerate(transactions, 1):
        trans_type = type_names.get(trans['type'], trans['type'])
        status = status_names.get(trans['status'], trans['status'])
        amount = trans['amount']
        date = trans['created_at'][:10] if trans['created_at'] else 'غير محدد'
        
        history_text += f"{i}. {trans_type}\n"
        history_text += f"   💰 {amount:.2f} ل.س\n"
        history_text += f"   📊 {status}\n"
        history_text += f"   📅 {date}\n\n"
    
    await update.message.reply_text(history_text, reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def show_terms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    terms_text = """📋 الشروط والأحكام

1. يجب الاشتراك في القناة الرسمية لاستخدام البوت
2. جميع عمليات الشحن والسحب تخضع للمراجعة
3. العمولات والحدود الدنيا قابلة للتغيير
4. الإدارة غير مسؤولة عن أي خسائر في iChancy
5. يحق للإدارة إيقاف أي حساب مخالف
6. بيانات المستخدمين محمية وسرية
7. استخدام البوت يعني الموافقة على هذه الشروط

للاستفسارات تواصل مع الدعم"""
    
    await update.message.reply_text(terms_text, reply_markup=main_menu_keyboard())
    return ConversationHandler.END

async def show_bonus_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return ConversationHandler.END
    
    if not await require_bot_active(update, context):
        return ConversationHandler.END
    
    bonus = await get_setting("deposit_bonus")
    
    if bonus > 0:
        await update.message.reply_text(
            f"💎 معلومات البونص الحالي\n\n"
            f"🎁 نسبة البونص: {bonus}%\n\n"
            f"يُضاف البونص تلقائياً على كل عملية شحن للمحفظة",
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            "💎 معلومات البونص\n\n"
            "⚠️ لا يوجد بونص حالياً\n\n"
            "تابعنا للاطلاع على العروض القادمة",
            reply_markup=main_menu_keyboard()
        )
    
    return ConversationHandler.END

async def show_support(update: Update, context: ContextTypes.DEFAULT_TYPE):
    support_username = await get_setting("support_username")
    
    await update.message.reply_text(
        f"📞 التواصل والدعم\n\n"
        f"للاستفسارات والمساعدة تواصل مع:\n{support_username}",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def cancel_pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return ConversationHandler.END
    
    if not await require_bot_active(update, context):
        return ConversationHandler.END
    
    await cancel_pending_requests(update.effective_user.id)
    
    await update.message.reply_text(
        "⏸️ تم إيقاف جميع العمليات المعلقة",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END
