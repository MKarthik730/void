import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

os.environ["HF_HOME"] = "D:\\huggingface"
os.environ["HUGGINGFACE_HUB_CACHE"] = "D:\\huggingface\\hub"

adapter_path = os.path.abspath('LLM')
base_model_name = "mistralai/Mistral-7B-v0.1"

print("⏳ Loading tokenizer...")
tokenizer = AutoTokenizer.from_pretrained(base_model_name, use_fast=False)
tokenizer.pad_token = tokenizer.eos_token

print("⏳ Loading base model (CPU mode — may take 5-10 mins)...")
model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    device_map="cpu",           # ← CPU only, no GPU needed
    torch_dtype=torch.float32,  # ← float32 for CPU
    low_cpu_mem_usage=True,     # ← reduces RAM spike
)

print("⏳ Loading Telugu LoRA adapters...")
model = PeftModel.from_pretrained(model, adapter_path)
model.eval()

print("✅ Model Loaded!")

def ask_ai(question):
    prompt = f"### Instruction:\n{question}\n\n### Response:\n"
    inputs = tokenizer(prompt, return_tensors="pt")  # ← no .to("cuda")
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,        # ← keep low for speed on CPU
            temperature=0.3,
            repetition_penalty=1.2,
            eos_token_id=tokenizer.eos_token_id,
            do_sample=True
        )
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return full_text.split("### Response:\n")[-1].strip()

test_questions = [
    "భారతదేశం గురించి ఒక వాక్యం చెప్పండి.",
    "మీరు ఎవరు?",
    "సూర్యుడు ఏ దిక్కున ఉదయిస్తాడు?"
]

for q in test_questions:
    print(f"\nUser: {q}")
    print(f"AI: {ask_ai(q)}")