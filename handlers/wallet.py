from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import STATES, PENDING_CHANNEL_ID
from database.db import get_user, get_setting, create_pending_request, add_transaction, update_wallet, update_pending_request
from utils.keyboards import wallet_menu_keyboard, deposit_method_keyboard, withdraw_method_keyboard, cancel_keyboard, main_menu_keyboard, approval_inline_keyboard, confirm_keyboard
from handlers.common import require_subscription, require_bot_active

async def wallet_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return ConversationHandler.END
    
    if not await require_bot_active(update, context):
        return ConversationHandler.END
    
    user = await get_user(update.effective_user.id)
    balance = user['wallet_balance'] if user else 0
    
    await update.message.reply_text(
        f"💰 إدارة محفظة البوت\n\n"
        f"💵 رصيدك الحالي: {balance:.2f} ل.س\n\n"
        f"اختر العملية:",
        reply_markup=wallet_menu_keyboard()
    )
    return STATES["WALLET_MENU"]

async def wallet_deposit_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📥 شحن المحفظة\n\nاختر طريقة الدفع:",
        reply_markup=deposit_method_keyboard()
    )
    return STATES["WALLET_DEPOSIT_METHOD"]

async def wallet_deposit_syriatel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    syriatel_code = await get_setting("syriatel_code")
    min_amount = await get_setting("min_syriatel")
    
    context.user_data['deposit_method'] = 'syriatel'
    context.user_data['deposit_currency'] = 'SYP'
    
    await update.message.reply_text(
        f"📱 شحن عبر سيريتل كاش\n\n"
        f"كود التحويل: <code>{syriatel_code}</code>\n"
        f"الحد الأدنى: {min_amount} ل.س\n\n"
        f"أدخل المبلغ المحول:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    return STATES["WALLET_DEPOSIT_AMOUNT"]

async def wallet_deposit_shamcash_syp(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shamcash_code = await get_setting("shamcash_code")
    min_amount = await get_setting("min_shamcash_syp")
    
    context.user_data['deposit_method'] = 'shamcash_syp'
    context.user_data['deposit_currency'] = 'SYP'
    
    await update.message.reply_text(
        f"💵 شحن عبر شام كاش - ليرة سورية\n\n"
        f"كود التحويل: <code>{shamcash_code}</code>\n"
        f"الحد الأدنى: {min_amount} ل.س\n\n"
        f"أدخل المبلغ المحول بالليرة:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    return STATES["WALLET_DEPOSIT_AMOUNT"]

async def wallet_deposit_shamcash_usd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    shamcash_code = await get_setting("shamcash_code")
    min_amount = await get_setting("min_shamcash_usd")
    exchange_rate = await get_setting("exchange_rate_usd")
    
    context.user_data['deposit_method'] = 'shamcash_usd'
    context.user_data['deposit_currency'] = 'USD'
    context.user_data['exchange_rate'] = exchange_rate
    
    await update.message.reply_text(
        f"💲 شحن عبر شام كاش - دولار\n\n"
        f"كود التحويل: <code>{shamcash_code}</code>\n"
        f"الحد الأدنى: {min_amount} $\n"
        f"سعر الصرف: {exchange_rate} ل.س/$\n\n"
        f"أدخل المبلغ المحول بالدولار:",
        reply_markup=cancel_keyboard(),
        parse_mode="HTML"
    )
    return STATES["WALLET_DEPOSIT_AMOUNT"]

async def wallet_deposit_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=wallet_menu_keyboard())
        return STATES["WALLET_MENU"]
    
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل مبلغاً صحيحاً", reply_markup=cancel_keyboard())
        return STATES["WALLET_DEPOSIT_AMOUNT"]
    
    method = context.user_data.get('deposit_method')
    currency = context.user_data.get('deposit_currency')
    
    if method == 'syriatel':
        min_amount = await get_setting("min_syriatel")
    elif method == 'shamcash_syp':
        min_amount = await get_setting("min_shamcash_syp")
    else:
        min_amount = await get_setting("min_shamcash_usd")
    
    if amount < min_amount:
        await update.message.reply_text(
            f"⚠️ المبلغ أقل من الحد الأدنى: {min_amount}",
            reply_markup=cancel_keyboard()
        )
        return STATES["WALLET_DEPOSIT_AMOUNT"]
    
    context.user_data['deposit_amount'] = amount
    
    if currency == 'USD':
        exchange_rate = context.user_data.get('exchange_rate', 15000)
        syp_amount = amount * exchange_rate
        bonus = await get_setting("deposit_bonus")
        bonus_amount = syp_amount * (bonus / 100)
        total = syp_amount + bonus_amount
        
        confirm_text = (
            f"💰 تأكيد الشحن:\n\n"
            f"المبلغ: ${amount}\n"
            f"سعر الصرف: {exchange_rate} ل.س/$\n"
            f"المبلغ بالليرة: {syp_amount:.2f} ل.س\n"
        )
        if bonus > 0:
            confirm_text += f"البونص ({bonus}%): {bonus_amount:.2f} ل.س\n"
        confirm_text += f"الإجمالي: {total:.2f} ل.س\n\nهل تريد التأكيد؟"
        context.user_data['final_amount'] = total
    else:
        bonus = await get_setting("deposit_bonus")
        bonus_amount = amount * (bonus / 100)
        total = amount + bonus_amount
        
        confirm_text = f"💰 تأكيد الشحن:\n\nالمبلغ: {amount:.2f} ل.س\n"
        if bonus > 0:
            confirm_text += f"البونص ({bonus}%): {bonus_amount:.2f} ل.س\n"
        confirm_text += f"الإجمالي: {total:.2f} ل.س\n\nهل تريد التأكيد؟"
        context.user_data['final_amount'] = total
    
    await update.message.reply_text(confirm_text, reply_markup=confirm_keyboard())
    return STATES["WALLET_DEPOSIT_CONFIRM"]

async def wallet_deposit_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=wallet_menu_keyboard())
        return STATES["WALLET_MENU"]
    
    if text != "✅ تأكيد":
        await update.message.reply_text("اختر تأكيد أو إلغاء", reply_markup=confirm_keyboard())
        return STATES["WALLET_DEPOSIT_CONFIRM"]
    
    method = context.user_data.get('deposit_method')
    currency = context.user_data.get('deposit_currency')
    amount = context.user_data.get('deposit_amount')
    final_amount = context.user_data.get('final_amount')
    
    method_names = {
        'syriatel': 'سيريتل كاش',
        'shamcash_syp': 'شام كاش - ليرة',
        'shamcash_usd': 'شام كاش - دولار'
    }
    
    request_id = await create_pending_request(
        update.effective_user.id,
        "wallet_deposit",
        final_amount,
        currency,
        method,
        f"Original: {amount} {currency}"
    )
    
    await add_transaction(
        update.effective_user.id,
        "wallet_deposit",
        final_amount,
        "pending",
        f"شحن محفظة - {method_names.get(method, method)}"
    )
    
    channel_message = (
        f"📥 طلب شحن محفظة جديد\n\n"
        f"👤 المستخدم: <code>{update.effective_user.id}</code>\n"
        f"💳 الطريقة: {method_names.get(method, method)}\n"
        f"💰 المبلغ الأصلي: {amount} {currency}\n"
        f"💵 المبلغ النهائي: {final_amount:.2f} ل.س\n"
        f"📋 رقم الطلب: <code>{request_id}</code>"
    )
    
    await context.bot.send_message(
        PENDING_CHANNEL_ID,
        channel_message,
        reply_markup=approval_inline_keyboard(request_id),
        parse_mode="HTML"
    )
    
    await update.message.reply_text(
        f"✅ تم إرسال طلب الشحن للمراجعة\n\n"
        f"📋 رقم الطلب: {request_id}\n"
        f"💰 المبلغ: {final_amount:.2f} ل.س\n\n"
        f"سيتم إشعارك عند الموافقة",
        reply_markup=wallet_menu_keyboard()
    )
    
    return STATES["WALLET_MENU"]

async def wallet_withdraw_method(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    min_withdraw = await get_setting("min_withdraw")
    
    if user['wallet_balance'] < min_withdraw:
        await update.message.reply_text(
            f"⚠️ رصيدك غير كافٍ للسحب\n"
            f"الحد الأدنى للسحب: {min_withdraw} ل.س\n"
            f"رصيدك: {user['wallet_balance']:.2f} ل.س",
            reply_markup=wallet_menu_keyboard()
        )
        return STATES["WALLET_MENU"]
    
    await update.message.reply_text(
        f"📤 سحب من المحفظة\n\n"
        f"💰 رصيدك: {user['wallet_balance']:.2f} ل.س\n"
        f"الحد الأدنى: {min_withdraw} ل.س\n\n"
        f"اختر طريقة السحب:",
        reply_markup=withdraw_method_keyboard()
    )
    return STATES["WALLET_WITHDRAW_METHOD"]

async def wallet_withdraw_syriatel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['withdraw_method'] = 'syriatel'
    await update.message.reply_text(
        "📱 سحب عبر سيريتل كاش\n\nأدخل المبلغ المطلوب سحبه:",
        reply_markup=cancel_keyboard()
    )
    return STATES["WALLET_WITHDRAW_AMOUNT"]

async def wallet_withdraw_shamcash(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['withdraw_method'] = 'shamcash'
    await update.message.reply_text(
        "💵 سحب عبر شام كاش\n\nأدخل المبلغ المطلوب سحبه:",
        reply_markup=cancel_keyboard()
    )
    return STATES["WALLET_WITHDRAW_AMOUNT"]

async def wallet_withdraw_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=wallet_menu_keyboard())
        return STATES["WALLET_MENU"]
    
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except:
        await update.message.reply_text("⚠️ أدخل مبلغاً صحيحاً", reply_markup=cancel_keyboard())
        return STATES["WALLET_WITHDRAW_AMOUNT"]
    
    user = await get_user(update.effective_user.id)
    min_withdraw = await get_setting("min_withdraw")
    
    if amount < min_withdraw:
        await update.message.reply_text(
            f"⚠️ المبلغ أقل من الحد الأدنى: {min_withdraw} ل.س",
            reply_markup=cancel_keyboard()
        )
        return STATES["WALLET_WITHDRAW_AMOUNT"]
    
    if amount > user['wallet_balance']:
        await update.message.reply_text(
            f"⚠️ رصيدك غير كافٍ!\nرصيدك: {user['wallet_balance']:.2f} ل.س",
            reply_markup=cancel_keyboard()
        )
        return STATES["WALLET_WITHDRAW_AMOUNT"]
    
    context.user_data['withdraw_amount'] = amount
    method = context.user_data.get('withdraw_method')
    
    if method == 'syriatel':
        await update.message.reply_text(
            "📱 أدخل رقم الهاتف للسحب عليه:",
            reply_markup=cancel_keyboard()
        )
    else:
        await update.message.reply_text(
            "💵 أدخل كود الدفع للسحب عليه:",
            reply_markup=cancel_keyboard()
        )
    
    return STATES["WALLET_WITHDRAW_INFO"]

async def wallet_withdraw_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=wallet_menu_keyboard())
        return STATES["WALLET_MENU"]
    
    withdraw_info = text.strip()
    amount = context.user_data.get('withdraw_amount')
    method = context.user_data.get('withdraw_method')
    method_names = {'syriatel': 'سيريتل كاش', 'shamcash': 'شام كاش'}
    
    await update_wallet(update.effective_user.id, -amount)
    
    request_id = await create_pending_request(
        update.effective_user.id,
        "wallet_withdraw",
        amount,
        "SYP",
        f"{method}|{withdraw_info}"
    )
    
    await add_transaction(
        update.effective_user.id,
        "wallet_withdraw",
        amount,
        "pending",
        f"سحب من المحفظة - {method_names.get(method, method)}"
    )
    
    if method == 'syriatel':
        info_label = "📱 رقم الهاتف"
    else:
        info_label = "💳 كود الدفع"
    
    channel_message = (
        f"📤 طلب سحب من المحفظة\n\n"
        f"👤 المستخدم: <code>{update.effective_user.id}</code>\n"
        f"💳 الطريقة: {method_names.get(method, method)}\n"
        f"{info_label}: <code>{withdraw_info}</code>\n"
        f"💰 المبلغ: {amount:.2f} ل.س\n"
        f"📋 رقم الطلب: <code>{request_id}</code>"
    )
    
    await context.bot.send_message(
        PENDING_CHANNEL_ID,
        channel_message,
        reply_markup=approval_inline_keyboard(request_id),
        parse_mode="HTML"
    )
    
    await update.message.reply_text(
        f"✅ تم إرسال طلب السحب للمراجعة\n\n"
        f"📋 رقم الطلب: {request_id}\n"
        f"💰 المبلغ: {amount:.2f} ل.س\n\n"
        f"سيتم إشعارك عند الموافقة",
        reply_markup=wallet_menu_keyboard()
    )
    
    return STATES["WALLET_MENU"]

async def wallet_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.common import go_back
    return await go_back(update, context)
