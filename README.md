# Rate Limiter

A rate limiter implementation from scratch in Python — no external libraries used.

Built as part of a series of open-source system design projects.

## Algorithms Implemented

### 1. Sliding Window
Tracks exact timestamps of requests per user in a circular buffer. Blocks requests if count exceeds the limit within the time window.

- Accurate request counting
- Higher memory usage (stores every timestamp)
- Best for: payment gateways, strict API quotas

### 2. Token Bucket
Each user gets a bucket of tokens. Tokens refill at a fixed rate. Each request consumes one token.

- Allows bursting (multiple requests at once if tokens available)
- Low memory usage (stores only 2 values per user)
- Best for: public APIs, Nginx, GitHub, Twitter

## Data Structures (built from scratch)

- **HashMap** — array of buckets, hash function with chaining for collision handling
- **CircularBuffer** — fixed-size buffer with head/tail pointers and wrap-around

## Project Structure

```
rate-limiter/
├── src/
│   ├── hash_map.py          # HashMap implementation
│   ├── circular_buffer.py   # CircularBuffer implementation
│   └── rate_limiter.py      # SlidingWindowRateLimiter, TokenBucketRateLimiter
├── tests/
│   └── test.py              # Unit tests
├── demo.py                  # HTTP server demo (calculator API with rate limiting)
└── requirements.txt
```

## Usage

```python
from src.rate_limiter import SlidingWindowRateLimiter, TokenBucketRateLimiter

# Allow 5 requests per 60 seconds
limiter = SlidingWindowRateLimiter(max_requests=5, window_seconds=60)
limiter.is_allowed("user1", current_time)  # True / False

# 10 token capacity, refills 1 token/sec
limiter = TokenBucketRateLimiter(capacity=10, refill_rate=1)
limiter.is_allowed("user1", current_time)  # True / False
```

## Run Tests

```bash
python3 -m unittest tests.test -v
```

## Demo Server

A calculator API protected by the token bucket rate limiter (5 requests/minute):

```bash
python3 demo.py
curl 'http://localhost:8080?a=10&b=3&op=*'
```

Supported operators: `+` `-` `*` `/`

After 5 requests, returns `429 Rate limit exceeded`.
