import time
from app.metrics import RATE_LIMIT_BREACHES

# In-memory store: user_id → last_request_timestamp
last_request_time = {}
THROTTLE_COOLDOWN = 1

# This says: you cannot have more than 1 request per THROTTLE_COOLDOWN
def is_throttled(user_id: str) -> bool:
    now = time.time()
    last_time = last_request_time.get(user_id)

    if last_time and (now - last_time) < THROTTLE_COOLDOWN:
        RATE_LIMIT_BREACHES.labels(user_id=user_id).inc()
        return True

    # Update last request time
    last_request_time[user_id] = now
    return False
