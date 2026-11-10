import json
import time
import random
import os
import requests
from bot import BeThoMoBot

GITHUB_TOKEN = os.getenv("GH_PAT") or os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY", "nthanhhung0122-max/bethomo")
RUNNER_TIMEOUT_SECONDS = 5 * 3600  # Chạy 5 tiếng mỗi runner
LOOP_DELAY_SECONDS = 300  # 5 phút quét lặp lại 1 lần cho cả 3 acc

def trigger_next_runner():
    """Kích hoạt ca trực tiếp theo trên GitHub Actions trước khi runner này hết giờ (Handover Chaining 24/7)"""
    if not GITHUB_TOKEN:
        print("[Handover] Không tìm thấy GITHUB_TOKEN, bỏ qua trigger.", flush=True)
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
            with open('accounts.json', 'r', encoding='utf-8') as f:
                accs = json.load(f)['accounts']
        except Exception as e:
            print(f"Lỗi đọc accounts.json: {e}", flush=True)
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
