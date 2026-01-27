# 𝔻𝕣𝕒𝕩 𝕥𝕙𝕖 𝔻𝕖𝕤𝕥𝕣𝕠𝕪𝕖𝕣 Telegram Bot

## Overview
A comprehensive Telegram bot for managing iChancy gaming accounts with wallet functionality, built in Python using python-telegram-bot v20+.

## Features
- iChancy account creation and management
- Wallet system with Syriatel Cash and ShamCash support
- Referral system with commission tracking
- Gift code system
- Point gifting between users
- Admin panel with full control
- Pending request approval system
- Arabic interface

## Project Structure
```
├── main.py                 # Bot entry point
├── config.py               # Configuration and constants
├── database/
│   └── db.py              # SQLite database operations
├── handlers/
│   ├── common.py          # Common handlers and utilities
│   ├── ichancy.py         # iChancy account handlers
│   ├── wallet.py          # Wallet management handlers
│   ├── referral.py        # Referral system handlers
│   ├── gift.py            # Gift code and gifting handlers
│   ├── admin.py           # Admin panel handlers
│   ├── callbacks.py       # Inline button callbacks
│   └── misc.py            # Miscellaneous handlers
└── utils/
    ├── ichancy_api.py     # iChancy API integration
    └── keyboards.py       # Telegram keyboard definitions
```

## Environment Variables
- `BOT_TOKEN`: Telegram bot token (required)

## Running the Bot
```bash
python main.py
```

## Admin Commands
- `/admin` - Access admin panel (restricted to admin IDs)

## Database
Uses SQLite with the following tables:
- users: User accounts and wallet balances
- transactions: Transaction history
- pending_requests: Pending approval requests
- gift_codes: Gift code management
- gift_code_uses: Gift code usage tracking
- settings: Bot configuration settings

## Recent Changes
- Initial bot implementation with full Arabic interface
- SQLite database integration
- iChancy API integration for account management
- Wallet system with multiple payment methods
- Referral system with automatic commission
- Admin panel with comprehensive controls
