from http.server import HTTPServer, BaseHTTPRequestHandler
from src.rate_limiter import TokenBucketRateLimiter, SlidingWindowRateLimiter
from src.distributed_sliding_window import DistributedSlidingWindowRateLimiter
from src.distributed_token_bucket import DistributedTokenBucketRateLimiter
from src.config import REDIS_HOST, REDIS_PORT
from urllib.parse import urlparse, parse_qs
import time
import json

# Local Sliding Window: 5 requests per 10 seconds
local_sliding = SlidingWindowRateLimiter(max_requests=5, window_seconds=10)

# Local Token Bucket: 5 tokens, refills 5 per minute
local_bucket = TokenBucketRateLimiter(capacity=5, refill_rate=5/60)

# Distributed Sliding Window: 5 requests per 10 second window (requires mini-redis)
distributed_sliding = DistributedSlidingWindowRateLimiter(
    max_requests=5, window_seconds=10
)

# Distributed Token Bucket: 5 tokens, refills 1 per second (requires mini-redis)
distributed_bucket = DistributedTokenBucketRateLimiter(
    capacity=5, refill_rate=1
)

def calc(params):
    a = float(params["a"][0])
    b = float(params["b"][0])
    op = params.get("op", ["+"])[0].strip() or "+"
    if op == "+":
        result = a + b
    elif op == "-":
        result = a - b
    elif op == "*":
        result = a * b
    elif op == "/":
        if b == 0:
            raise ValueError("Division by zero")
        result = a / b
    else:
        raise ValueError(f"Unknown operator: {op}")
    return {"a": a, "op": op, "b": b, "result": result}

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urlparse(self.path)
        user_id = self.client_address[0]
        current_time = time.time()
        params = parse_qs(parsed.query)

        if parsed.path == "/local/sliding":
            if not local_sliding.is_allowed(user_id, current_time):
                self.send_error_json(429, "Rate limit exceeded (local sliding window).")
                return
            self.handle_calc(params)
            return

        if parsed.path == "/local/bucket":
            if not local_bucket.is_allowed(user_id, current_time):
                self.send_error_json(429, "Rate limit exceeded (local token bucket).")
                return
            self.handle_calc(params)
            return

        if parsed.path == "/distributed/sliding":
            if not distributed_sliding.is_allowed(user_id):
                self.send_error_json(429, "Rate limit exceeded (distributed sliding window).")
                return
            self.handle_calc(params)
            return

        if parsed.path == "/distributed/bucket":
            if not distributed_bucket.is_allowed(user_id):
                self.send_error_json(429, "Rate limit exceeded (distributed token bucket).")
                return
            self.handle_calc(params)
            return

        self.send_error_json(404, "Not found. Use /local/sliding, /local/bucket, /distributed/sliding, /distributed/bucket")

    def handle_calc(self, params):
        try:
            result = calc(params)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        except (KeyError, IndexError):
            self.send_error_json(400, "Provide a, b, and optional op (+,-,*,/)")
        except ValueError as e:
            self.send_error_json(400, str(e))

    def send_error_json(self, code, message):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode())

    def log_message(self, _format, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]} → {args[1]}")

print("Server running on http://localhost:8080")
print("\nEndpoints (all with calculator API: ?a=10&b=3&op=+):")
print("  /local/sliding       — Local sliding window (5 req / 10 sec)")
print("  /local/bucket        — Local token bucket (5 tokens, refill 5/min)")
print("  /distributed/sliding — Distributed sliding window (5 req / 10 sec)")
print("  /distributed/bucket  — Distributed token bucket (5 tokens, refill 1/sec)")
print("\nops: + - * /")
print("Distributed endpoints need mini-redis on port 6380\n")
HTTPServer(("", 8080), Handler).serve_forever()
