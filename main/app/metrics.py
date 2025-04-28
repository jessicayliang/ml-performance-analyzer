from prometheus_client import Counter, Histogram, Gauge

REQUEST_LATENCY = Histogram('llm_request_latency_seconds', 'Time spent processing entire request',
                            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0])
TIME_TO_FIRST_TOKEN = Histogram('llm_time_to_first_token_seconds', 'Time to first token',
                                buckets=[0.05, 0.1, 0.2, 0.5, 1.0, 2.0, 5.0])
REQUEST_COUNT = Counter('llm_request_count', 'Total number of requests')
TOKENS_GENERATED = Counter('llm_tokens_generated_total', 'Total number of tokens generated')
TOKENS_INPUT = Counter('llm_tokens_input_total', 'Total number of input tokens processed')
ERROR_COUNT = Counter('llm_error_count', 'Total number of failed requests')
ERROR_TYPES = Counter('llm_error_types', 'Types of errors', ['error_type'])

TOKEN_LENGTH_INPUT = Histogram('llm_token_length_input', 'Input token lengths',
                               buckets=[10, 50, 100, 250, 500, 1000, 2000])
TOKEN_LENGTH_OUTPUT = Histogram('llm_token_length_output', 'Output token lengths',
                                buckets=[10, 50, 100, 250, 500, 1000, 2000])
GPU_MEMORY_USAGE = Gauge('llm_gpu_memory_usage_bytes', 'GPU memory usage in bytes')
CPU_USAGE_PERCENT = Gauge('llm_cpu_usage_percent', 'CPU usage percentage')
RAM_USAGE_BYTES = Gauge('llm_ram_usage_bytes', 'RAM usage in bytes')
QUEUE_TIME = Histogram('llm_queue_time_seconds', 'Time in queue',
                       buckets=[0.01, 0.05, 0.1, 0.5, 1.0, 5.0, 10.0])
QUEUE_SIZE = Gauge('llm_queue_size', 'Current request queue size')
RATE_LIMIT_BREACHES = Counter('llm_rate_limit_breaches', 'Rate limit breaches', ['user_id'])
THROTTLING_INCIDENTS = Counter('llm_throttling_incidents', 'Throttling incidents')

MODEL_TEMPERATURE = Histogram('llm_temperature_distribution', 'Distribution of temperature values used',
                              buckets=[0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0])
TOP_P_DISTRIBUTION = Histogram('llm_top_p_distribution', 'Distribution of top_p values used',
                               buckets=[0.1, 0.5, 0.8, 0.9, 0.95, 0.99, 1.0])
PROMPT_RESPONSE_RATIO = Histogram('llm_prompt_response_ratio', 'Ratio of prompt tokens to response tokens',
                                  buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0])

# Tokenization metrics
TOKENIZATION_TIME = Histogram('llm_tokenization_time_seconds', 'Time spent on tokenization',
                              buckets=[0.001, 0.005, 0.01, 0.05, 0.1, 0.5])

# Model loading and initialization
MODEL_LOAD_TIME = Gauge('llm_model_load_time_seconds', 'Time taken to load model into memory')
MODEL_INIT_TIME = Gauge('llm_model_init_time_seconds', 'Time taken to initialize model')

# Breaking down the inference pipeline
INFERENCE_COMPUTATION_TIME = Histogram('llm_inference_computation_time_seconds', 'Pure inference computation time',
                                       buckets=[0.05, 0.1, 0.5, 1.0, 5.0, 10.0])
TOKENS_PER_SECOND = Histogram('llm_tokens_per_second', 'Generation speed in tokens per second',
                              buckets=[1, 5, 10, 20, 50, 100])

# KV cache metrics
KV_CACHE_SIZE_BYTES = Gauge('llm_kv_cache_size_bytes', 'KV cache memory usage in bytes')
KV_CACHE_HIT_RATIO = Gauge('llm_kv_cache_hit_ratio', 'KV cache hit ratio')

# Batch processing metrics
BATCH_SIZE = Histogram('llm_batch_size', 'Batch sizes used for inference',
                       buckets=[1, 2, 4, 8, 16, 32, 64])
EFFECTIVE_BATCH_UTILIZATION = Gauge('llm_effective_batch_utilization', 'Percentage of batch capacity utilized')

# Additional GPU metrics
GPU_UTILIZATION_PERCENT = Gauge('llm_gpu_utilization_percent', 'GPU utilization percentage')
GPU_POWER_USAGE_WATTS = Gauge('llm_gpu_power_usage_watts', 'GPU power consumption in watts')
GPU_TEMPERATURE_CELSIUS = Gauge('llm_gpu_temperature_celsius', 'GPU temperature in Celsius')

# Network metrics
NETWORK_BYTES_SENT = Counter('llm_network_bytes_sent', 'Total bytes sent over network')
NETWORK_BYTES_RECEIVED = Counter('llm_network_bytes_received', 'Total bytes received over network')

# User metrics
UNIQUE_USERS = Gauge('llm_unique_users', 'Number of unique users in time window')
USER_SESSION_LENGTH = Histogram('llm_user_session_length', 'Length of user sessions in messages',
                                buckets=[1, 2, 5, 10, 20, 50, 100])
CONTEXT_LENGTH_UTILIZATION = Histogram('llm_context_length_utilization', 'Percentage of max context length used',
                                       buckets=[0.1, 0.25, 0.5, 0.75, 0.9, 0.95, 0.99])

# Business metrics
ESTIMATED_COST = Counter('llm_estimated_cost_dollars', 'Estimated cost of requests in dollars',
                         ['model_id', 'operation_type'])
TOKENS_PROCESSED_PER_DOLLAR = Gauge('llm_tokens_per_dollar', 'Tokens processed per dollar spent')
