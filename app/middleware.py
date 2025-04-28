from app.metrics import QUEUE_SIZE, QUEUE_TIME
import time

request_queue = {}

async def queue_simulation_middleware(request, call_next):
    if request.url.path != "/generate":
        return await call_next(request)

    request_id = id(request)
    request_queue[request_id] = time.time()
    QUEUE_SIZE.inc()

    try:
        response = await call_next(request)
        return response

    finally:
        start_ts = request_queue.pop(request_id, None)
        if start_ts is not None:
            elapsed = time.time() - start_ts
            QUEUE_TIME.observe(elapsed)
        QUEUE_SIZE.dec()
