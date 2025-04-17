from fastapi import FastAPI, Request, Response
from prometheus_client import Counter, Gauge, generate_latest, CollectorRegistry
import random

# custom registry to avoid default tracked metrics
custom_registry = CollectorRegistry()

REQUESTS = Counter(
    'http_requests_total',
    'Total number of HTTP requests',
    ['label1', 'label2'],
    registry=custom_registry
)

RANDOM_GAUGE = Gauge(
    'random_value',
    'Randomly changing value',
    ['label3'],
    registry=custom_registry
)

app = FastAPI()

@app.get("/")
def index(request: Request):
    REQUESTS.labels(method=request.method, endpoint="/").inc()
    RANDOM_GAUGE.labels(endpoint="/").set(random.uniform(0, 100))
    return {"message": "Hello, world!"}

@app.get("/metrics")
def metrics():
    data = generate_latest(custom_registry)
    return Response(content=data, media_type="text/plain; version=0.0.4; charset=utf-8")
