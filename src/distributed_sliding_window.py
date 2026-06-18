from src.redis_client import RedisClient
from src.config import REDIS_HOST, REDIS_PORT
import threading
import time

class DistributedSlidingWindowRateLimiter:
    def __init__(self, max_requests, window_seconds, host = REDIS_HOST, port = REDIS_PORT):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.redis = RedisClient(host, port)
        self.cleanup_redis = RedisClient(host, port) 
        self.active_keys = set()
        threading.Thread(target=self._cleanup_loop, daemon=True).start()

    def _cleanup(self):
        now = int(time.time() * 1000)
        for key in list(self.active_keys):
            response = self.cleanup_redis.lrange(key, "0", "-1")
            valid = [int(a) for a in response if int(a) >= (now-(self.window_seconds * 1000))]
            if valid:
                self.cleanup_redis.ltrim(key, "0", str(len(valid) - 1))
            else:
                self.active_keys.discard(key)
    
    def _cleanup_loop(self):
        while True:
            time.sleep(self.window_seconds);
            self._cleanup()

    def is_allowed(self, client_id):
        key = f"rate:{client_id}"
        self.active_keys.add(key)
        now = int(time.time() * 1000)
        self.redis.lpush(key, str(now))
        response = self.redis.lrange(key, "0", "-1")
        valid = [int(a) for a in response if int(a) >= (now-(self.window_seconds * 1000))]
        return len(valid) <= self.max_requests

