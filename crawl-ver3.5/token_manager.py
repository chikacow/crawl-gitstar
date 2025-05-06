import os
import time
import requests
from dotenv import load_dotenv
load_dotenv()

class TokenManager:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_token_index = 0
        self.token_usage = {token: {"count": 0, "reset_time": 0} for token in tokens}

    def get_token(self):
        for _ in range(len(self.tokens)):
            token = self.tokens[self.current_token_index]
            self.current_token_index = (self.current_token_index + 1) % len(self.tokens)

            if self.is_token_usable(token):
                return token
            else:
                print(f"⚠ Token hết quota, thử token tiếp theo...")

        self.wait_for_reset()
        return self.get_token()

    def is_token_usable(self, token):
        headers = {"Authorization": f"token {token}"}
        url = "https://api.github.com/rate_limit"
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                remaining = data["resources"]["core"]["remaining"]
                reset_time = data["resources"]["core"]["reset"]
                self.token_usage[token] = {"count": 5000 - remaining, "reset_time": reset_time}
                return remaining > 0
        except Exception as e:
            print(f"✘ Error checking token: {e}")
        return False

    def wait_for_reset(self):
        reset_times = [v["reset_time"] for v in self.token_usage.values()]
        sleep_time = min(reset_times) - time.time()
        if sleep_time > 0:
            print(f"⏳ Tất cả token hết quota. Chờ {sleep_time:.2f} giây...")
            time.sleep(sleep_time + 1)

def github_token_manager():
    tokens = []
    i = 1
    while True:
        token = os.getenv(f"GITHUB_TOKEN_{i}")
        if not token:
            break
        tokens.append(token)
        i += 1
    return tokens
