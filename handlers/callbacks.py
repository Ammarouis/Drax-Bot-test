from telegram import Update
from telegram.ext import ContextTypes
from config import ADMIN_IDS
from database.db import get_pending_request, update_pending_request, update_wallet, get_user, add_transaction, update_transaction_status
from utils.ichancy_api import get_api
from handlers.common import is_admin

async def approval_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if not is_admin(query.from_user.id):
        await query.answer("غير مصرح لك", show_alert=True)
        return
    
    data = query.data
    action, request_id = data.split("_", 1)
    request_id = int(request_id)
    
    request = await get_pending_request(request_id)
    if not request:
        await query.edit_message_text("⚠️ الطلب غير موجود")
        return
    
    if request['status'] != 'pending':
        await query.edit_message_text(f"⚠️ تم معالجة الطلب مسبقاً\n\nالحالة: {request['status']}")
        return
    
    user_id = request['telegram_id']
    amount = request['amount']
    request_type = request['request_type']
    
    if action == "approve":
        await update_pending_request(request_id, status='approved')
        await update_transaction_status(user_id, request_type, 'completed')
        
        if request_type == 'wallet_deposit':
            user = await get_user(user_id)
            await update_wallet(user_id, amount)
            
            if user and user.get('referrer_id'):
                from database.db import get_setting
                commission_rate = await get_setting("referral_commission")
                commission = amount * (commission_rate / 100)
                await update_wallet(user['referrer_id'], commission)
                await add_transaction(
                    user['referrer_id'],
                    "referral_commission",
                    commission,
                    "completed",
                    f"عمولة إحالة من {user_id}"
                )
            
            await query.edit_message_text(
                f"✅ تمت الموافقة\n\n"
                f"👤 المستخدم: <code>{user_id}</code>\n"
                f"💰 المبلغ: {amount:.2f} ل.س\n"
                f"📋 رقم الطلب: <code>{request_id}</code>",
                parse_mode="HTML"
            )
            
            try:
                await context.bot.send_message(
                    user_id,
                    f"✅ تمت الموافقة على طلب الشحن!\n\n"
                    f"💰 تمت إضافة {amount:.2f} ل.س إلى محفظتك"
                )
            except:
                pass
        
        elif request_type == 'wallet_withdraw':
            await query.edit_message_text(
                f"✅ تمت الموافقة على السحب\n\n"
                f"👤 المستخدم: <code>{user_id}</code>\n"
                f"💰 المبلغ: {amount:.2f} ل.س\n"
                f"📋 رقم الطلب: <code>{request_id}</code>",
                parse_mode="HTML"
            )
            
            try:
                await context.bot.send_message(
                    user_id,
                    f"✅ تمت الموافقة على طلب السحب!\n\n"
                    f"💰 المبلغ: {amount:.2f} ل.س\n"
                    f"سيتم التحويل قريباً"
                )
            except:
                pass
        
        elif request_type == 'ichancy_deposit':
            player_id = request['details']
            api = get_api()
            success, msg = await api.deposit_to_player(player_id, amount)
            
            if success:
                await query.edit_message_text(
                    f"✅ تمت الموافقة وتنفيذ الإيداع\n\n"
                    f"👤 المستخدم: <code>{user_id}</code>\n"
                    f"🎮 معرف اللاعب: <code>{player_id}</code>\n"
                    f"💰 المبلغ: {amount:.2f} ل.س",
                    parse_mode="HTML"
                )
                
                try:
                    await context.bot.send_message(
                        user_id,
                        f"✅ تم شحن حساب iChancy بنجاح!\n\n"
                        f"💰 المبلغ: {amount:.2f} ل.س"
                    )
                except:
                    pass
            else:
                await update_wallet(user_id, amount)
                await query.edit_message_text(
                    f"❌ فشل الإيداع في iChancy\n\n"
                    f"الخطأ: {msg}\n"
                    f"تم إرجاع الرصيد للمستخدم"
                )
        
        elif request_type == 'ichancy_withdraw':
            player_id = request['details']
            api = get_api()
            success, msg = await api.withdraw_from_player(player_id, amount)
            
            if success:
                await update_wallet(user_id, amount)
                await query.edit_message_text(
                    f"✅ تم السحب من iChancy وإضافة الرصيد\n\n"
                    f"👤 المستخدم: <code>{user_id}</code>\n"
                    f"💰 المبلغ: {amount:.2f} ل.س",
                    parse_mode="HTML"
                )
                
                try:
                    await context.bot.send_message(
                        user_id,
                        f"✅ تم السحب من iChancy بنجاح!\n\n"
                        f"💰 تمت إضافة {amount:.2f} ل.س إلى محفظتك"
                    )
                except:
                    pass
            else:
                await query.edit_message_text(
                    f"❌ فشل السحب من iChancy\n\n"
                    f"الخطأ: {msg}"
                )
    
    elif action == "reject":
        await update_pending_request(request_id, status='rejected')
        await update_transaction_status(user_id, request_type, 'rejected')
        
        if request_type in ['wallet_withdraw', 'ichancy_deposit']:
            await update_wallet(user_id, amount)
        
        await query.edit_message_text(
            f"❌ تم الرفض\n\n"
            f"👤 المستخدم: <code>{user_id}</code>\n"
            f"💰 المبلغ: {amount:.2f} ل.س\n"
            f"📋 رقم الطلب: <code>{request_id}</code>",
            parse_mode="HTML"
        )
        
        try:
            await context.bot.send_message(
                user_id,
                f"❌ تم رفض طلبك\n\n"
                f"📋 رقم الطلب: {request_id}\n"
                f"تواصل مع الدعم للاستفسار"
            )
        except:
            pass
