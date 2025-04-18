import os
import torch
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B"
HF_TOKEN = os.getenv("HF_TOKEN", None)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
llm = LLM(model=MODEL_ID, dtype=torch.float16)

def generate_text(prompt: str, max_tokens: int, temperature: float, top_p: float):
    sampling_params = SamplingParams(temperature=temperature, top_p=top_p, max_tokens=max_tokens)
    outputs = llm.generate([prompt], sampling_params)
    return outputs[0].outputs[0].text, tokenizer.encode(prompt), tokenizer.encode(outputs[0].outputs[0].text)
