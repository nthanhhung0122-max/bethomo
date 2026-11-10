import json, time, random, os, requests
from bot import BeThoMoBot
def main():
    print('=== SUPERVISOR BÉ THỢ MỎ 24/7 (ACC 1, 2, 4) ===')
    with open('accounts.json', 'r', encoding='utf-8') as f:
        accs = json.load(f)['accounts']
    for acc in accs:
        BeThoMoBot(acc).run()
        time.sleep(random.uniform(2, 5))
if __name__ == '__main__':
    main()
