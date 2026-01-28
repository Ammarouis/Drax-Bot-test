from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard():
    keyboard = [
        ["🎮 إدارة حساب iChancy", "💰 إدارة محفظة البوت"],
        ["👥 نظام الإحالة", "📞 التواصل والدعم"],
        ["🎁 تفعيل كود هدية", "🎈 إهداء نقاط"],
        ["📜 السجل", "💎 معلومات البونص الحالي"],
        ["⏸️ إيقاف العمليات المعلقة", "📋 الشروط والأحكام"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def ichancy_menu_keyboard():
    keyboard = [
        ["➕ إنشاء حساب", "💳 شحن الحساب"],
        ["💸 السحب من الحساب", "ℹ️ عرض معلوماتي"],
        ["🔙 رجوع"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def wallet_menu_keyboard():
    keyboard = [
        ["📥 شحن المحفظة", "📤 سحب من المحفظة"],
        ["🔙 رجوع"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def deposit_method_keyboard():
    keyboard = [
        ["📱 سيريتل كاش"],
        ["💵 شام كاش - ليرة سورية", "💲 شام كاش - دولار"],
        ["🔙 رجوع"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def withdraw_method_keyboard():
    keyboard = [
        ["📱 سحب سيريتل كاش"],
        ["💵 سحب شام كاش"],
        ["🔙 رجوع"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def back_keyboard():
    keyboard = [["🔙 رجوع"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def cancel_keyboard():
    keyboard = [["❌ إلغاء"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def admin_menu_keyboard():
    keyboard = [
        ["📊 تغيير عمولة الإحالة", "📉 تعديل الحدود الدنيا"],
        ["💰 تغيير رصيد مستخدم", "📈 إحصائيات المستخدمين"],
        ["🎁 إعدادات الإهداء", "🔄 تشغيل/إيقاف البوت"],
        ["💎 إعدادات البونص", "📞 تغيير معرف الدعم"],
        ["✉️ رسالة لمستخدم", "📢 رسالة جماعية"],
        ["💱 تغيير سعر صرف الدولار", "📝 تعديل أكواد الدفع"],
        ["🎫 إنشاء كود هدية", "💵 العمولات المجمعة"],
        ["🔙 رجوع"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def min_limits_keyboard():
    keyboard = [
        ["الحد الأدنى سيريتل", "الحد الأدنى شام ليرة"],
        ["الحد الأدنى شام دولار", "الحد الأدنى للسحب"],
        ["🔙 رجوع"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def gift_settings_keyboard():
    keyboard = [
        ["تشغيل/إيقاف الإهداء", "الحد الأدنى للإهداء"],
        ["عمولة الإهداء", "🔙 رجوع"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def payment_codes_keyboard():
    keyboard = [
        ["كود سيريتل", "كود شام كاش"],
        ["🔙 رجوع"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def approval_inline_keyboard(request_id: int):
    keyboard = [
        [
            InlineKeyboardButton("✅ قبول", callback_data=f"approve_{request_id}"),
            InlineKeyboardButton("❌ رفض", callback_data=f"reject_{request_id}")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

def confirm_keyboard():
    keyboard = [["✅ تأكيد", "❌ إلغاء"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
