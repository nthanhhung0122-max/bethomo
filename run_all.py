import json
import time
import random
import os
import requests
from bot import BeThoMoBot

GITHUB_TOKEN = os.getenv("GH_PAT")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "nthanhhung0122-max/bethomo")
RUNNER_TIMEOUT_SECONDS = 5 * 3600  # Chạy 5 tiếng mỗi runner
LOOP_DELAY_SECONDS = 300  # 5 phút quét lặp lại 1 lần cho cả 3 acc

def load_accounts():
    """Đọc danh sách tài khoản. Session/api_hash chỉ lấy từ secret, không từ file public."""
    raw = os.getenv("TELEGRAM_ACCOUNTS_JSON")
    if raw:
        return json.loads(raw)["accounts"]
    for path in ("accounts.local.json", "accounts.json"):
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)["accounts"]
    raise FileNotFoundError("Không có TELEGRAM_ACCOUNTS_JSON và không tìm thấy accounts.local.json")

def trigger_next_runner():
    """Kích hoạt ca trực tiếp theo trên GitHub Actions trước khi runner này hết giờ (Handover Chaining 24/7)"""
    if not GITHUB_TOKEN:
        print("[Handover] Thiếu secret GH_PAT. GITHUB_TOKEN mặc định không tạo được workflow run mới nên 24/7 sẽ dừng sau ca này.", flush=True)
        return
    url = f"https://api.github.com/repos/{GITHUB_REPOSITORY}/actions/workflows/auto_run.yml/dispatches"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    try:
        r = requests.post(url, json={"ref": "main"}, headers=headers, timeout=20)
        if r.status_code in [200, 204]:
            print("🚀 [Handover Chaining 24/7] Đã kích hoạt ca runner tiếp theo thành công!", flush=True)
        else:
            print(f"⚠️ [Handover] Trigger thất bại ({r.status_code}): {r.text}", flush=True)
    except Exception as e:
        print(f"❌ [Handover Error]: {e}", flush=True)

def main():
    print("===================================================", flush=True)
    print("🔥 BẮT ĐẦU CHẠY BÉ THỢ MỎ 24/7 (ACC 1, 2, 4) 🔥", flush=True)
    print("===================================================", flush=True)

    start_time = time.time()

    while True:
        elapsed = time.time() - start_time
        if elapsed >= RUNNER_TIMEOUT_SECONDS:
            trigger_next_runner()
            print("Hoàn thành ca trực 5 tiếng. Nhường lại cho ca runner mới!", flush=True)
            break

        try:
            accs = load_accounts()
        except Exception as e:
            print(f"Lỗi đọc danh sách tài khoản: {e}", flush=True)
            break

        missing = [a["name"] for a in accs if not a.get("session_str")]
        if missing:
            print(f"Thiếu session_str cho: {', '.join(missing)}. Kiểm tra secret TELEGRAM_ACCOUNTS_JSON.", flush=True)
            break

        print(f"\n--- [{time.strftime('%Y-%m-%d %H:%M:%S')}] BẮT ĐẦU VÒNG QUÉT TẤT CẢ TÀI KHOẢN ---", flush=True)
        for acc in accs:
            BeThoMoBot(acc).run()
            delay = random.uniform(3, 7)
            print(f"Nghỉ {delay:.1f}s trước tài khoản tiếp theo...", flush=True)
            time.sleep(delay)

        print(f"💤 Hoàn tất vòng quét. Nghỉ {LOOP_DELAY_SECONDS // 60} phút trước chu kỳ kế tiếp...\n", flush=True)
        time.sleep(LOOP_DELAY_SECONDS)

if __name__ == '__main__':
    main()
