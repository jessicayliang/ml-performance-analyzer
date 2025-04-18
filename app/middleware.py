from app.metrics import QUEUE_SIZE
import time

request_queue = {}

# To get metric for number of in-flight requests
async def queue_simulation_middleware(request, call_next):
    if request.url.path == "/generate":
        request_id = id(request)
        request_queue[request_id] = time.time()
        QUEUE_SIZE.inc()

        try:
            response = await call_next(request)
            return response
        finally:
            QUEUE_SIZE.dec()
            request_queue.pop(request_id, None)
    else:
        return await call_next(request)

