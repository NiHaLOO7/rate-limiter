from src.hash_map import HashMap
from src.circular_buffer import CircularBuffer


class SlidingWindowRateLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_windows = HashMap()

    def is_allowed(self, user_id, current_time):
        buffer = self.user_windows.get(user_id)
        if buffer is None:
            buffer = CircularBuffer(self.max_requests)
            self.user_windows.put(user_id, buffer)
        buffer.pop_older_than(current_time - self.window_seconds)
        if len(buffer) < self.max_requests:
            buffer.push(current_time)
            return True
        return False


class TokenBucketRateLimiter:
    def __init__(self, capacity, refill_rate):
        self.capacity = capacity
        self.refill_rate = refill_rate
        self.user_windows = HashMap()

    def is_allowed(self, user_id, current_time):
        bucket = self.user_windows.get(user_id)
        if bucket is None:
            tokens, last_refill_time = self.capacity, current_time
        else:
            tokens, last_refill_time = bucket
        elapsed_time = current_time - last_refill_time
        new_tokens = min((tokens + elapsed_time * self.refill_rate), self.capacity)
        if new_tokens >= 1:
            new_tokens -= 1
            self.user_windows.put(user_id, (new_tokens, current_time))
            return True
        return False
