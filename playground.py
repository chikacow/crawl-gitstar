import requests
import time
import threading
from collections import deque
from functools import lru_cache

class TokenManager:
    def __init__(self, tokens, cache_timeout=60):
        """
        Khởi tạo TokenManager với danh sách các token GitHub.
        :param tokens: Danh sách các token.
        :param cache_timeout: Thời gian cache kết quả rate limit cho mỗi token.
        """
        self.tokens = tokens
        self.current_token_index = 0
        self.token_usage = {token: {"count": 0, "reset_time": 0} for token in tokens}
        self.cache_timeout = cache_timeout
        self.lock = threading.Lock()  # Để đồng bộ khi đa luồng

    @lru_cache(maxsize=None)
    def get_token(self):
        """
        Lấy token hợp lệ, nếu tất cả đều hết quota thì chờ đến khi reset.
        :return: Token GitHub còn usable.
        """
        with self.lock:
            # Dùng vòng lặp thay vì đệ quy để tránh stack overflow
            for _ in range(len(self.tokens)):
                token = self.tokens[self.current_token_index]
                self.current_token_index = (self.current_token_index + 1) % len(self.tokens)

                if self.is_token_usable(token):
                    return token
                else:
                    print(f"⚠ Token bị hết quota, thử token tiếp theo...")

            # Nếu tất cả token đều hết quota → chờ reset rồi thử lại
            self.wait_for_reset()
            return self.get_token()

    def is_token_usable(self, token):
        """
        Kiểm tra token còn usable không (còn quota). Nếu đã cache, dùng luôn thông tin cũ.
        """
        if not self.is_token_cache_valid(token):
            self.update_token_usage(token)

        remaining = self.token_usage[token]["remaining"]
        return remaining > 0

    def is_token_cache_valid(self, token):
        """
        Kiểm tra xem thông tin cache cho token có còn hợp lệ không.
        """
        return time.time() - self.token_usage[token]["cache_time"] < self.cache_timeout

    def update_token_usage(self, token):
        """
        Cập nhật thông tin quota cho token từ GitHub API.
        """
        headers = {"Authorization": f"token {token}"}
        url = "https://api.github.com/rate_limit"
        
        try:
            resp = requests.get(url, headers=headers)
            if resp.status_code == 200:
                data = resp.json()
                remaining = data.get("resources", {}).get("core", {}).get("remaining", 0)
                reset_time = data.get("resources", {}).get("core", {}).get("reset", 0)

                self.token_usage[token] = {
                    "remaining": remaining,
                    "reset_time": reset_time,
                    "cache_time": time.time()
                }
            else:
                print(f"✘ Error checking rate limit for token: {token}")
        except requests.RequestException as e:
            print(f"✘ Request error while checking token rate: {e}")

    def wait_for_reset(self):
        """
        Chờ đến khi token sớm nhất được reset.
        """
        reset_times = [self.token_usage[token]["reset_time"] for token in self.tokens]
        soonest_reset = min(reset_times)
        sleep_time = soonest_reset - time.time()
        if sleep_time > 0:
            print(f"⏳ Tất cả token hết quota. Đợi {sleep_time:.2f} giây để reset...")
            time.sleep(sleep_time + 1)  # Đợi dư 1 giây để chắc chắn
        else:
            print("✔ Token đã reset. Tiếp tục...")

    def check_rate_limit(self):
        """
        Kiểm tra xem tất cả token có đều hết quota không.
        :return: True nếu tất cả token hết quota, False nếu còn ít nhất 1 usable.
        """
        exhausted = 0
        for token in self.tokens:
            if not self.is_token_usable(token):
                exhausted += 1
        return exhausted == len(self.tokens)

# Demo usage
if __name__ == "__main__":
    tokens = ["your_token_1", "your_token_2", "your_token_3"]  # Example tokens
    token_manager = TokenManager(tokens)

    # Lấy token sử dụng
    token = token_manager.get_token()
    print(f"Đang sử dụng token: {token}")
