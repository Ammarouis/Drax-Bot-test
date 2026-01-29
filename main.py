import asyncio
import logging
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ConversationHandler, filters
)
from config import BOT_TOKEN, STATES
from database.db import init_db

from handlers.common import start_command, go_back, verify_subscription
from handlers.ichancy import (
    ichancy_menu, create_account_start, create_account_username, create_account_password,
    deposit_to_ichancy_start, deposit_to_ichancy_amount, withdraw_from_ichancy_start,
    withdraw_from_ichancy_amount, show_my_info, ichancy_back
)
from handlers.wallet import (
    wallet_menu, wallet_deposit_method, wallet_deposit_syriatel, wallet_deposit_shamcash_syp,
    wallet_deposit_shamcash_usd, wallet_deposit_amount, wallet_deposit_confirm,
    wallet_withdraw_method, wallet_withdraw_syriatel, wallet_withdraw_shamcash,
    wallet_withdraw_amount, wallet_withdraw_info, wallet_back
)
from handlers.referral import referral_menu
from handlers.gift import (
    gift_code_start, gift_code_enter, gift_points_start, gift_points_user, gift_points_amount
)
from handlers.admin import (
    admin_command, admin_menu_handler, admin_referral_commission, admin_min_limits,
    admin_min_limit_value, admin_user_balance, admin_user_balance_amount,
    admin_gift_settings, admin_gift_min, admin_gift_commission, admin_bonus_settings,
    admin_support_username, admin_message_user, admin_message_user_text, admin_broadcast,
    admin_exchange_rate, admin_payment_codes, admin_payment_code_value,
    admin_create_gift_code, admin_gift_code_points, admin_gift_code_uses
)
from handlers.callbacks import approval_callback, myinfo_callback
from handlers.misc import show_history, show_terms, show_bonus_info, show_support, cancel_pending

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN not found in environment variables")
        return
    
    asyncio.get_event_loop().run_until_complete(init_db())
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    ichancy_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎮 إدارة حساب iChancy$"), ichancy_menu)],
        states={
            STATES["ICHANCY_MENU"]: [
                MessageHandler(filters.Regex("^➕ إنشاء حساب$"), create_account_start),
                MessageHandler(filters.Regex("^💳 شحن الحساب$"), deposit_to_ichancy_start),
                MessageHandler(filters.Regex("^💸 السحب من الحساب$"), withdraw_from_ichancy_start),
                MessageHandler(filters.Regex("^ℹ️ عرض معلوماتي$"), show_my_info),
                MessageHandler(filters.Regex("^🔙 رجوع$"), ichancy_back),
            ],
            STATES["CREATE_USERNAME"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_account_username),
            ],
            STATES["CREATE_PASSWORD"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, create_account_password),
            ],
            STATES["DEPOSIT_AMOUNT"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, deposit_to_ichancy_amount),
            ],
            STATES["WITHDRAW_AMOUNT"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, withdraw_from_ichancy_amount),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            MessageHandler(filters.Regex("^🔙 رجوع$"), go_back),
        ],
        allow_reentry=True
    )
    
    wallet_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^💰 إدارة محفظة البوت$"), wallet_menu)],
        states={
            STATES["WALLET_MENU"]: [
                MessageHandler(filters.Regex("^📥 شحن المحفظة$"), wallet_deposit_method),
                MessageHandler(filters.Regex("^📤 سحب من المحفظة$"), wallet_withdraw_method),
                MessageHandler(filters.Regex("^🔙 رجوع$"), wallet_back),
            ],
            STATES["WALLET_DEPOSIT_METHOD"]: [
                MessageHandler(filters.Regex("^📱 سيريتل كاش$"), wallet_deposit_syriatel),
                MessageHandler(filters.Regex("^💵 شام كاش - ليرة سورية$"), wallet_deposit_shamcash_syp),
                MessageHandler(filters.Regex("^💲 شام كاش - دولار$"), wallet_deposit_shamcash_usd),
                MessageHandler(filters.Regex("^🔙 رجوع$"), wallet_menu),
            ],
            STATES["WALLET_DEPOSIT_AMOUNT"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_deposit_amount),
            ],
            STATES["WALLET_DEPOSIT_CONFIRM"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_deposit_confirm),
            ],
            STATES["WALLET_WITHDRAW_METHOD"]: [
                MessageHandler(filters.Regex("^📱 سحب سيريتل كاش$"), wallet_withdraw_syriatel),
                MessageHandler(filters.Regex("^💵 سحب شام كاش$"), wallet_withdraw_shamcash),
                MessageHandler(filters.Regex("^🔙 رجوع$"), wallet_menu),
            ],
            STATES["WALLET_WITHDRAW_AMOUNT"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_withdraw_amount),
            ],
            STATES["WALLET_WITHDRAW_INFO"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, wallet_withdraw_info),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            MessageHandler(filters.Regex("^🔙 رجوع$"), go_back),
        ],
        allow_reentry=True
    )
    
    gift_code_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎁 تفعيل كود هدية$"), gift_code_start)],
        states={
            STATES["GIFT_CODE"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gift_code_enter),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            MessageHandler(filters.Regex("^❌ إلغاء$"), go_back),
        ],
        allow_reentry=True
    )
    
    gift_points_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🎈 إهداء نقاط$"), gift_points_start)],
        states={
            STATES["GIFT_POINTS_USER"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gift_points_user),
            ],
            STATES["GIFT_POINTS_AMOUNT"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, gift_points_amount),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            MessageHandler(filters.Regex("^❌ إلغاء$"), go_back),
        ],
        allow_reentry=True
    )
    
    admin_handler = ConversationHandler(
        entry_points=[CommandHandler("admin", admin_command)],
        states={
            STATES["ADMIN_MENU"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_menu_handler),
            ],
            STATES["ADMIN_REFERRAL_COMMISSION"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_referral_commission),
            ],
            STATES["ADMIN_MIN_LIMITS"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_min_limits),
            ],
            STATES["ADMIN_MIN_LIMIT_VALUE"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_min_limit_value),
            ],
            STATES["ADMIN_USER_BALANCE"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_user_balance),
            ],
            STATES["ADMIN_USER_BALANCE_AMOUNT"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_user_balance_amount),
            ],
            STATES["ADMIN_GIFT_SETTINGS"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_gift_settings),
            ],
            STATES["ADMIN_GIFT_MIN"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_gift_min),
            ],
            STATES["ADMIN_GIFT_COMMISSION"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_gift_commission),
            ],
            STATES["ADMIN_BONUS_SETTINGS"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_bonus_settings),
            ],
            STATES["ADMIN_SUPPORT_USERNAME"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_support_username),
            ],
            STATES["ADMIN_MESSAGE_USER"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_message_user),
            ],
            STATES["ADMIN_MESSAGE_USER_TEXT"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_message_user_text),
            ],
            STATES["ADMIN_BROADCAST"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_broadcast),
            ],
            STATES["ADMIN_EXCHANGE_RATE"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_exchange_rate),
            ],
            STATES["ADMIN_PAYMENT_CODES"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_payment_codes),
            ],
            STATES["ADMIN_PAYMENT_CODE_VALUE"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_payment_code_value),
            ],
            STATES["ADMIN_CREATE_GIFT_CODE"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_create_gift_code),
            ],
            STATES["ADMIN_GIFT_CODE_POINTS"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_gift_code_points),
            ],
            STATES["ADMIN_GIFT_CODE_USES"]: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, admin_gift_code_uses),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            MessageHandler(filters.Regex("^🔙 رجوع$"), go_back),
        ],
        allow_reentry=True
    )
    
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(MessageHandler(filters.Regex("^✅ تحقق من الاشتراك$"), verify_subscription))
    application.add_handler(ichancy_handler)
    application.add_handler(wallet_handler)
    application.add_handler(gift_code_handler)
    application.add_handler(gift_points_handler)
    application.add_handler(admin_handler)
    
    application.add_handler(MessageHandler(filters.Regex("^👥 نظام الإحالة$"), referral_menu))
    application.add_handler(MessageHandler(filters.Regex("^📞 التواصل والدعم$"), show_support))
    application.add_handler(MessageHandler(filters.Regex("^⏸️ إيقاف العمليات المعلقة$"), cancel_pending))
    application.add_handler(MessageHandler(filters.Regex("^📜 السجل$"), show_history))
    application.add_handler(MessageHandler(filters.Regex("^📋 الشروط والأحكام$"), show_terms))
    application.add_handler(MessageHandler(filters.Regex("^💎 معلومات البونص الحالي$"), show_bonus_info))
    
    application.add_handler(CallbackQueryHandler(approval_callback, pattern="^(approve|reject)_"))
    application.add_handler(CallbackQueryHandler(myinfo_callback, pattern="^myinfo_"))
    
    logger.info("Bot started successfully!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
