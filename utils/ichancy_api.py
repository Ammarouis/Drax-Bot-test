import httpx
import asyncio
import logging
from config import AGENT_USERNAME, AGENT_PASSWORD, PARENT_ID, ICHANCY_BASE_URL

logger = logging.getLogger(__name__)

class IChancyAPI:
    def __init__(self):
        self.client = None
        self.logged_in = False
        self.cookies = {}
    
    async def _get_client(self):
        if self.client is None:
            self.client = httpx.AsyncClient(timeout=30.0, cookies=self.cookies)
        return self.client
    
    async def login(self):
        try:
            client = await self._get_client()
            login_url = f"{ICHANCY_BASE_URL}/User/signInRequest"
            payload = {
                "login": AGENT_USERNAME,
                "password": AGENT_PASSWORD
            }
            response = await client.post(login_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") or result.get("result"):
                    self.logged_in = True
                    self.cookies = dict(response.cookies)
                    return True, "تم تسجيل الدخول بنجاح"
                return False, result.get("message", "فشل تسجيل الدخول")
            return False, f"خطأ في الاتصال: {response.status_code}"
        except Exception as e:
            return False, f"خطأ: {str(e)}"
    
    async def get_children(self):
        try:
            client = await self._get_client()
            url = f"{ICHANCY_BASE_URL}/Agent/getChildren"
            response = await client.post(url, json={})
            if response.status_code == 200:
                return True, response.json()
            return False, "فشل في جلب البيانات"
        except Exception as e:
            return False, str(e)
    
    async def register_player(self, username: str, password: str):
        try:
            if not self.logged_in:
                success, msg = await self.login()
                if not success:
                    logger.error(f"Login failed: {msg}")
                    return False, msg, None
            
            await self.get_children()
            
            client = await self._get_client()
            register_url = f"{ICHANCY_BASE_URL}/Player/registerPlayer"
            payload = {
                "login": username,
                "password": password,
                "email": f"{username}@gmail.com",
                "parentId": PARENT_ID
            }
            
            logger.info(f"Registering player: {username}")
            response = await client.post(register_url, json=payload)
            logger.info(f"Register response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Register response: {result}")
                
                if result.get("success") or result.get("result"):
                    player_id = await self.get_player_id(username)
                    logger.info(f"Player ID found: {player_id}")
                    if player_id:
                        return True, "تم إنشاء الحساب بنجاح", player_id
                    return True, "تم إنشاء الحساب ولكن لم يتم العثور على معرف اللاعب", None
                
                error_msg = result.get("message") or result.get("error") or str(result)
                logger.error(f"Register failed: {error_msg}")
                return False, error_msg, None
            return False, f"خطأ: {response.status_code}", None
        except Exception as e:
            logger.exception(f"Register exception: {e}")
            return False, f"خطأ: {str(e)}", None
    
    async def get_player_id(self, username: str):
        try:
            client = await self._get_client()
            url = f"{ICHANCY_BASE_URL}/Statistics/getPlayersStatisticsPro"
            payload = {
                "start": 0,
                "limit": 10,
                "filter": {},
                "searchBy": {"players": username}
            }
            response = await client.post(url, json=payload)
            logger.info(f"Get player ID response status: {response.status_code}")
            if response.status_code == 200:
                result = response.json()
                logger.info(f"Get player ID response: {result}")
                records = result.get("result", {}).get("records", [])
                if records:
                    player_id = records[0].get("playerId")
                    logger.info(f"Found player ID: {player_id}")
                    return player_id
                logger.warning(f"No records found for username: {username}")
            return None
        except Exception as e:
            logger.exception(f"Get player ID exception: {e}")
            return None
    
    async def deposit_to_player(self, player_id: str, amount: float):
        try:
            if not self.logged_in:
                success, msg = await self.login()
                if not success:
                    return False, msg
            
            client = await self._get_client()
            url = f"{ICHANCY_BASE_URL}/Player/depositToPlayer"
            payload = {
                "amount": abs(amount),
                "comment": None,
                "playerId": player_id,
                "currencyCode": "NSP",
                "currency": "NSP",
                "moneyStatus": 5
            }
            
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") or result.get("result"):
                    return True, "تم الإيداع بنجاح"
                return False, result.get("message", "فشل الإيداع")
            return False, f"خطأ: {response.status_code}"
        except Exception as e:
            return False, f"خطأ: {str(e)}"
    
    async def withdraw_from_player(self, player_id: str, amount: float):
        try:
            if not self.logged_in:
                success, msg = await self.login()
                if not success:
                    return False, msg
            
            client = await self._get_client()
            url = f"{ICHANCY_BASE_URL}/Player/withdrawFromPlayer"
            payload = {
                "amount": -abs(amount),
                "comment": None,
                "playerId": player_id,
                "currencyCode": "NSP",
                "currency": "NSP",
                "moneyStatus": 5
            }
            
            response = await client.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") or result.get("result"):
                    return True, "تم السحب بنجاح"
                return False, result.get("message", "فشل السحب")
            return False, f"خطأ: {response.status_code}"
        except Exception as e:
            return False, f"خطأ: {str(e)}"
    
    async def close(self):
        if self.client:
            await self.client.aclose()
            self.client = None

def get_api():
    return IChancyAPI()
