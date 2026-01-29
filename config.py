import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [6967281416, 1652070303, 8485216961]
PENDING_CHANNEL_ID = -1003666982201
REQUIRED_CHANNEL = "@DraxtheDestroyer_Channel"

AGENT_USERNAME = os.getenv("ICHANCY_AGENT_USERNAME", "")
AGENT_PASSWORD = os.getenv("ICHANCY_AGENT_PASSWORD", "")
PARENT_ID = os.getenv("ICHANCY_PARENT_ID", "")
CF_CLEARANCE = os.getenv("ICHANCY_CF_CLEARANCE", "")

ICHANCY_BASE_URL = "https://agents.ichancy.com/global/api"

DEFAULT_SETTINGS = {
    "exchange_rate_usd": 15000,
    "referral_commission": 5,
    "deposit_bonus": 0,
    "min_syriatel": 50,
    "min_shamcash_syp": 50,
    "min_shamcash_usd": 0.5,
    "min_withdraw": 100,
    "min_gift": 100,
    "gift_commission": 2,
    "syriatel_code": "*117*1234#",
    "shamcash_code": "SHAM123",
    "support_username": "@DraxtheDestroyer_Support",
    "gifting_enabled": 1,
    "bot_active": 1
}

STATES = {
    "MAIN_MENU": 0,
    "ICHANCY_MENU": 1,
    "CREATE_USERNAME": 2,
    "CREATE_PASSWORD": 3,
    "DEPOSIT_AMOUNT": 4,
    "WITHDRAW_AMOUNT": 5,
    "WALLET_MENU": 6,
    "WALLET_DEPOSIT_METHOD": 7,
    "WALLET_DEPOSIT_AMOUNT": 8,
    "WALLET_DEPOSIT_CONFIRM": 9,
    "WALLET_WITHDRAW_METHOD": 10,
    "WALLET_WITHDRAW_AMOUNT": 11,
    "GIFT_CODE": 12,
    "GIFT_POINTS_USER": 13,
    "GIFT_POINTS_AMOUNT": 14,
    "ADMIN_MENU": 15,
    "ADMIN_REFERRAL_COMMISSION": 16,
    "ADMIN_MIN_LIMITS": 17,
    "ADMIN_USER_BALANCE": 18,
    "ADMIN_USER_BALANCE_AMOUNT": 19,
    "ADMIN_GIFT_SETTINGS": 20,
    "ADMIN_BONUS_SETTINGS": 21,
    "ADMIN_SUPPORT_USERNAME": 22,
    "ADMIN_MESSAGE_USER": 23,
    "ADMIN_MESSAGE_USER_TEXT": 24,
    "ADMIN_BROADCAST": 25,
    "ADMIN_EXCHANGE_RATE": 26,
    "ADMIN_PAYMENT_CODES": 27,
    "ADMIN_CREATE_GIFT_CODE": 28,
    "ADMIN_GIFT_CODE_POINTS": 29,
    "ADMIN_GIFT_CODE_USES": 30,
    "ADMIN_MIN_LIMIT_TYPE": 31,
    "ADMIN_MIN_LIMIT_VALUE": 32,
    "ADMIN_GIFT_TOGGLE": 33,
    "ADMIN_GIFT_MIN": 34,
    "ADMIN_GIFT_COMMISSION": 35,
    "ADMIN_PAYMENT_CODE_TYPE": 36,
    "ADMIN_PAYMENT_CODE_VALUE": 37,
}
