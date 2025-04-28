import time
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.llm_engine import generate_text
from app.metrics import *
from app.monitoring import start_metrics_updater, update_resource_metrics
from app.middleware import queue_simulation_middleware
from app.throttling import is_throttled

MAX_HISTORY_MESSAGES = 7

app = FastAPI()
app.middleware("http")(queue_simulation_middleware)

# In-memory session store: user_id -> list of messages
chat_histories = {}

class PromptRequest(BaseModel):
    user_id: str
    prompt: str
    model: str = "llama"
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.95

@app.post("/generate")
async def generate(request: PromptRequest):
    start_time = time.time()

    try:
        ttft_start = time.time()

        user_id = request.user_id
        user_prompt = request.prompt
        model = request.model

        # Check for throttling
        if is_throttled(user_id, model):
            raise HTTPException(status_code=429, detail="Too many requests. Please wait before trying again.")

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
            top_p=request.top_p,
            model=model
        )

        ttft_end = time.time()

        # Append model's response to the history
        history.append({"role": "assistant", "content": response_text})

        # Truncate history before generating
        if len(history) > MAX_HISTORY_MESSAGES:
            system_prompt = [history[0]]
            trimmed_history = history[1:][-MAX_HISTORY_MESSAGES:]  # trim after system
            history = system_prompt + trimmed_history

        # Log metrics
        REQUEST_LATENCY.labels(user_id=user_id, model=model).observe(time.time() - start_time)
        TIME_TO_FIRST_TOKEN.labels(user_id=user_id, model=model).observe(ttft_end - ttft_start)
        REQUEST_COUNT.labels(user_id=user_id, model=model).inc()
        TOKENS_INPUT.labels(user_id=user_id, model=model).inc(len(input_tokens))
        TOKENS_GENERATED.labels(user_id=user_id, model=model).inc(len(output_tokens))
        TOKEN_LENGTH_INPUT.observe(len(input_tokens))
        TOKEN_LENGTH_OUTPUT.observe(len(output_tokens))

        return {"output": response_text}

    except HTTPException as http_exc:
        ERROR_COUNT.labels(user_id=user_id, model=model).inc()
        ERROR_TYPES.labels(error_type=f"HTTP_{http_exc.status_code}", model=model).inc()
        raise http_exc

    except Exception as e:
        ERROR_COUNT.labels(user_id=user_id, model=model).inc()
        ERROR_TYPES.labels(error_type=type(e).__name__, model=model).inc()
        raise e

@app.get("/metrics")
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

@app.get("/")
def health():
    return {"status": "Model is ready"}

start_metrics_updater()
