# ml-performance-analyzer

Term project for coms6998 applied machine learning in the cloud

A performance analysis framework for pre-trained ML models in cloud environments

Run inference

## Setup

```
// Set up
git clone https://github.com/jessicayliang/ml-performance-analyzer.git
cd ml-performance-analyzer
python3 -m venv env
source env/bin/activate
pip install -r requirements.txt
python3 run.py

// Run inference
curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" \
    -d '{"prompt": "Explain how transformers work.", "max_tokens": 100, "user_id": "user_1"}'

// View metrics
curl "http://localhost:8000/metrics"

```

## Metrics Collected

### Garbage collection

`python_gc_objects_collected_total`: The total number of objects collected during garbage collection.
`python_gc_objects_uncollectable_total`: Number of uncollectable objects found during GC.
`python_gc_collections_total`: The number of times each generation was collected.
`process_virtual_memory_bytes`: Total virtual memory used by the process.

### Process

`process_resident_memory_bytes`: The amount of physical memory (RAM) used by the process.
`process_cpu_seconds_total`: Total CPU time spent in user and system mode.
`process_open_fds`: Number of open file descriptors.
`process_max_fds`: The maximum number of open file descriptors.

### Request Latency

`llm_request_latency_seconds`: Latency in processing requests.
`llm_time_to_first_token_seconds`: Time from request to the first token generation.

### Request and Token

`llm_request_count_total`: Total number of requests made.
`llm_tokens_generated_total`: Total number of tokens generated in response to requests.
`llm_tokens_input_total`: Total number of input tokens processed.
`llm_error_count_total`: Total number of failed requests.

### Resource Utilization

`llm_gpu_memory_usage_bytes`: GPU memory usage.
`llm_cpu_usage_percent`: CPU usage percentage.
`llm_ram_usage_bytes`: RAM usage.

### Token Length

`llm_token_length_input`: Distribution of input token lengths.
`llm_token_length_output`: Distribution of output token lengths.

### Queue and Rate Limit

`llm_queue_time_seconds`: Time spent in the queue before processing.
`llm_queue_size`: Current size of the request queue.
`llm_rate_limit_breaches_total`: Number of rate-limit breaches.
`llm_throttling_incidents_total`: Number of throttling incidents.
