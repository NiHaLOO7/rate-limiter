from src.rate_limiter import SlidingWindowRateLimiter, TokenBucketRateLimiter
import unittest

class TestRateLimiter(unittest.TestCase):
    
    def testSlidingWindow(self):
        # Test 1: Sliding Window
        limiter = SlidingWindowRateLimiter(max_requests=3, window_seconds=10)
        self.assertTrue(limiter.is_allowed("user1", 1.0))   # True
        self.assertTrue(limiter.is_allowed("user1", 2.0))   # True
        self.assertTrue(limiter.is_allowed("user1", 3.0))   # True
        self.assertFalse(limiter.is_allowed("user1", 4.0))   # False
        self.assertTrue(limiter.is_allowed("user1", 15.0))  # True (window expire)


    def testTokenBucket(self):
        # Test 1: Sliding Window
        limiter = TokenBucketRateLimiter(capacity=3, refill_rate=1)
        self.assertTrue(limiter.is_allowed("user1", 1.0))   # True
        self.assertTrue(limiter.is_allowed("user1", 1.0))   # True
        self.assertTrue(limiter.is_allowed("user1", 1.0))   # True
        self.assertFalse(limiter.is_allowed("user1", 1.0))   # False
        self.assertTrue(limiter.is_allowed("user1", 3.0))  # True (window expire)

if __name__ == '__main__':
    unittest.main()