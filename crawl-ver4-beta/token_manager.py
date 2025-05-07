import time
import requests
import threading
import logging

logging.basicConfig(level=logging.INFO)

class TokenManager:
    def __init__(self, tokens, cache_timeout=120):
        self.tokens = tokens
        self.token_usage = {
            t: {"remaining": 1, "reset_time": 0, "cache_time": 0, "disabled": False}
            for t in tokens
        }
        self.cache_timeout = cache_timeout
        self.lock = threading.Lock()

    def get_token(self):
        with self.lock:
            usable_tokens = [
                t for t in self.tokens
                if not self.token_usage[t]["disabled"] and self._is_usable(t)
            ]

            if usable_tokens:
                # Chọn token còn nhiều quota nhất
                best_token = max(usable_tokens, key=lambda t: self.token_usage[t]["remaining"])
                return best_token

            self._wait_for_reset()
            return self.get_token()

    def _is_usable(self, token):
        if not self._is_cache_valid(token):
            self._update_token_usage(token)
        return self.token_usage[token]["remaining"] > 0

    def _is_cache_valid(self, token):
        return time.time() - self.token_usage[token]["cache_time"] < self.cache_timeout

    def _update_token_usage(self, token):
        try:
            resp = requests.get(
                "https://api.github.com/rate_limit",
                headers={"Authorization": f"token {token}"}
            )
            if resp.ok:
                core = resp.json()["resources"]["core"]
                self.token_usage[token].update({
                    "remaining": core["remaining"],
                    "reset_time": core["reset"],
                    "cache_time": time.time(),
                })
            else:
                logging.warning(f"[TokenManager] Failed to check token ({resp.status_code}). Disabling.")
                self.token_usage[token]["disabled"] = True
        except Exception as e:
            logging.warning(f"[TokenManager] Error checking token: {e}")
            self.token_usage[token]["disabled"] = True

    def _wait_for_reset(self):
        soonest = min(
            (t["reset_time"] for t in self.token_usage.values() if not t["disabled"]),
            default=time.time() + 60  # fallback: wait 1 phút
        )
        wait = soonest - time.time()
        if wait > 0:
            logging.info(f"⏳ Waiting {wait:.1f}s for token reset...")
            time.sleep(wait + 1)
