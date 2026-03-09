import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# --- Configuration ---
# Point this to your unzipped folder
adapter_path = "./telugu_model" 
# Use the exact base model you used during fine-tuning
base_model_name = "mistralai/Mistral-7B-v0.1" 

print("⏳ Loading model... This may take 2-5 minutes.")

# 1. Load the Tokenizer
tokenizer = AutoTokenizer.from_pretrained(adapter_path)

# 2. Load the Base Model in 4-bit (to save memory)
model = AutoModelForCausalLM.from_pretrained(
    base_model_name,
    load_in_4bit=True,
    device_map="auto",
    torch_dtype=torch.float16,
)

# 3. Load your Telugu Adapters
model = PeftModel.from_pretrained(model, adapter_path)
model.eval()

print("✅ Model Loaded Successfully!")

def ask_ai(question):
    # This matches the Alpaca format you used in training
    prompt = f"### Instruction:\n{question}\n\n### Response:\n"
    
    inputs = tokenizer(prompt, return_tensors="pt").to("cuda")
    
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=100,
            temperature=0.3, # Low temp = more factual
            repetition_penalty=1.2,
            eos_token_id=tokenizer.eos_token_id
        )
    
    # Extract only the response part
    full_text = tokenizer.decode(outputs[0], skip_special_tokens=True)
    response = full_text.split("### Response:\n")[-1].strip()
    return response

# --- Test Queries ---
test_questions = [
    "భారతదేశం గురించి ఒక వాక్యం చెప్పండి.",  # "Tell a sentence about India."
    "మీరు ఎవరు?",                            # "Who are you?"
    "సూర్యుడు ఏ దిక్కున ఉదయిస్తాడు?"         # "In which direction does the sun rise?"
]

for q in test_questions:
    print(f"\nUser: {q}")
    print(f"AI: {ask_ai(q)}")