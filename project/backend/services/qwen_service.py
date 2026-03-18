"""
VOID Backend — LLM Service
Uses llama-cpp-python to run Qwen2.5-3B GGUF locally (CPU, no GPU needed)
Fast, lightweight, no transformers required
"""
from llama_cpp import Llama
import os
from config import QWEN_GGUF_PATH

# ── Load model once at startup ────────────────────────────────────────────────
print(f"⏳ Loading Qwen2.5-3B from {QWEN_GGUF_PATH} ...")
_llm = Llama(
    model_path=QWEN_GGUF_PATH,
    n_ctx=2048,
    n_threads=4,
    n_gpu_layers=0,
    verbose=False,
)
print("✅ Qwen2.5-3B ready!")

SYSTEM_PROMPT = (
    "You are VOID, a friendly AI assistant for Telugu users. "
    "Always reply in Tenglish — mix Telugu words written in English script "
    "with English naturally. Use casual words like bro, ra, rey, kada, ga, "
    "ani, undi, cheppu, nenu, ela, em, ayyo. Keep replies short and natural "
    "like WhatsApp messages. Don't be formal."
)


def run(instruction: str, max_new_tokens: int = 200) -> str:
    """Run Qwen2.5-3B via llama-cpp-python using ChatML format."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user",   "content": instruction},
    ]
    response = _llm.create_chat_completion(
        messages=messages,
        max_tokens=max_new_tokens,
        temperature=0.7,
        top_p=0.9,
        repeat_penalty=1.1,
        stop=["<|im_end|>", "<|endoftext|>"],
    )
    return response["choices"][0]["message"]["content"].strip()
