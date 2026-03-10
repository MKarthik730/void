import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel
import os

os.environ["HF_HOME"] = "D:\\huggingface"
os.environ["HUGGINGFACE_HUB_CACHE"] = "D:\\huggingface\\hub"

adapter_path = os.path.abspath("LLM")
base_model_name = "mistralai/Mistral-7B-v0.1"

print("⏳ Loading base model (this takes a few minutes)...")
model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    dtype=torch.float16,        # fixed deprecation warning
    device_map="cpu",
    low_cpu_mem_usage=True,
    offload_state_dict=True,    # offloads to disk to save RAM
)

tokenizer = AutoTokenizer.from_pretrained(base_model_name, use_fast=False)
tokenizer.pad_token = tokenizer.eos_token

print("⏳ Loading LoRA adapters...")
model = PeftModel.from_pretrained(model, adapter_path)

print("⏳ Merging adapters into base model...")
model = model.merge_and_unload()

print("⏳ Saving merged model to D:\\LLM_merged ...")
model.save_pretrained("D:\\LLM_merged")
tokenizer.save_pretrained("D:\\LLM_merged")

print("✅ Done! Merged model saved to D:\\LLM_merged")