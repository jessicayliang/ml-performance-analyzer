import os
import time
import torch
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer
from app.metrics import (
    TOKENIZATION_TIME, MODEL_TEMPERATURE, TOP_P_DISTRIBUTION,
    INFERENCE_COMPUTATION_TIME, TOKENS_PER_SECOND,
    MODEL_INIT_TIME
)

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
HF_TOKEN = os.getenv("HF_TOKEN", None)  # only some gated models need HF_TOKEN

# Measure model load time
model_load_start = time.time()
tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
model_init_start = time.time()
llm = LLM(model=MODEL_ID, dtype=torch.float16)
model_init_end = time.time()

# Record metrics
MODEL_INIT_TIME.set(model_init_end - model_init_start)

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
llm = LLM(model=MODEL_ID, dtype=torch.float16)

def generate_text(messages: list[dict], max_tokens: int, temperature: float, top_p: float):
    # Record temperature and top_p settings
    if temperature is not None:
        MODEL_TEMPERATURE.observe(temperature)

    if top_p is not None:
        TOP_P_DISTRIBUTION.observe(top_p)

    # Tokenization time
    tokenize_start = time.time()

    # Format messages into a chat prompt
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )
    tokenize_end = time.time()
    TOKENIZATION_TIME.observe(tokenize_end - tokenize_start)

    # Prepare sampling params and call vLLM
    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )

    # Inference time
    inference_start = time.time()
    outputs = llm.generate([formatted_prompt], sampling_params)
    inference_end = time.time()

    # Decode the response
    generated_text = outputs[0].outputs[0].text
    input_tokens = tokenizer.encode(formatted_prompt)
    output_tokens = tokenizer.encode(generated_text)

    # Calculate metrics
    inference_time = inference_end - inference_start
    tokens_count = len(output_tokens)
    tokens_per_second = tokens_count / inference_time if inference_time > 0 else 0

    # Record metrics
    INFERENCE_COMPUTATION_TIME.observe(inference_time)
    TOKENS_PER_SECOND.observe(tokens_per_second)

    return generated_text, input_tokens, output_tokens
