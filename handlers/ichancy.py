from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from config import STATES, PENDING_CHANNEL_ID
from database.db import get_user, update_user, update_wallet, create_pending_request, add_transaction
from utils.keyboards import ichancy_menu_keyboard, main_menu_keyboard, back_keyboard, cancel_keyboard, approval_inline_keyboard
from utils.ichancy_api import get_api
from handlers.common import require_subscription, require_bot_active

async def ichancy_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_subscription(update, context):
        return ConversationHandler.END
    
    if not await require_bot_active(update, context):
        return ConversationHandler.END
    
    await update.message.reply_text(
        "🎮 إدارة حساب iChancy\n\nاختر العملية المطلوبة:",
        reply_markup=ichancy_menu_keyboard()
    )
    return STATES["ICHANCY_MENU"]

async def create_account_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    if user and user.get('ichancy_player_id'):
        await update.message.reply_text(
            f"✅ لديك حساب بالفعل!\n\n"
            f"🎮 اسم المستخدم: <code>{user['ichancy_username']}</code>\n"
            f"🆔 معرف اللاعب: <code>{user['ichancy_player_id']}</code>\n\n"
            f"⚠️ لا يمكنك إنشاء أكثر من حساب واحد.",
            reply_markup=ichancy_menu_keyboard(),
            parse_mode="HTML"
        )
        return STATES["ICHANCY_MENU"]
    
    await update.message.reply_text(
        "📝 إنشاء حساب جديد\n\nأدخل اسم المستخدم المطلوب (بالإنجليزية فقط):",
        reply_markup=cancel_keyboard()
    )
    return STATES["CREATE_USERNAME"]

async def create_account_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=ichancy_menu_keyboard())
        return STATES["ICHANCY_MENU"]
    
    if not text.isalnum():
        await update.message.reply_text(
            "⚠️ اسم المستخدم يجب أن يحتوي على أحرف وأرقام إنجليزية فقط.\nحاول مرة أخرى:",
            reply_markup=cancel_keyboard()
        )
        return STATES["CREATE_USERNAME"]
    
    context.user_data['new_username'] = text
    await update.message.reply_text(
        f"✅ اسم المستخدم: {text}\n\nالآن أدخل كلمة المرور (8 أحرف على الأقل):",
        reply_markup=cancel_keyboard()
    )
    return STATES["CREATE_PASSWORD"]

async def create_account_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=ichancy_menu_keyboard())
        return STATES["ICHANCY_MENU"]
    
    if len(text) < 8:
        await update.message.reply_text(
            "⚠️ كلمة المرور يجب أن تكون 8 أحرف على الأقل.\nحاول مرة أخرى:",
            reply_markup=cancel_keyboard()
        )
        return STATES["CREATE_PASSWORD"]
    
    username = context.user_data.get('new_username')
    password = text
    
    await update.message.reply_text("⏳ جاري إنشاء الحساب...")
    
    api = get_api()
    success, message, player_id = await api.register_player(username, password)
    
    if success:
        await update_user(
            update.effective_user.id,
            ichancy_username=username,
            ichancy_player_id=player_id
        )
        await update.message.reply_text(
            f"✅ تم إنشاء الحساب بنجاح!\n\n"
            f"🎮 اسم المستخدم: <code>{username}</code>\n"
            f"🔑 كلمة المرور: <code>{password}</code>\n"
            f"🆔 معرف اللاعب: <code>{player_id}</code>\n\n"
            f"احتفظ بهذه المعلومات!",
            reply_markup=ichancy_menu_keyboard(),
            parse_mode="HTML"
        )
    else:
        await update.message.reply_text(
            f"❌ فشل إنشاء الحساب:\n{message}",
            reply_markup=ichancy_menu_keyboard()
        )
    
    return STATES["ICHANCY_MENU"]

async def deposit_to_ichancy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    
    if not user or not user.get('ichancy_player_id'):
        await update.message.reply_text(
            "⚠️ يجب إنشاء حساب iChancy أولاً",
            reply_markup=ichancy_menu_keyboard()
        )
        return STATES["ICHANCY_MENU"]
    
    await update.message.reply_text(
        f"💳 شحن حساب iChancy\n\n"
        f"💰 رصيد محفظتك: {user['wallet_balance']:.2f} ل.س\n\n"
        f"أدخل المبلغ المطلوب شحنه:",
        reply_markup=cancel_keyboard()
    )
    return STATES["DEPOSIT_AMOUNT"]

async def deposit_to_ichancy_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=ichancy_menu_keyboard())
        return STATES["ICHANCY_MENU"]
    
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except:
        await update.message.reply_text(
            "⚠️ أدخل مبلغاً صحيحاً",
            reply_markup=cancel_keyboard()
        )
        return STATES["DEPOSIT_AMOUNT"]
    
    user = await get_user(update.effective_user.id)
    
    if amount > user['wallet_balance']:
        await update.message.reply_text(
            f"⚠️ رصيدك غير كافٍ!\nرصيدك الحالي: {user['wallet_balance']:.2f} ل.س",
            reply_markup=cancel_keyboard()
        )
        return STATES["DEPOSIT_AMOUNT"]
    
    await update_wallet(update.effective_user.id, -amount)
    
    request_id = await create_pending_request(
        update.effective_user.id,
        "ichancy_deposit",
        amount,
        "SYP",
        "ichancy",
        user['ichancy_player_id']
    )
    
    await add_transaction(
        update.effective_user.id,
        "ichancy_deposit",
        amount,
        "pending",
        f"شحن iChancy - {user['ichancy_player_id']}"
    )
    
    channel_message = (
        f"📥 طلب شحن iChancy جديد\n\n"
        f"👤 المستخدم: <code>{update.effective_user.id}</code>\n"
        f"🎮 معرف اللاعب: <code>{user['ichancy_player_id']}</code>\n"
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
        f"✅ تم إرسال طلب الشحن للمراجعة\n\n"
        f"💰 المبلغ: {amount:.2f} ل.س\n"
        f"📋 رقم الطلب: {request_id}\n\n"
        f"سيتم إشعارك عند الموافقة",
        reply_markup=ichancy_menu_keyboard()
    )
    
    return STATES["ICHANCY_MENU"]

async def withdraw_from_ichancy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    
    if not user or not user.get('ichancy_player_id'):
        await update.message.reply_text(
            "⚠️ يجب إنشاء حساب iChancy أولاً",
            reply_markup=ichancy_menu_keyboard()
        )
        return STATES["ICHANCY_MENU"]
    
    await update.message.reply_text(
        f"💸 السحب من حساب iChancy\n\n"
        f"أدخل المبلغ المطلوب سحبه:",
        reply_markup=cancel_keyboard()
    )
    return STATES["WITHDRAW_AMOUNT"]

async def withdraw_from_ichancy_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    
    if text == "❌ إلغاء":
        await update.message.reply_text("تم الإلغاء", reply_markup=ichancy_menu_keyboard())
        return STATES["ICHANCY_MENU"]
    
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except:
        await update.message.reply_text(
            "⚠️ أدخل مبلغاً صحيحاً",
            reply_markup=cancel_keyboard()
        )
        return STATES["WITHDRAW_AMOUNT"]
    
    user = await get_user(update.effective_user.id)
    
    request_id = await create_pending_request(
        update.effective_user.id,
        "ichancy_withdraw",
        amount,
        "SYP",
        "ichancy",
        user['ichancy_player_id']
    )
    
    await add_transaction(
        update.effective_user.id,
        "ichancy_withdraw",
        amount,
        "pending",
        f"سحب من iChancy - {user['ichancy_player_id']}"
    )
    
    channel_message = (
        f"📤 طلب سحب من iChancy جديد\n\n"
        f"👤 المستخدم: <code>{update.effective_user.id}</code>\n"
        f"🎮 معرف اللاعب: <code>{user['ichancy_player_id']}</code>\n"
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
        f"💰 المبلغ: {amount:.2f} ل.س\n"
        f"📋 رقم الطلب: {request_id}\n\n"
        f"سيتم إشعارك عند الموافقة",
        reply_markup=ichancy_menu_keyboard()
    )
    
    return STATES["ICHANCY_MENU"]

async def show_my_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = await get_user(update.effective_user.id)
    
    if not user:
        await update.message.reply_text("⚠️ لم يتم العثور على حسابك")
        return STATES["ICHANCY_MENU"]
    
    info_text = (
        f"ℹ️ معلوماتك:\n\n"
        f"🆔 معرف تيليجرام: <code>{update.effective_user.id}</code>\n"
        f"💰 رصيد المحفظة: {user['wallet_balance']:.2f} ل.س\n"
    )
    
    if user.get('ichancy_username'):
        info_text += f"\n🎮 حساب iChancy:\n"
        info_text += f"   اسم المستخدم: <code>{user['ichancy_username']}</code>\n"
        info_text += f"   معرف اللاعب: <code>{user.get('ichancy_player_id', 'غير متوفر')}</code>"
    else:
        info_text += "\n⚠️ لم تقم بإنشاء حساب iChancy بعد"
    
    await update.message.reply_text(info_text, reply_markup=ichancy_menu_keyboard(), parse_mode="HTML")
    return STATES["ICHANCY_MENU"]

async def ichancy_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.common import go_back
    return await go_back(update, context)
