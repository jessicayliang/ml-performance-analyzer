from .metrics import QUEUE_SIZE
import time

request_queue = {}

async def queue_simulation_middleware(request, call_next):
    if request.url.path == "/generate":
        request_id = id(request)
        request_queue[request_id] = time.time()
        QUEUE_SIZE.inc()

    response = await call_next(request)
    return response
