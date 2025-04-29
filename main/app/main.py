import time
import threading
from collections import defaultdict
from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from starlette.responses import Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from app.llm_engine import generate_text
from app.metrics import *
from app.monitoring import start_metrics_updater, update_resource_metrics
from app.middleware import queue_simulation_middleware
from app.throttling import is_throttled

MAX_HISTORY_MESSAGES = 20

app = FastAPI()
app.middleware("http")(queue_simulation_middleware)

# In-memory session store: user_id -> list of messages
chat_histories = {}

# Track active users and their session lengths
active_users = set()
user_message_counts = defaultdict(int)
last_user_activity = {}
MAX_CONTEXT_LENGTH = 4096  # Adjust based on your model's context window

class PromptRequest(BaseModel):
    user_id: str
    prompt: str
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

        # Update user metrics
        active_users.add(user_id)
        user_message_counts[user_id] += 1
        last_user_activity[user_id] = time.time()

        # Check for throttling
        if is_throttled(user_id):
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
            top_p=request.top_p
        )

        ttft_end = time.time()

        # After generating the response:
        # Calculate context length utilization
        total_context_length = len(input_tokens) + len(output_tokens)
        if MAX_CONTEXT_LENGTH and MAX_CONTEXT_LENGTH > 0:
            context_utilization = total_context_length / MAX_CONTEXT_LENGTH
        else:
            # Default to a reasonable value if MAX_CONTEXT_LENGTH is not defined
            context_utilization = total_context_length / 4096  # Using 4096 as fallback value
        CONTEXT_LENGTH_UTILIZATION.observe(context_utilization)

        # Append model's response to the history
        history.append({"role": "assistant", "content": response_text})

        # Truncate history before generating
        if len(history) > MAX_HISTORY_MESSAGES:
            system_prompt = [history[0]]
            trimmed_history = history[1:][-MAX_HISTORY_MESSAGES:]  # trim after system
            history = system_prompt + trimmed_history

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

# Add a background task to clean up inactive users (optional)
def clean_inactive_users():
    def _loop():
        while True:
            current_time = time.time()
            inactive_threshold = 3600  # 1 hour

            inactive_users = [
                user_id for user_id, last_time in last_user_activity.items()
                if current_time - last_time > inactive_threshold
            ]

            for user_id in inactive_users:
                active_users.discard(user_id)
                user_message_counts.pop(user_id, None)
                last_user_activity.pop(user_id, None)

            time.sleep(300)  # Check every 5 minutes

    thread = threading.Thread(target=_loop, daemon=True)
    thread.start()

# Initialize metrics with default values on startup
def initialize_context_metric():
    # Add initial observation for context length utilization
    CONTEXT_LENGTH_UTILIZATION.observe(0.0)

start_metrics_updater()
initialize_context_metric()
clean_inactive_users()