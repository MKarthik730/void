"""
VOID Backend — Mistral Service
Loads Mistral-7B + Telugu LoRA and exposes run() helper
"""
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel
import os
from config import BASE_MODEL, ADAPTER_PATH

# ── 4-bit quantization config ─────────────────────────────────────────────────
bnb_config = BitsAndBytesConfig(
    load_in_4bit=True,
    bnb_4bit_compute_dtype=torch.float16,
    bnb_4bit_use_double_quant=True,
    bnb_4bit_quant_type="nf4",
)

# ── Load once at startup ──────────────────────────────────────────────────────
print("⏳ Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(BASE_MODEL, use_fast=False)
tokenizer.pad_token = tokenizer.eos_token

print("⏳ Loading Mistral-7B base model (CPU mode)...")
_model = AutoModelForCausalLM.from_pretrained(
    BASE_MODEL,
    device_map="cpu",           # force CPU — no GPU needed
    torch_dtype=torch.float32,  # float32 for CPU
    low_cpu_mem_usage=True,     # reduces RAM spike during load
)

print("⏳ Loading Telugu LoRA adapters...")
_model = PeftModel.from_pretrained(_model, os.path.abspath(ADAPTER_PATH))
_model.eval()
print("✅ Mistral + Telugu LoRA ready!")

DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def run(instruction: str, max_new_tokens: int = 200) -> str:
    prompt = f"### Instruction:\n{instruction}\n\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt")  # no .to("cuda")
    
    with torch.no_grad():
        outputs = _model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.3,
            repetition_penalty=1.2,
            eos_token_id=tokenizer.eos_token_id,
            do_sample=True,
        )
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return full_text.split("### Response:\n")[-1].strip()
