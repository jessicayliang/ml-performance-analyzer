import os
import torch
from vllm import LLM, SamplingParams
from transformers import AutoTokenizer

MODEL_ID = "Qwen/Qwen2.5-0.5B-Instruct"
HF_TOKEN = os.getenv("HF_TOKEN", None)  # only some gated models need HF_TOKEN

tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, token=HF_TOKEN)
llm = LLM(model=MODEL_ID, dtype=torch.float16)

def generate_text(messages: list[dict], max_tokens: int, temperature: float, top_p: float):
    # Format messages into a chat prompt
    formatted_prompt = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True
    )

    tokenized_prompt = tokenizer(
        formatted_prompt,
        truncation=True,
        return_tensors="pt"
    )

    truncated_prompt = tokenizer.decode(
        tokenized_prompt.input_ids[0],
        skip_special_tokens=False
    )

    # Prepare sampling params and call vLLM
    sampling_params = SamplingParams(
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens
    )
    outputs = llm.generate([truncated_prompt], sampling_params)

    # Decode the response
    generated_text = outputs[0].outputs[0].text
    return generated_text, tokenizer.encode(truncated_prompt), tokenizer.encode(generated_text)
