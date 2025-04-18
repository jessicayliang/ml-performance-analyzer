import time
from fastapi import FastAPI, Request
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.models import PromptRequest
from app.llm_engine import generate_text
from app.metrics import *
from app.monitoring import start_metrics_updater, update_resource_metrics
from app.middleware import queue_simulation_middleware

app = FastAPI()
app.middleware("http")(queue_simulation_middleware)

# In-memory session store: user_id -> list of messages
chat_histories = {}

@app.post("/generate")
async def generate(request: PromptRequest):
    start_time = time.time()
    QUEUE_SIZE.dec()

    try:
        ttft_start = time.time()

        user_id = request.user_id
        user_prompt = request.prompt

        # Initialize chat history if not present
        history = chat_histories.setdefault(user_id, [])

        # Ensure a system prompt is at the start
        if not any(m["role"] == "system" for m in history):
            history.insert(0, {"role": "system", "content": "You are a helpful assistant."})

        # Add current user message
        history.append({"role": "user", "content": user_prompt})

        # Generate assistant reply based on full history
        response_text, input_tokens, output_tokens = generate_text(
            messages=history,
            max_tokens=request.max_tokens,
            temperature=request.temperature,
            top_p=request.top_p
        )

        ttft_end = time.time()

        # Append model's response to the history
        history.append({"role": "assistant", "content": response_text})

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
