from src.redis_client import RedisClient
from src.config import REDIS_HOST, REDIS_PORT
import time

class DistributedTokenBucketRateLimiter:
    def __init__(self, capacity, refill_rate, host = REDIS_HOST, port = REDIS_PORT):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.redis = RedisClient(host, port)


    def is_allowed(self, client_id):
        allowed = False
        keys = [f"bucket:{client_id}:tokens", f"bucket:{client_id}:last_refill"]
        tokens = self.redis.get(keys[0])
        last_refill = self.redis.get(keys[1])
        now = time.time()
        tokens = self.capacity if tokens == None else float(tokens)
        last_refill = now if last_refill == None else float(last_refill)
        elapsed = now - last_refill
        tokens = min((tokens + (elapsed * self.refill_rate)), self.capacity)
        if tokens >= 1:
            tokens -= 1
            allowed = True
        self.redis.set(keys[0], str(tokens))
        self.redis.set(keys[1], str(now))
        return allowed
        
