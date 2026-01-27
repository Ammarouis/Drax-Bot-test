import requests
from config import AGENT_USERNAME, AGENT_PASSWORD, PARENT_ID, ICHANCY_BASE_URL

class IChancyAPI:
    def __init__(self):
        self.session = requests.Session()
        self.logged_in = False
    
    def login(self):
        try:
            login_url = f"{ICHANCY_BASE_URL}/User/signInRequest"
            payload = {
                "login": AGENT_USERNAME,
                "password": AGENT_PASSWORD
            }
            response = self.session.post(login_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") or result.get("result"):
                    self.logged_in = True
                    return True, "تم تسجيل الدخول بنجاح"
                return False, result.get("message", "فشل تسجيل الدخول")
            return False, f"خطأ في الاتصال: {response.status_code}"
        except Exception as e:
            return False, f"خطأ: {str(e)}"
    
    def get_children(self):
        try:
            url = f"{ICHANCY_BASE_URL}/Agent/getChildren"
            response = self.session.post(url, json={})
            if response.status_code == 200:
                return True, response.json()
            return False, "فشل في جلب البيانات"
        except Exception as e:
            return False, str(e)
    
    def register_player(self, username: str, password: str):
        try:
            if not self.logged_in:
                success, msg = self.login()
                if not success:
                    return False, msg, None
            
            self.get_children()
            
            register_url = f"{ICHANCY_BASE_URL}/Player/registerPlayer"
            payload = {
                "login": username,
                "password": password,
                "email": f"{username}@gmail.com",
                "parentId": PARENT_ID
            }
            
            response = self.session.post(register_url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") or result.get("result"):
                    player_id = self.get_player_id(username)
                    if player_id:
                        return True, "تم إنشاء الحساب بنجاح", player_id
                    return True, "تم إنشاء الحساب ولكن لم يتم العثور على معرف اللاعب", None
                return False, result.get("message", "فشل إنشاء الحساب"), None
            return False, f"خطأ: {response.status_code}", None
        except Exception as e:
            return False, f"خطأ: {str(e)}", None
    
    def get_player_id(self, username: str):
        try:
            url = f"{ICHANCY_BASE_URL}/Statistics/getPlayersStatisticsPro"
            payload = {
                "start": 0,
                "limit": 10,
                "filter": {},
                "searchBy": {"players": username}
            }
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                records = result.get("result", {}).get("records", [])
                if records:
                    return records[0].get("playerId")
            return None
        except:
            return None
    
    def deposit_to_player(self, player_id: str, amount: float):
        try:
            if not self.logged_in:
                success, msg = self.login()
                if not success:
                    return False, msg
            
            url = f"{ICHANCY_BASE_URL}/Player/depositToPlayer"
            payload = {
                "amount": abs(amount),
                "comment": None,
                "playerId": player_id,
                "currencyCode": "NSP",
                "currency": "NSP",
                "moneyStatus": 5
            }
            
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") or result.get("result"):
                    return True, "تم الإيداع بنجاح"
                return False, result.get("message", "فشل الإيداع")
            return False, f"خطأ: {response.status_code}"
        except Exception as e:
            return False, f"خطأ: {str(e)}"
    
    def withdraw_from_player(self, player_id: str, amount: float):
        try:
            if not self.logged_in:
                success, msg = self.login()
                if not success:
                    return False, msg
            
            url = f"{ICHANCY_BASE_URL}/Player/withdrawFromPlayer"
            payload = {
                "amount": -abs(amount),
                "comment": None,
                "playerId": player_id,
                "currencyCode": "NSP",
                "currency": "NSP",
                "moneyStatus": 5
            }
            
            response = self.session.post(url, json=payload)
            if response.status_code == 200:
                result = response.json()
                if result.get("success") or result.get("result"):
                    return True, "تم السحب بنجاح"
                return False, result.get("message", "فشل السحب")
            return False, f"خطأ: {response.status_code}"
        except Exception as e:
            return False, f"خطأ: {str(e)}"

def get_api():
    return IChancyAPI()
