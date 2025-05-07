from prometheus_client import Counter, Histogram, Gauge

# Histograms (latency per user)
REQUEST_LATENCY = Histogram(
    'llm_request_latency_seconds',
    'Time spent processing entire request',
    ['user_id', 'model'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0]
)
TIME_TO_FIRST_TOKEN = Histogram(
    'llm_time_to_first_token_seconds',
    'Time to first token',
    ['user_id', 'model'],
    buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0]
)

# Counters (request and token counters per user)
REQUEST_COUNT = Counter(
    'llm_request_count',
    'Total number of requests',
    ['user_id', 'model']
)
TOKENS_GENERATED = Counter(
    'llm_tokens_generated_total',
    'Total number of tokens generated',
    ['user_id', 'model']
)
TOKENS_INPUT = Counter(
    'llm_tokens_input_total',
    'Total number of input tokens processed',
    ['user_id', 'model']
)
ERROR_COUNT = Counter(
    'llm_error_count',
    'Total number of failed requests',
    ['user_id', 'model']
)

# Counter for error types
ERROR_TYPES = Counter(
    'llm_error_types',
    'Types of errors',
    ['error_type', 'model']
)

# Histograms for token length
TOKEN_LENGTH_INPUT = Histogram(
    'llm_token_length_input',
    'Input token lengths',
    buckets=[10, 50, 100, 250, 500, 1000, 2000]
)
TOKEN_LENGTH_OUTPUT = Histogram(
    'llm_token_length_output',
    'Output token lengths',
    buckets=[10, 50, 100, 250, 500, 1000, 2000]
)

# Memory Usage
GPU_MEMORY_USAGE = Gauge(
    'llm_gpu_memory_usage_bytes',
    'GPU memory usage in bytes'
)
CPU_USAGE_PERCENT = Gauge(
    'llm_cpu_usage_percent',
    'CPU usage percentage'
)
RAM_USAGE_BYTES = Gauge(
    'llm_ram_usage_bytes',
    'RAM usage in bytes'
)

# Histogram for queue time
QUEUE_TIME = Histogram(
    'llm_queue_time_seconds',
    'Time in queue',
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0]
)

# Queue size
QUEUE_SIZE = Gauge(
    'llm_queue_size',
    'Current request queue size'
)

# Counters with user labels
RATE_LIMIT_BREACHES = Counter(
    'llm_rate_limit_breaches',
    'Rate limit breaches',
    ['user_id', 'model']
)
THROTTLING_INCIDENTS = Counter(
    'llm_throttling_incidents',
    'Throttling incidents'
)

TST_TOGGLE = Gauge(
    'llm_index_toggle',
    'Toggles between 0 and 1 every time index page is accessed'
)