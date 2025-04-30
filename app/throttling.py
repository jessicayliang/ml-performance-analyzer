import time
from collections import deque
from app.metrics import RATE_LIMIT_BREACHES

# In-memory store: user_id to deque of timestamps
# Here, we can send at most MAX_REQUESTS requests per THROTTLE_WINDOW seconds
request_timestamps = {}
THROTTLE_WINDOW = 10  # seconds
MAX_REQUESTS = 3

def is_throttled(user_id: str, model: str) -> bool:
    now = time.time()
    timestamps = request_timestamps.get(user_id, deque())

    # Remove timestamps older than the throttle window
    while timestamps and now - timestamps[0] > THROTTLE_WINDOW:
        timestamps.popleft()

    if len(timestamps) >= MAX_REQUESTS:
        RATE_LIMIT_BREACHES.labels(user_id=user_id, model=model).inc()
        return True

    # Add the current timestamp and update the store
    timestamps.append(now)
    request_timestamps[user_id] = timestamps
    return False
