import requests
import json
import time
import random
import os
import urllib.parse
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon import functions, types

class BeThoMoBot:
    def __init__(self, acc):
        self.name = acc['name']
        self.uid = acc['uid']
        self.session_str = acc.get('session_str') or os.getenv(f"TELEGRAM_STRING_SESSION_ACC{acc.get('slot', '')}") or ''
        self.api_id = acc.get('api_id', 39182276)
        self.api_hash = acc.get('api_hash') or os.getenv('TELEGRAM_API_HASH') or ''
        self.unban_email = acc.get('unban_email') or os.getenv('UNBAN_EMAIL') or ''
        self.base_url = "https://api-bethomo.vercel.app/api"
        self.fb_url = f"https://be-tho-mo-default-rtdb.asia-southeast1.firebasedatabase.app/users/{self.uid}.json"
        self.init_data = None
        self.headers = None

    def get_headers(self):
        return {
            "Content-Type": "application/json",
            "x-init-data": self.init_data,
            "Origin": "https://app9006949357.tgcloud.ai",
            "Referer": "https://app9006949357.tgcloud.ai/",
            "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Mobile Safari/537.36"
        }

    def refresh_init_data(self):
        """Lấy init_data tươi từ Telegram WebApp qua Telethon"""
        if not self.session_str or not self.api_hash:
            print(f"[{self.name}] ❌ Thiếu session_str hoặc api_hash (kiểm tra secret TELEGRAM_ACCOUNTS_JSON).", flush=True)
            return False
        try:
            client = TelegramClient(StringSession(self.session_str), self.api_id, self.api_hash)
            client.connect()
            if not client.is_user_authorized():
                print(f"[{self.name}] ❌ Session Telegram chưa được xác thực!", flush=True)
                client.disconnect()
                return False

            bot = client.get_entity("BeThoMo_bot")
            app = types.InputBotAppShortName(bot_id=types.InputUser(bot.id, bot.access_hash), short_name="play")
            res = client(functions.messages.RequestAppWebViewRequest(peer=bot, app=app, platform="android"))
            client.disconnect()

            raw_init = res.url.split("#tgWebAppData=")[1].split("&tgWebAppVersion=")[0]
            self.init_data = urllib.parse.unquote(raw_init)
            self.headers = self.get_headers()
            return True
        except Exception as e:
            print(f"[{self.name}] ❌ Lỗi lấy init_data qua Telethon: {e}", flush=True)
            return False

    def get_firebase_profile(self):
        """Đọc profile live từ Firebase Realtime Database"""
        try:
            r = requests.get(self.fb_url, timeout=15)
            if r.status_code == 200:
                return r.json()
        except Exception as e:
            print(f"[{self.name}] Lỗi đọc Firebase: {e}", flush=True)
        return None

    def claim_referral(self):
        """Nhận thưởng giới thiệu bạn bè (nếu có)"""
        try:
            r = requests.get(f"{self.base_url}/referral", headers=self.headers, timeout=15)
            if r.status_code == 200:
                print(f"[{self.name}] 🎁 Check Referral: OK", flush=True)
        except Exception as e:
            print(f"[{self.name}] Lỗi claim_referral: {e}", flush=True)

    def claim_tasks(self, completed_tasks):
        """Nhận thưởng các nhiệm vụ cộng đồng chưa hoàn thành"""
        all_task_ids = ["t1", "t2", "t5", "t6", "t7", "t8"]
        for tid in all_task_ids:
            if completed_tasks and completed_tasks.get(tid):
                continue
            try:
                r = requests.post(
                    f"{self.base_url}/claim_task",
                    headers=self.headers,
                    json={"taskId": tid},
                    timeout=15
                )
                res = r.json()
                if res.get("success"):
                    print(f"[{self.name}] ✅ Nhận thưởng nhiệm vụ {tid} thành công!", flush=True)
                else:
                    err = res.get("errorCode")
                    if err != "already_claimed":
                        print(f"[{self.name}] Nhiệm vụ {tid}: {err}", flush=True)
                time.sleep(random.uniform(1.5, 3.0))
            except Exception as e:
                print(f"[{self.name}] Lỗi claim_task {tid}: {e}", flush=True)

    def request_unban_if_needed(self, profile):
        """Tự động gửi yêu cầu mở khóa nếu tài khoản bị khóa nhầm"""
        if profile and profile.get("isBanned"):
            if not self.unban_email:
                print(f"[{self.name}] ⚠️ Tài khoản bị gắn cờ isBanned=True nhưng chưa cấu hình UNBAN_EMAIL, bỏ qua.", flush=True)
                return
            print(f"[{self.name}] ⚠️ Tài khoản đang bị gắn cờ isBanned=True. Đang gửi đơn Unban với email: {self.unban_email}...", flush=True)
            try:
                r = requests.post(
                    f"{self.base_url}/request_unban",
                    headers=self.headers,
                    json={"email": self.unban_email},
                    timeout=15
                )
                print(f"[{self.name}] Kết quả gửi đơn Unban ({self.unban_email}): {r.text}", flush=True)
            except Exception as e:
                print(f"[{self.name}] Lỗi gửi đơn Unban: {e}", flush=True)

    def try_adsgram_activation(self):
        """Gửi request phân phối Adsgram để kích hoạt ca khai thác khi có quảng cáo"""
        try:
            url = "https://api.adsgram.ai/adv"
            params = {
                "blockId": "58541",
                "tg_id": str(self.uid),
                "platform": "android"
            }
            h = {
                "Referer": "https://app9006949357.tgcloud.ai/",
                "Origin": "https://app9006949357.tgcloud.ai",
                "User-Agent": "Mozilla/5.0 (Linux; Android 12; Pixel 6) AppleWebKit/537.36"
            }
            r = requests.get(url, params=params, headers=h, timeout=10)
            if r.status_code == 200:
                print(f"[{self.name}] 🎉 Adsgram trả về quảng cáo khả dụng! Đang nhận ca đào...", flush=True)
            else:
                err = r.json().get("error", "unknown")
                print(f"[{self.name}] Adsgram status: {err}", flush=True)
        except Exception as e:
            print(f"[{self.name}] Adsgram check error: {e}", flush=True)

    def run(self):
        print(f"\n⛏️ [{self.name}] Bắt đầu kiểm tra & thu thập tài nguyên...", flush=True)
        profile = self.get_firebase_profile()
        if not profile:
            print(f"[{self.name}] Chưa có dữ liệu tài khoản trên Bé Thợ Mỏ.", flush=True)
            return

        gold = profile.get("gold", 0)
        diamonds = profile.get("diamonds", 0)
        level = profile.get("level", 1)
        work_end = profile.get("workEndTime", 0)
        is_banned = profile.get("isBanned", False)
        now_ms = int(time.time() * 1000)

        print(f"[{self.name}] 📊 Level: {level} | Vàng: {gold:,} (~{gold * 0.0005:,.1f} VNĐ) | KC: {diamonds:,} | Bị khóa: {is_banned}", flush=True)
        print(f"[{self.name}] 🔒 QUY TẮC: TUYỆT ĐỐI KHÔNG ĐỔI VÀNG SANG KIM CƯƠNG. BẢO TOÀN 100% VÀNG ĐỂ RÚT TIỀN MẶT!", flush=True)

        if not self.refresh_init_data():
            print(f"[{self.name}] Bỏ qua vì không lấy được WebApp initData.", flush=True)
            return

        # 1. Gửi unban nếu tài khoản bị gắn cờ
        if is_banned:
            self.request_unban_if_needed(profile)

        # 2. Nhận thưởng Referral
        self.claim_referral()

        # 3. Hoàn thành & nhận task cộng đồng
        completed = profile.get("completedTasks", {})
        self.claim_tasks(completed)

        # 4. Kiểm tra ca đào
        if now_ms >= work_end:
            print(f"[{self.name}] Ca đào đã hết hạn. Đang kiểm tra quảng cáo phân phối...", flush=True)
            self.try_adsgram_activation()
        else:
            remaining_min = (work_end - now_ms) // 60000
            print(f"[{self.name}] Ca khai thác đang hoạt động. Còn lại: {remaining_min} phút.", flush=True)

        print(f"[{self.name}] ✅ Hoàn tất lượt kiểm tra.", flush=True)
