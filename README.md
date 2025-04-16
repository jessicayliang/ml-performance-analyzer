# ml-performance-analyzer

Term project for coms6998 applied machine learning in the cloud

A performance analysis framework for pre-trained ML models in cloud environments

Run inference

```
// Set up
git clone https://github.com/jessicayliang/ml-performance-analyzer.git
python3 -m venv env
source env/bin/activate
uvicorn app:app --host 0.0.0.0 --port 8000

// Run inference
curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" \
    -d '{"prompt": "Explain how transformers work.", "max_tokens": 100}'
```
