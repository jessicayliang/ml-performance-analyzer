from fastapi import FastAPI, Request
from pydantic import BaseModel
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import torch
import os
import time
from prometheus_client import Counter, Histogram, Gauge, Summary, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
import psutil
import GPUtil
import threading

MODEL_ID = "Qwen/Qwen2.5-0.5B"
HF_TOKEN = os.getenv("HF_TOKEN", None)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
llm = LLM(model=MODEL_ID, dtype=torch.float16)

# ---- FastAPI App Setup ----
app = FastAPI()

# ---- Request Model ----
class PromptRequest(BaseModel):
    prompt: str
    max_tokens: int = 256
    temperature: float = 0.7
    top_p: float = 0.95

# ---- Prometheus Metrics ----
# Latency metrics
REQUEST_LATENCY = Histogram('llm_request_latency_seconds', 'Time spent processing entire request',
                            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0])
TIME_TO_FIRST_TOKEN = Histogram('llm_time_to_first_token_seconds', 'Time from request to first token generation',
                                buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0])

# Throughput metrics
REQUEST_COUNT = Counter('llm_request_count', 'Total number of requests')
TOKENS_GENERATED = Counter('llm_tokens_generated_total', 'Total number of tokens generated')
TOKENS_INPUT = Counter('llm_tokens_input_total', 'Total number of input tokens processed')

# Error metrics
ERROR_COUNT = Counter('llm_error_count', 'Total number of failed requests')
ERROR_TYPES = Counter('llm_error_types', 'Types of errors', ['error_type'])

# Resource usage metrics
GPU_MEMORY_USAGE = Gauge('llm_gpu_memory_usage_bytes', 'GPU memory usage in bytes')
CPU_USAGE_PERCENT = Gauge('llm_cpu_usage_percent', 'CPU usage percentage')
RAM_USAGE_BYTES = Gauge('llm_ram_usage_bytes', 'RAM usage in bytes')

# Token usage metrics
TOKEN_LENGTH_INPUT = Histogram('llm_token_length_input', 'Distribution of input token lengths',
                               buckets=[10, 50, 100, 250, 500, 1000, 2000])
TOKEN_LENGTH_OUTPUT = Histogram('llm_token_length_output', 'Distribution of output token lengths',
                                buckets=[10, 50, 100, 250, 500, 1000, 2000])

# Queue metrics
QUEUE_TIME = Histogram('llm_queue_time_seconds', 'Time spent in queue before processing',
                       buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0])
QUEUE_SIZE = Gauge('llm_queue_size', 'Current number of requests in queue')

# Rate limiting metrics
RATE_LIMIT_BREACHES = Counter('llm_rate_limit_breaches', 'Number of rate limit breaches', ['user_id'])
THROTTLING_INCIDENTS = Counter('llm_throttling_incidents', 'Number of throttling incidents')

# Global variables to track queue information
# In a real system, this would be tied to your actual request queue
request_queue = {}

# ---- Endpoint ----
@app.post("/generate")
async def generate_text(request: PromptRequest):
    request_id = id(request)
    start_time = time.time()

    # Track queue time (example - in real system this would be actual queue time)
    queue_start_time = time.time() - 0.1  # Simulating a small queue time
    QUEUE_TIME.observe(start_time - queue_start_time)

    # Update queue size
    QUEUE_SIZE.dec()  # Simulating removal from queue

    error_occurred = False

    try:
        # Count input tokens
        input_tokens = tokenizer.encode(request.prompt)
        input_token_count = len(input_tokens)
        TOKEN_LENGTH_INPUT.observe(input_token_count)
        TOKENS_INPUT.inc(input_token_count)

        # Generate text
        ttft_start = time.time()
        sampling_params = SamplingParams(
            temperature=request.temperature,
            top_p=request.top_p,
            max_tokens=request.max_tokens,
        )
        outputs = llm.generate([request.prompt], sampling_params)
        ttft_end = time.time()
        TIME_TO_FIRST_TOKEN.observe(ttft_end - ttft_start)

        response_text = outputs[0].outputs[0].text

        # Count output tokens
        output_tokens = tokenizer.encode(response_text)
        output_token_count = len(output_tokens)
        TOKEN_LENGTH_OUTPUT.observe(output_token_count)
        TOKENS_GENERATED.inc(output_token_count)

        # Increment request counter
        REQUEST_COUNT.inc()

        return {"output": response_text}
    except Exception as e:
        # Track errors
        error_occurred = True
        ERROR_COUNT.inc()
        ERROR_TYPES.labels(error_type=type(e).__name__).inc()
        raise e

    finally:
        # Record total request latency
        REQUEST_LATENCY.observe(time.time() - start_time)

        # Update resource usage metrics (done in background for all requests)
        update_resource_metrics()

def update_resource_metrics():
    """Update system resource metrics"""
    # CPU usage
    CPU_USAGE_PERCENT.set(psutil.cpu_percent())

    # RAM usage
    RAM_USAGE_BYTES.set(psutil.virtual_memory().used)

    # GPU usage if available
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            # Just using the first GPU for this example
            GPU_MEMORY_USAGE.set(gpus[0].memoryUsed * 1024 * 1024)  # Convert to bytes
    except:
        # Graceful degradation if GPUtil is not available
        pass

# Background thread to regularly update resource metrics
def metrics_updater():
    while True:
        update_resource_metrics()
        time.sleep(5)  # Update every 5 seconds

# ---- Metrics Endpoint ----
@app.get("/metrics")
async def metrics():
    """Endpoint for exposing Prometheus metrics"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

# ---- Queue simulation for metrics ----
@app.middleware("http")
async def queue_simulation_middleware(request: Request, call_next):
    # Simple queue simulation for metrics
    if request.url.path == "/generate":
        request_id = id(request)
        request_queue[request_id] = time.time()
        QUEUE_SIZE.inc()

    response = await call_next(request)

    return response

# ---- Optional: Health Check ----
@app.get("/")
def root():
    return {"status": "Model is ready"}

# Start the background metrics updater
metrics_thread = threading.Thread(target=metrics_updater, daemon=True)
metrics_thread.start()