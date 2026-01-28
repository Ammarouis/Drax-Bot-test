import aiosqlite
import os
from config import DEFAULT_SETTINGS

DATABASE_PATH = "bot_database.db"

async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                telegram_id INTEGER PRIMARY KEY,
                username TEXT,
                ichancy_username TEXT,
                ichancy_player_id TEXT,
                wallet_balance REAL DEFAULT 0,
                referrer_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                type TEXT,
                amount REAL,
                status TEXT DEFAULT 'pending',
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS pending_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                telegram_id INTEGER,
                request_type TEXT,
                amount REAL,
                currency TEXT DEFAULT 'SYP',
                method TEXT,
                status TEXT DEFAULT 'pending',
                message_id INTEGER,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS gift_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT UNIQUE,
                points REAL,
                max_uses INTEGER,
                current_uses INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS gift_code_uses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                code TEXT,
                telegram_id INTEGER,
                used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (telegram_id) REFERENCES users(telegram_id)
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        await db.execute('''
            CREATE TABLE IF NOT EXISTS commissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                amount REAL,
                source_user INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        for key, value in DEFAULT_SETTINGS.items():
            await db.execute('''
                INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)
            ''', (key, str(value)))
        
        await db.commit()

async def get_user(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM users WHERE telegram_id = ?', (telegram_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def create_user(telegram_id: int, username: str = None, referrer_id: int = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT OR IGNORE INTO users (telegram_id, username, referrer_id)
            VALUES (?, ?, ?)
        ''', (telegram_id, username, referrer_id))
        await db.commit()

async def update_user(telegram_id: int, **kwargs):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        for key, value in kwargs.items():
            await db.execute(f'''
                UPDATE users SET {key} = ? WHERE telegram_id = ?
            ''', (value, telegram_id))
        await db.commit()

async def update_wallet(telegram_id: int, amount: float):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            UPDATE users SET wallet_balance = wallet_balance + ? WHERE telegram_id = ?
        ''', (amount, telegram_id))
        await db.commit()

async def set_wallet(telegram_id: int, amount: float):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            UPDATE users SET wallet_balance = ? WHERE telegram_id = ?
        ''', (amount, telegram_id))
        await db.commit()

async def get_setting(key: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute(
            'SELECT value FROM settings WHERE key = ?', (key,)
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                value = row[0]
                if key in ['gifting_enabled', 'bot_active']:
                    return value == '1' or value == 'True'
                try:
                    if '.' in value:
                        return float(value)
                    return int(value)
                except ValueError:
                    return value
            return None

async def update_setting(key: str, value):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)
        ''', (key, str(value)))
        await db.commit()

async def add_transaction(telegram_id: int, trans_type: str, amount: float, status: str = 'pending', details: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT INTO transactions (telegram_id, type, amount, status, details)
            VALUES (?, ?, ?, ?, ?)
        ''', (telegram_id, trans_type, amount, status, details))
        await db.commit()

async def get_transactions(telegram_id: int, limit: int = 5):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('''
            SELECT * FROM transactions WHERE telegram_id = ?
            ORDER BY created_at DESC LIMIT ?
        ''', (telegram_id, limit)) as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def create_pending_request(telegram_id: int, request_type: str, amount: float, 
                                  currency: str = 'SYP', method: str = None, details: str = None):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            INSERT INTO pending_requests (telegram_id, request_type, amount, currency, method, details)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (telegram_id, request_type, amount, currency, method, details))
        await db.commit()
        return cursor.lastrowid

async def update_pending_request(request_id: int, **kwargs):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        for key, value in kwargs.items():
            await db.execute(f'''
                UPDATE pending_requests SET {key} = ? WHERE id = ?
            ''', (value, request_id))
        await db.commit()

async def get_pending_request(request_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM pending_requests WHERE id = ?', (request_id,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def cancel_pending_requests(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            UPDATE pending_requests SET status = 'cancelled' 
            WHERE telegram_id = ? AND status = 'pending'
        ''', (telegram_id,))
        await db.commit()

async def create_gift_code(code: str, points: float, max_uses: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT INTO gift_codes (code, points, max_uses)
            VALUES (?, ?, ?)
        ''', (code, points, max_uses))
        await db.commit()

async def get_gift_code(code: str):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            'SELECT * FROM gift_codes WHERE code = ?', (code,)
        ) as cursor:
            row = await cursor.fetchone()
            return dict(row) if row else None

async def use_gift_code(code: str, telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        
        existing = await db.execute('''
            SELECT * FROM gift_code_uses WHERE code = ? AND telegram_id = ?
        ''', (code, telegram_id))
        if await existing.fetchone():
            return False, "already_used"
        
        async with db.execute(
            'SELECT * FROM gift_codes WHERE code = ?', (code,)
        ) as cursor:
            row = await cursor.fetchone()
            gift_code = dict(row) if row else None
        
        if not gift_code:
            return False, "not_found"
        if gift_code['current_uses'] >= gift_code['max_uses']:
            return False, "exhausted"
        
        await db.execute('''
            UPDATE gift_codes SET current_uses = current_uses + 1 WHERE code = ?
        ''', (code,))
        await db.execute('''
            INSERT INTO gift_code_uses (code, telegram_id) VALUES (?, ?)
        ''', (code, telegram_id))
        await db.execute('''
            UPDATE users SET wallet_balance = wallet_balance + ? WHERE telegram_id = ?
        ''', (gift_code['points'], telegram_id))
        await db.commit()
        return True, gift_code['points']

async def get_referral_stats(telegram_id: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute('''
            SELECT COUNT(*) FROM users WHERE referrer_id = ?
        ''', (telegram_id,)) as cursor:
            count = (await cursor.fetchone())[0]
        return count

async def get_all_users():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute('SELECT * FROM users') as cursor:
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

async def get_user_stats():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM users') as cursor:
            total = (await cursor.fetchone())[0]
        async with db.execute('SELECT SUM(wallet_balance) FROM users') as cursor:
            total_balance = (await cursor.fetchone())[0] or 0
        return {"total_users": total, "total_balance": total_balance}

async def add_commission(commission_type: str, amount: float, source_user: int):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT INTO commissions (type, amount, source_user)
            VALUES (?, ?, ?)
        ''', (commission_type, amount, source_user))
        await db.commit()

async def get_total_commission():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute('SELECT SUM(amount) FROM commissions') as cursor:
            total = (await cursor.fetchone())[0] or 0
        return total
