import os
import torch
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

MAX_MODEL_LEN = 2048

MODELS = {
    "qwen": "Qwen/Qwen2.5-0.5B-Instruct",
    "llama": "suayptalha/FastLlama-3.2-1B-Instruct"
}

HF_TOKEN = os.getenv("HF_TOKEN", None)

# Initialize tokenizers
tokenizers = {
    "qwen": AutoTokenizer.from_pretrained(MODELS["qwen"], token=HF_TOKEN),
    "llama": AutoTokenizer.from_pretrained(MODELS["llama"], token=HF_TOKEN)
}

# Initialize vLLM engines
llms = {
    "qwen": LLM(model=MODELS["qwen"], dtype=torch.float16, gpu_memory_utilization=0.3, max_model_len=MAX_MODEL_LEN),
    "llama": LLM(model=MODELS["llama"], dtype=torch.float16, gpu_memory_utilization=0.6, max_model_len=MAX_MODEL_LEN)
}

def generate_text(
    messages: list[dict],
    max_tokens: int,
    temperature: float,
    top_p: float,
    model: str = "llama"  # default to Llama
):
    if model not in MODELS:
        raise ValueError(f"Model {model} is not supported. Choose from {list(MODELS.keys())}.")

    context_length = MAX_MODEL_LEN - max_tokens
    tokenizer = tokenizers[model]
    llm = llms[model]

    # Format messages into a chat prompt
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    tokenized_prompt = tokenizer(
        formatted_prompt,
        truncation=True,
        max_length=context_length,
        return_tensors="pt"
    )

    truncated_prompt = tokenizer.decode(
        tokenized_prompt.input_ids[0],
        skip_special_tokens=False
    )

    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
    outputs = llm.generate([truncated_prompt], sampling_params)

    generated_text = outputs[0].outputs[0].text
    return generated_text, tokenizer.encode(truncated_prompt), tokenizer.encode(generated_text)
