from fastapi import FastAPI, Request
from pydantic import BaseModel
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
import torch
import os

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

# ---- Endpoint ----
@app.post("/generate")
async def generate_text(request: PromptRequest):
    sampling_params = SamplingParams(
        temperature=request.temperature,
        top_p=request.top_p,
        max_tokens=request.max_tokens,
    )
    outputs = llm.generate([request.prompt], sampling_params)
    response_text = outputs[0].outputs[0].text
    return {"output": response_text}

# ---- Optional: Health Check ----
@app.get("/")
def root():
    return {"status": "Model is ready"}
