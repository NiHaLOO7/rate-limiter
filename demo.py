from http.server import HTTPServer, BaseHTTPRequestHandler
from src.rate_limiter import TokenBucketRateLimiter
from urllib.parse import urlparse, parse_qs
import time
import json

# 5 tokens max, refills 5 per minute (5/60 per second)
limiter = TokenBucketRateLimiter(capacity=5, refill_rate=5/60)

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        user_id = self.client_address[0]
        current_time = time.time()

        if not limiter.is_allowed(user_id, current_time):
            self.send_response(429)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Rate limit exceeded. Try again later."}).encode())
            return

        params = parse_qs(urlparse(self.path).query)

        try:
            a = float(params["a"][0])
            b = float(params["b"][0])
            op = params.get("op", ["+"])[0]

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

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"a": a, "op": op, "b": b, "result": result}).encode())

        except (KeyError, IndexError):
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Provide a, b, and optional op (+,-,*,/)"}).encode())
        except ValueError as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def log_message(self, _format, *args):
        print(f"[{time.strftime('%H:%M:%S')}] {args[0]} → {args[1]}")

print("Server running on http://localhost:8080")
print("Usage: curl 'http://localhost:8080?a=10&b=3&op=+'")
print("ops: + - * /")
print("5 requests per minute per IP\n")
HTTPServer(("", 8080), Handler).serve_forever()
