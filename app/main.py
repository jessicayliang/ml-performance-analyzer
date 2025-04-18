from fastapi import FastAPI, Request
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from .models import PromptRequest
from .llm_engine import generate_text
from .metrics import *
from .monitoring import start_metrics_updater, update_resource_metrics
from .middleware import queue_simulation_middleware

app = FastAPI()

app.middleware("http")(queue_simulation_middleware)

@app.post("/generate")
async def generate(request: PromptRequest):
    start_time = time.time()
    QUEUE_SIZE.dec()  # simulate removal from queue

    try:
        ttft_start = time.time()
        response_text, input_tokens, output_tokens = generate_text(
            prompt=request.prompt,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )
        ttft_end = time.time()

        # Log metrics
        REQUEST_LATENCY.observe(time.time() - start_time)
        TIME_TO_FIRST_TOKEN.observe(ttft_end - ttft_start)
        REQUEST_COUNT.inc()
        TOKENS_INPUT.inc(len(input_tokens))
        TOKENS_GENERATED.inc(len(output_tokens))
        TOKEN_LENGTH_INPUT.observe(len(input_tokens))
        TOKEN_LENGTH_OUTPUT.observe(len(output_tokens))

        update_resource_metrics()
        return {"output": response_text}

    except Exception as e:
        ERROR_COUNT.inc()
        ERROR_TYPES.labels(error_type=type(e).__name__).inc()
        raise e

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def health():
    return {"status": "Model is ready"}

start_metrics_updater()
