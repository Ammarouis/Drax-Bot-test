from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import ADMIN_IDS, REQUIRED_CHANNEL
from database.db import get_user, create_user, get_setting
from utils.keyboards import main_menu_keyboard

def subscription_keyboard():
    return ReplyKeyboardMarkup(
        [["✅ تحقق من الاشتراك"]],
        resize_keyboard=True
    )

async def check_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except:
        return False

async def check_bot_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user_id = update.effective_user.id
    if user_id in ADMIN_IDS:
        return True
    return await get_setting("bot_active")

async def require_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not await check_subscription(update, context):
        await update.message.reply_text(
            f"⚠️ يجب عليك الاشتراك في قناتنا أولاً للاستفادة من خدمات البوت:\n\n"
            f"📢 {REQUIRED_CHANNEL}\n\n"
            f"بعد الاشتراك، اضغط على الزر أدناه للتحقق:",
            reply_markup=subscription_keyboard()
        )
        return False
    return True

async def require_bot_active(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    if not await check_bot_active(update, context):
        await update.message.reply_text(
            "🔴 البوت غير متوفر حالياً\n\n"
            "يرجى المحاولة لاحقاً أو التواصل مع الدعم الفني.",
            reply_markup=main_menu_keyboard()
        )
        return False
    return True

async def ensure_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    existing = await get_user(user.id)
    if not existing:
        referrer_id = context.args[0] if context.args else None
        if referrer_id:
            try:
                referrer_id = int(referrer_id)
            except:
                referrer_id = None
        await create_user(user.id, user.username, referrer_id)
    return await get_user(user.id)

async def verify_subscription(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if await check_subscription(update, context):
        user = await ensure_user(update, context)
        
        if not await check_bot_active(update, context):
            await update.message.reply_text(
                "🔴 البوت غير متوفر حالياً\n\n"
                "يرجى المحاولة لاحقاً أو التواصل مع الدعم الفني.",
                reply_markup=main_menu_keyboard()
            )
            return ConversationHandler.END
        
        await update.message.reply_text(
            f"✅ تم التحقق من الاشتراك بنجاح!\n\n"
            f"🎰 مرحباً بك في بوت 𝔻𝕣𝕒𝕩 𝕥𝕙𝕖 𝔻𝕖𝕤𝕥𝕣𝕠𝕪𝕖𝕣\n\n"
            f"💰 رصيد محفظتك: {user['wallet_balance']:.2f} ل.س\n\n"
            f"اختر من القائمة أدناه:",
            reply_markup=main_menu_keyboard()
        )
    else:
        await update.message.reply_text(
            f"❌ لم يتم التحقق من الاشتراك!\n\n"
            f"يرجى الاشتراك في القناة أولاً:\n"
            f"📢 {REQUIRED_CHANNEL}\n\n"
            f"ثم اضغط على الزر مجدداً:",
            reply_markup=subscription_keyboard()
        )
    return ConversationHandler.END

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_subscription(update, context):
        await update.message.reply_text(
            f"👋 أهلاً بك في بوت 𝔻𝕣𝕒𝕩 𝕥𝕙𝕖 𝔻𝕖𝕤𝕥𝕣𝕠𝕪𝕖𝕣\n\n"
            f"⚠️ للبدء باستخدام البوت، يجب الاشتراك في قناتنا أولاً:\n\n"
            f"📢 {REQUIRED_CHANNEL}\n\n"
            f"بعد الاشتراك، اضغط على الزر أدناه للتحقق:",
            reply_markup=subscription_keyboard()
        )
        return ConversationHandler.END
    
    user = await ensure_user(update, context)
    
    if not await check_bot_active(update, context):
        await update.message.reply_text(
            "🔴 البوت غير متوفر حالياً\n\n"
            "يرجى المحاولة لاحقاً أو التواصل مع الدعم الفني.",
            reply_markup=main_menu_keyboard()
        )
        return ConversationHandler.END
    
    await update.message.reply_text(
        f"🎰 مرحباً بك في بوت 𝔻𝕣𝕒𝕩 𝕥𝕙𝕖 𝔻𝕖𝕤𝕥𝕣𝕠𝕪𝕖𝕣\n\n"
        f"💰 رصيد محفظتك: {user['wallet_balance']:.2f} ل.س\n\n"
        f"اختر من القائمة أدناه:",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

async def go_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    balance = user['wallet_balance'] if user else 0
    
    await update.message.reply_text(
        f"🏠 القائمة الرئيسية\n\n💰 رصيدك: {balance:.2f} ل.س",
        reply_markup=main_menu_keyboard()
    )
    return ConversationHandler.END

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS
