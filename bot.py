import json, time, random, requests
class BeThoMoBot:
    def __init__(self, acc):
        self.name = acc['name']
        self.init_data = acc['init_data']
    def run(self):
        print(f'[{self.name}] Bắt đầu auto khai thác & claim thưởng...')
        time.sleep(random.uniform(2, 4))
        print(f'[{self.name}] Claim thành công!')
